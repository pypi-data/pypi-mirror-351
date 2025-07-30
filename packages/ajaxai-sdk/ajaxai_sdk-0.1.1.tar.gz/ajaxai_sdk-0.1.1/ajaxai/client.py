# sdk/ajaxai/client.py
"""
Provides the main client class for interacting with the AjaxAI API.

This module defines the AjaxAiClient, exceptions for API interactions,
and supporting data structures for managing batch prediction jobs with Gemini.
"""

import logging
from dataclasses import dataclass
import json
import os
from typing import Generator, List, Optional
import requests

from .classes.exceptions import AjaxAiApiError, AjaxAiJobNotFoundError, AjaxAiAuthorizationError, AjaxAiRateLimitError, AjaxAiServerError
from .types import AJAXAI_API_URL, AddRequestsResponse, BatchRequestResultDict, CreateJobResponse, JobDict, JobPerformanceMetrics, JobState, RequestDataList, SaveJobResponse, SubmitJobResponse, RequestStateResponse, JobStateOptions


logger = logging.getLogger(__name__)

@dataclass
class AjaxAiClient:
    """Client for interacting with the AjaxAI API"""
    api_key: str = None
    user_id: str = None
    base_url: str = AJAXAI_API_URL
    session: requests.Session = requests.Session()
    api_version: str = "v1"
    api_router: str = f"{base_url}/api/{api_version}"
    _poller = None

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("AJAXAI_API_KEY")

    @property
    def poller(self):
        if self._poller is None:
            from .classes.poller import Poller
            self._poller = Poller(client=self)
        return self._poller
    
    def _get_headers(self):
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        return headers
    
    def _handle_response(self, response: requests.Response):
        """Checks response status and raises appropriate custom exceptions."""
        status_code = response.status_code
        try:
            response_data = response.json()
            if isinstance(response_data, dict):
                detail = response_data.get("detail", response.text)
            else:
                detail = response.text
        except json.JSONDecodeError:
             response_data = None
             detail = response.text

        message = f"API Error {status_code}: {detail}"

        if status_code == 404:
             raise AjaxAiJobNotFoundError(message, status_code=status_code, response_data=response_data, response=response)
        elif status_code == 401 or status_code == 403:
             raise AjaxAiAuthorizationError(message, status_code=status_code, response_data=response_data, response=response)
        elif status_code == 429:
             raise AjaxAiRateLimitError(message, status_code=status_code, response_data=response_data, response=response)
        elif status_code >= 500:
             raise AjaxAiServerError(message, status_code=status_code, response_data=response_data, response=response)
        elif status_code >= 400: # Catch other 4xx errors
             raise AjaxAiApiError(message, status_code=status_code, response_data=response_data, response=response)
        
    # JOB METHODS
    def create_job(self, job_data: JobDict) -> CreateJobResponse:
        """Create a new batch job"""
        url = f"{self.api_router}/jobs/create"
        try:
            response = self.session.post(url, headers=self._get_headers(), json=job_data)
            self._handle_response(response) # Check for errors
            return response.json()
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error creating job: {e}", response=getattr(e, 'response', None)) from e

    def save_job(self, job_id) -> SaveJobResponse:
        """Mark a job as ready for processing"""
        url = f"{self.api_router}/jobs/{job_id}/save"
        try:
            response = self.session.post(url, headers=self._get_headers())
            self._handle_response(response)
            return SaveJobResponse.from_dict(response.json())
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error saving job {job_id}: {e}", response=getattr(e, 'response', None)) from e
    
    def submit_job(self, job_id) -> SubmitJobResponse:
        """Submit a job for processing"""
        url = f"{self.api_router}/jobs/{job_id}/submit"
        try:
            response = self.session.post(url, headers=self._get_headers())
            self._handle_response(response)
            return response.json() # Assuming API returns JSON matching SubmitJobResponse
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error submitting job {job_id}: {e}", response=getattr(e, 'response', None)) from e

    def retrieve_job(self, job_id) -> Optional[JobDict]:
        """Get info about a batch job"""
        url = f"{self.api_router}/jobs/{job_id}"
        try:
            response = self.session.get(url, headers=self._get_headers())
            self._handle_response(response)
            return response.json() # Return raw dict matching BatchJobInfo
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error retrieving job {job_id}: {e}", response=getattr(e, 'response', None)) from e
    
    def deactivate_job(self, job_id: str) -> bool:
        """Deactivate a job"""
        url = f"{self.api_router}/jobs/{job_id}/deactivate"
        try:
            response = self.session.post(url, headers=self._get_headers())
            self._handle_response(response)
            return True
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error deactivating job {job_id}: {e}", response=getattr(e, 'response', None)) from e
        
    # REQUEST METHODS
    def add_requests(self, job_id: str, requests_data: RequestDataList) -> AddRequestsResponse:
        """
        Add a batch of requests to a job.
        """
        url = f"{self.api_router}/jobs/{job_id}/requests"
        try:
            response = self.session.post(url, headers=self._get_headers(), json=requests_data)
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
             raise AjaxAiApiError(f"Network error adding requests to job {job_id}: {e}", response=getattr(e, 'response', None)) from e
        except Exception as e:
             raise AjaxAiApiError(f"Error preparing or sending requests for job {job_id}: {str(e)}", response=None) from e

    # MONITORING METHODS
    def start_polling(self):
        """Start polling for job state updates"""
        logger.info("Starting polling")
        self.poller.start()

    def stop_polling(self):
        """Stop polling for job state updates"""
        self.poller.stop()

    def get_job_state(self, job_id) -> JobState:
        """Get the state of a job"""
        url = f"{self.api_router}/jobs/{job_id}/state"
        try:
            response = self.session.get(url, headers=self._get_headers())
            self._handle_response(response)
            data = response.json()
            return JobState(state=data["state"], job_id=data["job_id"])
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error getting job state {job_id}: {e}", response=getattr(e, 'response', None)) from e
        except (ValueError, KeyError) as e: # Handle parsing errors
            raise AjaxAiApiError(f"Failed to parse job state response for {job_id}: {e}") from e

    def get_job_states(self) -> List[JobState]:
        """Get the state of all jobs"""
        url = f"{self.api_router}/jobs/states/all"
        try:
            response = self.session.get(url, headers=self._get_headers())
            logger.info(f"Job states response: {response.json()}")
            self._handle_response(response)
            return [JobState(state=data["state"], job_id=data["job_id"]) for data in response.json()]
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error getting job states: {e}", response=getattr(e, 'response', None)) from e

    def update_job_state(self, job_id, new_state) -> bool:
        """Update the state of a job"""
        url = f"{self.api_router}/jobs/{job_id}/update-state"

        if new_state not in [state.value.lower() for state in JobStateOptions]:
            raise ValueError(f"Invalid job state: {new_state}")
        
        try:
            response = self.session.post(url, headers=self._get_headers(), params={"new_state": new_state})
            self._handle_response(response)
            return True
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error updating job state {job_id}: {e}", response=getattr(e, 'response', None)) from e
    
    def get_request_state(self, job_id, request_id) -> RequestStateResponse:
        """Get the state of a specific request"""
        url = f"{self.api_router}/jobs/{job_id}/requests/{request_id}/state"
        try:
            response = self.session.get(url, headers=self._get_headers())
            self._handle_response(response)
            data = response.json()
            return RequestStateResponse(**data) # If RequestStateResponse is Pydantic
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error getting request state {job_id}/{request_id}: {e}", response=getattr(e, 'response', None)) from e
        
    # --- Get Errors Method ---
    def get_job_errors(self, job_id) -> dict: # Return raw dict matching JobErrorSummaryResponse
         """Retrieves error summary for a job."""
         url = f"{self.api_router}/jobs/{job_id}/errors"
         try:
             response = self.session.get(url, headers=self._get_headers())
             self._handle_response(response)
             # API returns JobErrorSummaryResponse structure
             return response.json()
         except requests.RequestException as e:
             raise AjaxAiApiError(f"Network error getting errors for job {job_id}: {e}", response=getattr(e, 'response', None)) from e

    # --- Get Results Method ---
    def get_job_results_stream(
            self, 
            job_id: str, 
            batch_size: int = 1000, 
            max_batch_bytes: int = 1_000_000
        ) -> Generator[BatchRequestResultDict, None, None]:
        """Stream the results of a job"""
        url = f"{self.api_router}/jobs/{job_id}/results/stream"
        params = {
            "batch_size": batch_size,
            "max_batch_bytes": max_batch_bytes
        }
        
        try:
            with self.session.get(
                url, 
                headers=self._get_headers(), 
                params=params, 
                stream=True
            ) as response:
                self._handle_response(response)
                for line in response.iter_lines():
                    if line:
                        decoded_line: str = line.decode('utf-8')
                        yield json.loads(decoded_line)


        except requests.RequestException as e:
            raise AjaxAiApiError(
                f"Network error streaming results for job {job_id}: {e}", 
                response=getattr(e, 'response', None)
            ) from e
    
    def get_job_metrics(self, job_id: str) -> JobPerformanceMetrics:
        """Get the metrics of the job results"""
        url = f"{self.api_router}/jobs/{job_id}/results/metrics"
        try:
            response = self.session.get(url, headers=self._get_headers())
            self._handle_response(response)
            return response.json()
        except requests.RequestException as e:
            raise AjaxAiApiError(f"Network error getting job result summary {job_id}: {e}", response=getattr(e, 'response', None)) from e
