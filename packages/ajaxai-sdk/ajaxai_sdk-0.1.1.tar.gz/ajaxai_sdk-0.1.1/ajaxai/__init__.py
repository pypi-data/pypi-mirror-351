# sdk/ajaxai/__init__.py
import os
from .batch_job import AjaxAiBatchJob
from .request import AjaxAiRequestItem, DefaultTextOutput
from .client import AjaxAiClient
from .classes.exceptions import (
    AjaxAiApiError,
    AjaxAiAuthorizationError, 
    AjaxAiRateLimitError,
    AjaxAiServerError,
    AjaxAiJobNotFoundError
)
from .registry import ajaxai_callback

__version__ = "0.1.1"

def create_batch_job(job_type: str, api_key: str | None = None, **kwargs) -> AjaxAiBatchJob:
    """
    Create a new batch job. job_type is mandatory.
    """
    if not job_type: # Explicit check, though type hinting helps
        raise ValueError("job_type must be a non-empty string.")

    if api_key is None:
        api_key = os.environ.get("AJAXAI_API_KEY")
    
    if api_key is None:
        raise ValueError("AJAXAI_API_KEY not provided or found in environment variables.")

    client = AjaxAiClient(api_key=api_key)
    job = AjaxAiBatchJob(client=client, job_type=job_type, **kwargs)
    create_response = job.create() 
    
    if not create_response.get("success"):
        error_msg = getattr(create_response, 'error', 'Unknown error during job creation in API')
        raise AjaxAiApiError(f"Failed to create job in backend: {error_msg}")

    return job

def get_batch_job(api_key: str, job_id: str) -> AjaxAiBatchJob:
    """Retrieve an existing batch job"""
    client = AjaxAiClient(api_key=api_key)
    job_data = client.retrieve_job(job_id)
    return AjaxAiBatchJob.from_dict(job_data, client)

__all__ = [
    'create_batch_job',
    'get_batch_job', 
    'AjaxAiBatchJob',
    'AjaxAiRequestItem',
    'AjaxAiClient',
    'AjaxAiApiError',
    'AjaxAiAuthorizationError',
    'AjaxAiRateLimitError',
    'AjaxAiServerError',
    'AjaxAiJobNotFoundError',
    'ajaxai_callback',
    'DefaultTextOutput'
]
