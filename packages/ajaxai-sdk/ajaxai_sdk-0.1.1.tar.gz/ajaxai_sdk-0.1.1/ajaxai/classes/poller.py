from dataclasses import dataclass, field
import logging
import time
from typing import List, Optional, Callable, TYPE_CHECKING, Set

from ..completed_job_processor import CompletedJobProcessor
from ..types import COMPLETED_JOB_STATES, JobState
from .exceptions import AjaxAiApiError, AjaxAiAuthorizationError, AjaxAiRateLimitError

if TYPE_CHECKING:
    from ..client import AjaxAiClient

logger = logging.getLogger(__name__)


@dataclass
class Poller:
    """
    Client-side job poller for the SDK.
    Polls the backend to check status of user's jobs and triggers callbacks.
    """
    client: "AjaxAiClient"
    polling_interval: int = 60 * 5  # 5 minutes
    running: bool = False
    max_retries: int = 3
    retry_backoff: float = 2.0
    error_callback: Optional[Callable[[Exception, dict], None]] = None
    # Track jobs we've already tried to process to avoid infinite loops
    _processed_jobs: Set[str] = field(default_factory=set)
    # Track failed job processing attempts
    _failed_processing_attempts: dict = field(default_factory=dict)
    max_processing_attempts: int = 3

    def start(self) -> bool:
        """Start the background polling thread"""
        try:
            logger.info("Starting poller")
            self.running = True
            # Reset tracking sets when starting fresh
            self._processed_jobs.clear()
            self._failed_processing_attempts.clear()
            
            while self.running:
                self._check_active_jobs()
                time.sleep(self.polling_interval)
            return True
        except Exception as e:
            self._handle_error(e, {"memo": "Unexpected error starting poller"})
            return False
        
    def stop(self) -> bool:
        """Stop the background polling thread"""
        try:
            self.running = False
            return True
        except Exception as e:
            self._handle_error(e, {"memo": "Unexpected error stopping poller"})
            return False
    
    def _check_active_jobs(self) -> Optional[List[JobState]]:
        """Check status of all active jobs"""
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                if not self.running:
                    logger.warning("Poller not running. Stopping.")
                    self.stop()
                    return None
                
                active_job_states: List[JobState] = self.client.get_job_states()

                if not active_job_states:
                    logger.info("No active jobs to poll. Stopping poller.")
                    self.stop()
                    return None
                
                logger.info(f"Found {len(active_job_states)} active jobs to poll.")
                self._process_job_states(active_job_states)
                return active_job_states
                
            except (AjaxAiAuthorizationError, AjaxAiRateLimitError) as e:
                # Don't retry auth errors, but do retry rate limits
                if isinstance(e, AjaxAiAuthorizationError):
                    self._handle_error(e, {"memo": "Authentication failed", "fatal": True})
                    self.stop()
                    return None
                else:  # Rate limit
                    wait_time = self.retry_backoff ** retry_count
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry {retry_count + 1}/{self.max_retries}")
                    time.sleep(wait_time)
                    retry_count += 1
                    
            except AjaxAiApiError as e:
                # Network/API errors - retry with backoff
                if retry_count >= self.max_retries:
                    self._handle_error(e, {"memo": "Max retries exceeded for API error", "fatal": True})
                    return None
                
                wait_time = self.retry_backoff ** retry_count
                logger.warning(f"API error, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
                retry_count += 1
                
            except Exception as e:
                # Unexpected errors - don't retry, stop poller
                self._handle_error(e, {"memo": "Unexpected error checking active jobs", "fatal": True})
                self.stop()
                return None
        
        # If we get here, all retries failed
        self._handle_error(Exception("All retries failed"), {"memo": "Max retries exceeded", "fatal": True})
        return None
    
    def check_single_job(self, job_id: str) -> Optional[JobState]:
        """Check one job's status."""
        try:
            job_state: JobState = self.client.get_job_state(job_id)
            
            if job_state.state in COMPLETED_JOB_STATES:
                self._process_completed_job(job_id)
            
            return job_state
        
        except AjaxAiApiError as e:
            self._handle_error(e, {"memo": "API error checking job state", "job_id": job_id})
            return None
        except Exception as e:
            self._handle_error(e, {"memo": "Unexpected error checking job state", "job_id": job_id})
            return None
    
    def _process_job_states(self, job_states: List[JobState]):
        """Process job updates and call callbacks if needed."""
        logger.info(f"Status update: {len(job_states)} Active Jobs - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for job_state in job_states:
            job_id = job_state.job_id
            
            try:
                if job_state.state in COMPLETED_JOB_STATES:
                    # Check if we've already successfully processed this job
                    if job_id in self._processed_jobs:
                        logger.debug(f"Job {job_id} already processed successfully, skipping")
                        continue
                    
                    # Check if we've exceeded max processing attempts for this job
                    attempts = self._failed_processing_attempts.get(job_id, 0)
                    if attempts >= self.max_processing_attempts:
                        logger.warning(f"Job {job_id} exceeded max processing attempts ({attempts}), marking as processed to avoid infinite loop")
                        self._processed_jobs.add(job_id)
                        continue
                    
                    logger.info(f"Processing completed job: {job_id} with state: {job_state.state} (attempt {attempts + 1})")
                    
                    # Try to process the completed job
                    success = self._process_completed_job(job_id)
                    
                    if success:
                        # Mark as successfully processed
                        self._processed_jobs.add(job_id)
                        # Remove from failed attempts tracking
                        self._failed_processing_attempts.pop(job_id, None)
                        logger.info(f"Successfully processed completed job: {job_id}")
                    else:
                        # Increment failed attempts
                        self._failed_processing_attempts[job_id] = attempts + 1
                        logger.warning(f"Failed to process job {job_id}, attempt {attempts + 1}/{self.max_processing_attempts}")
                        
                else:
                    logger.info(f"Continuing to wait for active job: {job_id} with state: {job_state.state}")
                    
            except Exception as e:
                # Don't let one job failure stop processing others
                job_id = getattr(job_state, 'job_id', 'unknown')
                self._handle_error(e, {
                    "memo": "Error processing individual job state", 
                    "job_id": job_id,
                    "non_fatal": True
                })

    def _process_completed_job(self, job_id: str) -> bool:
        """
        Process a completed job
        Returns True if processing succeeded, False if it failed
        """
        try:
            CompletedJobProcessor(self.client, job_id).process_completed_job()
            return True
        except Exception as e:
            self._handle_error(e, {
                "memo": "Error processing completed job", 
                "job_id": job_id,
                "non_fatal": True
            })
            return False

    def _handle_error(self, error: Exception, context: dict):
        """Handle errors with logging and optional user callback"""
        # Always log the error
        if context.get("fatal"):
            logger.error(f"Fatal poller error: {error}", extra=context, exc_info=True)
        elif context.get("non_fatal"):
            logger.warning(f"Non-fatal poller error: {error}", extra=context)
        else:
            logger.error(f"Poller error: {error}", extra=context, exc_info=True)
        
        # Call user's error callback if provided
        if self.error_callback:
            try:
                self.error_callback(error, context)
            except Exception as callback_error:
                logger.error(f"Error in user error callback: {callback_error}")
        
        # Stop poller for fatal errors
        if context.get("fatal"):
            self.stop()
            