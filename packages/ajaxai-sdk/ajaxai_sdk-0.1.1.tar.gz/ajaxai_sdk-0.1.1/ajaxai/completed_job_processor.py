from dataclasses import dataclass
import logging
from typing import Callable

from .batch_job import AjaxAiBatchJob
from .client import AjaxAiClient
from .registry import CALLBACK_REGISTRY
from .types import JobDict, JobStateOptions


logger = logging.getLogger(__name__)


def default_callback(job: AjaxAiBatchJob) -> None:
    """
    Default callback function for a completed job.
    """
    logger.info(
        f"Completed job {job.job_id} with state {job.state}"
        f"You're seeing this because you didn't provide a custom callback function for your job."
        f"Job type: {job.job_type}"
        f"Job metadata: {job.job_metadata}"
    )
    return None


@dataclass
class CompletedJobProcessor:
    """
    Processes completed jobs from the Poller and converts results into pydantic models.
    """
    client: AjaxAiClient
    job_id: str

    def process_completed_job(self) -> None:
        """
        Processes a completed job, retrieving its results and converting them to pydantic models.
        
        Args:
            callback: Function to call with the processed results
        """
        try:
            job_data: JobDict = self.client.retrieve_job(self.job_id)
            job: AjaxAiBatchJob = AjaxAiBatchJob.from_dict(job_data, self.client)

            handler: Callable = self._get_handler(job.state)
            handler(job)
            self.client.deactivate_job(self.job_id)
            
        except Exception as e:
            raise e
    
    def _get_handler(self, job_state: str) -> Callable[[AjaxAiBatchJob], None]:
        """
        Retrieves the appropriate handler function for a given job state using pattern matching.

        Args:
            job_state: The state of the completed job.

        Returns:
            The callable handler function for that state.

        Raises:
            ValueError: If the job_state is not one of the expected
                        completed states (SUCCESS, FAILED, ERROR).
        """
        try:
            match job_state:
                case JobStateOptions.SUCCESS.value | JobStateOptions.SUCCEEDED.value:
                    return self._handle_success
                case JobStateOptions.FAILED.value:
                    return self._handle_failure
                case JobStateOptions.ERROR.value:
                    raise ValueError(f"Job {self.job_id} had an error.")
                case _:
                    logger.error(f"Received unexpected job state '{job_state}' in CompletedJobProcessor.")
                    raise ValueError(
                        f"CompletedJobProcessor cannot handle job state '{job_state}'. "
                        f"Expected SUCCESS, FAILED, or ERROR."
                    )
        except Exception as e:
            raise ValueError(f"Unexpected error getting handler for job state: {e}")
    
    def _handle_success(self, job: AjaxAiBatchJob) -> None:
        """
        Handles a successful job.
        """
        logger.info(f"{job.__repr__} completed successfully.")
        
        try:
            try:
                callback_function = CALLBACK_REGISTRY.get(job.job_type)
                if callback_function is None:
                    callback_function = default_callback
                
                if not callable(callback_function):
                    raise TypeError(f"Callback for job type '{job.job_type}' is not callable")
                
                try:
                    callback_function(job)
                except Exception as e:
                    error_message = f"Error executing callback for job type '{job.job_type}': {e}"
                    logger.error(error_message, exc_info=True)
                    raise RuntimeError(error_message) from e
                    
            except (KeyError, TypeError) as e:
                raise ValueError(f"Unexpected error executing callback for job type: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error handling successful job: {e}")

    def _handle_failure(self, job: AjaxAiBatchJob) -> None:
        """
        Handles a failed job.
        """
        logger.error(f"{job.__repr__} failed.")

    def _handle_job_with_error(self, job: AjaxAiBatchJob) -> None:
        """
        Handles a job that had an error.
        """
        logger.error(f"{job.__repr__} had an error.")
