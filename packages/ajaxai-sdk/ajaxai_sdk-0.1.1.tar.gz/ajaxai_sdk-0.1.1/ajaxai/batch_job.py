# sdk/ajaxai/batch_job.py
import datetime
import json
import logging
import threading
from dydantic import create_model_from_schema
import shortuuid
from dataclasses import dataclass, field
from typing import Generator, List, Optional, Type
from pydantic import BaseModel

from .classes.exceptions import AjaxAiApiError
from .batch_results_handler import BatchResultsHandler
from .types import DEFAULT_VERTEX_MODEL, AddRequestResponse, BatchRequestResult, BatchRequestResultDict, CreateJobResponse, JobDict, JobPerformanceMetrics, JobStateOptions, RequestDataList, RequestStateOptions, SaveJobResponse, SubmitJobResponse
from .request import AjaxAiRequestItem
from .client import AjaxAiClient


logger = logging.getLogger(__name__)


@dataclass
class AjaxAiBatchJob:
    """A batch job containing multiple requests to be processed by Gemini"""
    client: AjaxAiClient
    job_type: str

    job_id: str = field(default_factory=lambda: shortuuid.uuid())
    user_id: str = ""

    model: str = DEFAULT_VERTEX_MODEL
    system_instruction: str = ""
    temperature: float = 0.5
    max_output_tokens: int = 1024
    top_k: int = 40
    top_p: float = 0.95

    display_name: str = ""
    job_metadata: Optional[BaseModel] = None
    job_metadata_schema: Optional[Type[BaseModel]] = None
    callback_url: str = ""
    max_batch_size: int = 20

    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    started_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    completed_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    archived_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    state: str = JobStateOptions.CREATED.value
    state_message: str = ""
    performance_metrics: JobPerformanceMetrics = field(default_factory=JobPerformanceMetrics)

    request_queue: List[AjaxAiRequestItem] = field(default_factory=list)
    _flush_timer: Optional[threading.Timer] = None

    last_auto_flush_error: Optional[Exception] = None

    def __post_init__(self):
        self.user_id = self.client.user_id
        if self.job_metadata:
            if not isinstance(self.job_metadata_schema, type) or not issubclass(self.job_metadata_schema, BaseModel):
                 self.job_metadata_schema = type(self.job_metadata)
        else:
            self.job_metadata_schema = None

    def to_dict(self) -> JobDict:
        """Convert the batch job to a dictionary"""
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "job_type": self.job_type,
            "model": self.model,
            "system_instruction": self.system_instruction,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "top_k": self.top_k,
            "top_p": self.top_p,

            "display_name": self.display_name,
            "job_metadata": self.job_metadata.model_dump() if self.job_metadata else {},
            "job_metadata_schema": self.job_metadata_schema.model_json_schema() if self.job_metadata_schema else {},
            "callback_url": self.callback_url,
            "max_batch_size": self.max_batch_size,

            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "archived_at": self.archived_at,

            "state": self.state,
            "state_message": self.state_message,
            "request_queue": [req.serialize_request() for req in self.request_queue],
        }
    
    @classmethod
    def from_json(cls, json_data: str, client: AjaxAiClient) -> "AjaxAiBatchJob":
        """Create a batch job from a JSON string"""
        return cls.from_dict(json.loads(json_data), client)
    
    @classmethod
    def from_dict(cls, data: JobDict, client: AjaxAiClient) -> "AjaxAiBatchJob":
        """Create a batch job from a dictionary"""
        try:
            job = cls(
                client=client,
                
                job_id=data["job_id"],
                user_id=data["user_id"],
                job_type=data["job_type"],
                
                model=data["model"],
                system_instruction=data["system_instruction"],
                temperature=data["temperature"],
                max_output_tokens=data["max_output_tokens"],
                top_k=data["top_k"],
                top_p=data["top_p"],
                
                display_name=data["display_name"],
                callback_url=data["callback_url"],
                max_batch_size=data["max_batch_size"],
                
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                started_at=data["started_at"],
                completed_at=data["completed_at"],
                archived_at=data["archived_at"],
                state=data["state"],
                state_message=data["state_message"],
            )
            if data["job_metadata_schema"] and data["job_metadata"]:
                job.job_metadata_schema = create_model_from_schema(data["job_metadata_schema"])
                job.job_metadata = job.job_metadata_schema.model_validate(data["job_metadata"])
            else:
                job.job_metadata = None
                job.job_metadata_schema = None

            job.request_queue = [AjaxAiRequestItem.from_dict(req) for req in data["request_queue"]]
            return job
        except KeyError as e:
            raise ValueError(f"Missing required field in job data: {e}") from e
        except TypeError as e:
            raise ValueError(f"Invalid data type in job data: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to create batch job from data: {e}") from e

    # JOB METHODS
    def create(self) -> CreateJobResponse:
        """Create a new batch job"""
        try:
            job_data: JobDict = self.to_dict()
            response: CreateJobResponse = self.client.create_job(job_data)
            return response
        except Exception as e:
            return CreateJobResponse(
                job_id=self.job_id,
                success=False,
                error=str(e)
            )
    
    def save(self) -> SaveJobResponse:
        """Complete the batch job and mark it as ready for processing."""
        try:
            if self.request_queue:
                logger.info(f"Job {self.job_id}: Processing {len(self.request_queue)} requests before saving.")
                self._process_request_queue(is_explicit_save_or_submit=True)
        except Exception as e:
            logger.error(f"SDK Error: Failed to process request queue during explicit save for job {self.job_id}: {e}", exc_info=True)
            return SaveJobResponse(
                job_id=self.job_id,
                success=False,
                error=f"Failed to send queued requests: {str(e)}"
            )
        
        try:
            response: SaveJobResponse = self.client.save_job(self.job_id)
            return response
        except Exception as e:
            return SaveJobResponse(
                job_id=self.job_id,
                success=False,
                error=str(e)
            )

    def submit(self) -> SubmitJobResponse:
        """Submit the batch job for processing by Gemini."""
        try:
            if self.request_queue:
                logger.info(f"Job {self.job_id}: Processing {len(self.request_queue)} requests before submitting.")
                self._process_request_queue(is_explicit_save_or_submit=True)
        except Exception as e:
            logger.error(f"SDK Error: Failed to process request queue during explicit submit for job {self.job_id}: {e}", exc_info=True)
            return SubmitJobResponse(
                job_id=self.job_id,
                success=False,
                error=f"Failed to send queued requests: {str(e)}"
            )

        try:
            # Ensure the job is saved first
            if self.state != JobStateOptions.READY.value:
                save_response = self.save()
                if not save_response.success:
                    return SubmitJobResponse(
                        job_id=self.job_id,
                        success=False,
                        error=f"Failed to save job before submitting: {save_response.error}"
                    )
                
            # Start processing the job
            result = self.client.submit_job(self.job_id)
            return result
        except Exception as e:
            logger.error(f"SDK Error: Failed to submit job {self.job_id}: {e}", exc_info=True)
            return SubmitJobResponse(
                job_id=self.job_id,
                success=False,
                error=str(e)
            )
    

    # REQUEST METHODS
    def add_request(self, request: AjaxAiRequestItem) -> AddRequestResponse:
        """Add a request to this batch job"""
        try:
            # If we're adding requests, job is now populating (whether it was created or even ready before)
            self.state = JobStateOptions.POPULATING.value

            # Associate request with this job
            request.job_id = self.job_id
            
            # Add to internal queue
            self.request_queue.append(request)

            self.last_auto_flush_error = None
            
            # Start flush timer if not already running
            if not self._flush_timer:
                self._start_flush_timer()
            
            # If queue full, process batch
            if len(self.request_queue) >= self.max_batch_size:
                self._process_request_queue(is_explicit_save_or_submit=True)
                
            return AddRequestResponse(
                request_id=request.request_id,
                success=True
            )
        except Exception as e:
            return AddRequestResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )
    
    # MONITORING METHODS
    def get_state(self) -> str:
        """Get the current state of this job"""
        job_state = self.client.get_job_state(self.job_id)
        # update local state
        self.state = job_state.state
        return self.state
    
    def get_request_state(self, request_id) -> str:
        """Get the state of a specific request"""
        state: RequestStateOptions = self.client.get_request_state(self.job_id, request_id)
        return state.value
    
    # RESULTS METHODS
    def get_results(self) -> Generator[BatchRequestResult, None, None]:
        try:
            """Get the results of the job, yielding each result individually"""
            batch_generator: Generator[BatchRequestResultDict, None, None] = self.client.get_job_results_stream(self.job_id)
            result_handler = BatchResultsHandler(self.client, self.job_id)
            
            # Process each batch and yield individual results
            for batch in batch_generator:
                for result in batch.get("batch", []):
                    if result == "error" or not isinstance(result, dict):
                        continue
                    processed_result = result_handler.process_result(result)
                    if processed_result:  # Only yield if we got a valid result
                        yield processed_result
        except Exception as e:
            raise AjaxAiApiError(f"Failed to get results for job {self.job_id}: {e}") from e
    
    def get_metrics(self) -> JobPerformanceMetrics:
        """Get the summary of the job results"""
        return self.client.get_job_metrics(self.job_id)
    
    # HELPER METHODS
    def _process_request_queue(self, is_explicit_save_or_submit: bool = False):
        """Process the current request queue and send to API, including output schema."""
        if not self.request_queue:
            return

        payload = RequestDataList(requests=[req_item.serialize_request() for req_item in self.request_queue])
        try:
            self.client.add_requests(self.job_id, payload)
            # Clear queue on successful API submission
            self.request_queue = []
            # Cancel timer if it's running and queue is now empty
            if self._flush_timer:
                self._flush_timer.cancel()
                self._flush_timer = None
        except Exception as api_err:
            logger.error(f"Failed to add requests batch to API for job {self.job_id}: {api_err}", exc_info=True)
            
            if is_explicit_save_or_submit:
                # For explicit operations, propagate the error
                raise api_err
            else:
                # For timer-based operations, store the error
                self.last_auto_flush_error = api_err

    def _start_flush_timer(self):
        """Start a timer to flush the queue after a delay"""
        self._flush_timer = threading.Timer(5.0, self._timer_flush)
        self._flush_timer.daemon = True
        self._flush_timer.start()
    
    def _timer_flush(self):
        """Called when the timer expires"""
        try:
            self._process_request_queue(is_explicit_save_or_submit=False)
        except Exception as e:
            # Unexpected error in timer flush logic
            self.last_auto_flush_error = e
            logger.error(f"Unexpected error during timer flush for job {self.job_id}: {e}", exc_info=True)
        finally:
            # Restart timer if queue still has items and no error occurred
            if self.request_queue and not self.last_auto_flush_error:
                self._start_flush_timer()
            else:
                self._flush_timer = None

    def close(self):
        """Clean up resources, particularly active timers"""
        if self._flush_timer and self._flush_timer.is_alive():
            self._flush_timer.cancel()
        self._flush_timer = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure resources are cleaned up when exiting a context manager"""
        self.close()
        