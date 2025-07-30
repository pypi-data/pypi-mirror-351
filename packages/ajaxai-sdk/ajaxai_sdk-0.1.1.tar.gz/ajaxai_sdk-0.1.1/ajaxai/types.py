# sdk/ajaxai/types.py
from dataclasses import dataclass
import datetime
from enum import Enum
import json
import os
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from pydantic import BaseModel, field_validator


class VertexModels(Enum):
    GEMINI_2_0_FLASH = "gemini-2.0-flash-001"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite-001"
    #GEMINI_1_5_FLASH_002 = "gemini-1.5-flash-002"
    #GEMINI_1_5_PRO_002 = "gemini-1.5-pro-002"
    #CLAUDE_3_7_SONNET = "claude-3.7-sonnet"
    #CLAUDE_3_5_HAIKU = "claude-3.5-haiku"
    #CLAUDE_3_5_SONNET_V2 = "claude-3.5-sonnet-v2"

DEFAULT_VERTEX_MODEL = VertexModels.GEMINI_2_0_FLASH.value

AJAXAI_API_URL = os.environ.get("AJAXAI_API_URL", "https://api.ajaxai.co")


class JobStateOptions(Enum):
    # initial states
    CREATED = "created" # job created, no requests added yet
    POPULATING = "populating" # job created, requests added, not ready for submission
    READY = "ready" # job created, requests added, ready for submission
    # processing states
    UNSPECIFIED = "unspecified" # job state not set
    QUEUED = "queued" # job created, requests added, not ready for submission
    PENDING = "pending" # job created, requests added, not ready for submission
    RUNNING = "running" # job created, requests added, running
    SUBMITTED = "submitted" # job created, requests added, not ready for submission
    PROCESSING = "processing" # job submitted to Gemini, processing
    # completed states
    COMPLETED = "completed" # job completed, results available  DEPRECATED
    SUCCESS = "success" # job completed, results available  DEPRECATED
    SUCCEEDED = "succeeded" # job completed, results available
    FAILED = "failed" # job failed
    CANCELLING = "cancelling" # job cancelled, cancelling
    CANCELLED = "cancelled" # job cancelled
    PAUSED = "paused" # job paused
    EXPIRED = "expired" # job expired
    UPDATING = "updating" # job updating
    PARTIALLY_SUCCEEDED = "partially_succeeded" # job partially succeeded
    # error states
    ERROR = "error" # job creation failed
    # post-analysis states
    IN_POST_ANALYSIS = "in_post_analysis" # job completed, results available, post-analysis in progress


COMPLETED_JOB_STATES: List[str] = [
    JobStateOptions.COMPLETED.value, # job completed, results available  DEPRECATED
    JobStateOptions.SUCCESS.value, # job completed, results available  DEPRECATED
    JobStateOptions.SUCCEEDED.value, # job completed, results available
    JobStateOptions.FAILED.value, 
    JobStateOptions.CANCELLED.value,
    JobStateOptions.PAUSED.value,
    JobStateOptions.EXPIRED.value,
    JobStateOptions.ERROR.value,
    JobStateOptions.IN_POST_ANALYSIS.value
]

PRE_SUBMISSION_JOB_STATES: List[str] = [
    JobStateOptions.POPULATING.value,
    JobStateOptions.READY.value
]

POLLABLE_JOB_STATES: List[str] = [
    JobStateOptions.SUBMITTED.value, 
    JobStateOptions.PROCESSING.value, 
    JobStateOptions.RUNNING.value,
    JobStateOptions.CANCELLING.value,
    JobStateOptions.UPDATING.value,
    JobStateOptions.PARTIALLY_SUCCEEDED.value,
    JobStateOptions.UNSPECIFIED.value,
    JobStateOptions.QUEUED.value,
    JobStateOptions.PENDING.value,
]

FAILED_JOB_STATES: List[str] = [
    JobStateOptions.FAILED.value,
    JobStateOptions.CANCELLED.value,
    JobStateOptions.PAUSED.value,
    JobStateOptions.EXPIRED.value,
    JobStateOptions.ERROR.value,
]

ACTIVE_JOB_STATES: List[str] = PRE_SUBMISSION_JOB_STATES + POLLABLE_JOB_STATES

class RequestStateOptions(Enum):
    PENDING = "pending" # request added, not yet processed
    PROCESSING = "processing" # request being processed
    SUCCESS = "success" # request completed, results available
    COMPLETED = "completed" # request completed, results available  DEPRECATED
    PARTIAL = "partial" # request completed, results available, but not all requests completed
    FAILED = "failed" # request failed
    ERROR = "error" # request failed

RequestStatusType = Literal[tuple(e.value for e in RequestStateOptions)]  # type: ignore

COMPLETED_REQUEST_STATES: List[RequestStateOptions] = [
    RequestStateOptions.SUCCESS.value,
    RequestStateOptions.COMPLETED.value,  # DEPRECATED
    RequestStateOptions.FAILED.value,
    RequestStateOptions.ERROR.value
]


class RequestDataDict(TypedDict):
    request_id: str
    content_parts: List[Dict[str, Any]]
    request_metadata: Dict[str, Any]
    request_metadata_schema: Optional[str] 
    output_model: Optional[BaseModel]
    output_schema: Optional[str] 


class RequestDataList(TypedDict):
    requests: List[RequestDataDict]


class CreateJobResponse(TypedDict):
    """Response from creating a batch job"""
    job_id: str
    state: str  # JobStateOptions value strings
    success: bool
    error: Union[str, None]  # Empty string or None when no error


class ActiveJobStatesDict(TypedDict):
    """Dictionary of active job states"""
    job_id: str
    state: str


class ActiveJobStatesListDict(TypedDict):
    """List of active job states"""
    jobs: List[ActiveJobStatesDict]


@dataclass
class SaveJobResponse:
    """Response from saving a batch job"""
    job_id: str
    success: bool
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SaveJobResponse":
        return cls(
            job_id=data["job_id"],
            success=data["success"],
            error=data["error"]
        )
    
    @classmethod
    def from_json(cls, json_data: str) -> "SaveJobResponse":
        return cls.from_dict(json.loads(json_data))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "success": self.success,
            "error": self.error
        }


@dataclass
class SubmitJobResponse:
    """Response from submitting a batch job"""
    job_id: str
    success: bool
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubmitJobResponse":
        return cls(
            job_id=data["job_id"],
            success=data["success"],
            error=data["error"]
        )

    @classmethod
    def from_json(cls, json_data: str) -> "SubmitJobResponse":
        return cls.from_dict(json.loads(json_data))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "success": self.success,
            "error": self.error
        }


@dataclass
class AddRequestResponse:
    """Response from adding a request to a batch job"""
    request_id: str
    success: bool
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AddRequestResponse":
        return cls(
            request_id=data["request_id"],
            success=data["success"],
            error=data["error"]
        )

    @classmethod
    def from_json(cls, json_data: str) -> "AddRequestResponse":
        return cls.from_dict(json.loads(json_data))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "success": self.success,
            "error": self.error
        }

@dataclass
class JobStateResponse:
    """Response from getting the state of a batch job"""
    state: str
    job_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobStateResponse":
        return cls(
            state=data["state"],
            job_id=data["job_id"]
        )

    @classmethod
    def from_json(cls, json_data: str) -> "JobStateResponse":
        return cls.from_dict(json.loads(json_data))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "job_id": self.job_id
        }


class AddRequestsResponseItem(TypedDict):
    """Response from adding a request to a batch job"""
    request_id: str
    success: bool
    error: Optional[str]


class AddRequestsResponse(TypedDict):
    """Response from adding a request to a batch job"""
    results: List[AddRequestsResponseItem]


class UsageData(BaseModel):
    """Usage data for a request"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class RequestData(BaseModel):
    """Data for a request"""
    content_parts: List[Dict[str, Any]]
    output_model: Optional[BaseModel]


class RequestSummary(BaseModel):
    """Summary for a request"""
    request_id: str
    model_name: Optional[str]
    status: Optional[RequestStatusType]  # type: ignore
    finish_reason: Optional[str]
    error_message: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class BatchRequestResult(BaseModel):
    """A request result from a batch job"""
    request: RequestData
    response: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    summary: Optional[RequestSummary]
    usage: Optional[UsageData]


class RequestDataDict(TypedDict):
    """A request data from a batch job"""
    content_parts: List[Dict[str, Any]]
    output_model: Optional[Dict[str, Any]]


class RequestSummaryDict(TypedDict):
    """A request summary from a batch job"""
    request_id: str
    model_name: Optional[str]
    status: RequestStateOptions
    finish_reason: Optional[str]
    error_message: Optional[str]


class UsageDataDict(TypedDict):
    """A usage data from a batch job"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class BatchRequestResultDict(TypedDict):
    """A request result from a batch job"""
    request: RequestDataDict
    response: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    summary: Optional[RequestSummaryDict]
    usage: Optional[UsageDataDict]
    metadata_schema: Optional[Dict[str, Any]]
    output_schema: Optional[Dict[str, Any]]


class JobPerformanceMetrics(BaseModel):
    """Performance metrics for a batch job"""
    total_requests: Optional[int] = None
    processed_requests: Optional[int] = None
    successful_requests: Optional[int] = None
    failed_requests: Optional[int] = None
    duration_seconds: Optional[float] = None
    total_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    created_at: Optional[str] = None

class JobPerformanceMetricsDict(TypedDict):
    """Performance metrics for a batch job"""
    total_requests: Optional[int]
    processed_requests: Optional[int]
    successful_requests: Optional[int]
    failed_requests: Optional[int]
    duration_seconds: Optional[float]
    total_tokens: Optional[int]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    created_at: Optional[str]


class JobState(BaseModel):
    """A job state"""
    state: str
    job_id: str
    user_id: Optional[str] = None
    client_id: Optional[str] = None


class JobStatus(BaseModel):
    """A job status"""
    state: str
    job_id: str
    user_id: Optional[str] = None
    display_name: Optional[str] = None
    job_type: Optional[str] = None
    model: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    request_count: Optional[int] = None
    error: Optional[str] = None
    completed_count: Optional[int] = None
    failed_count: Optional[int] = None
    

    @field_validator("state")
    def validate_state(cls, v) -> str:
        if isinstance(v, str):
            state_str = v.lower()
        elif hasattr(v, 'value') and isinstance(v.value, str):
            state_str = v.value.lower()
        elif isinstance(v, dict) and 'value' in v and isinstance(v['value'], str):
            state_str = v['value'].lower()
        else:
            raise ValueError(f"Cannot extract state from: {v}")
        
        valid_values = [e.value.lower() for e in JobStateOptions]
        if state_str not in valid_values:
            raise ValueError(f"Invalid state: {v}")

        return v.lower() if isinstance(v, str) else state_str



class RequestStateResponse(BaseModel):
    request_id: str
    job_id: str
    state: str
    request_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime.datetime] = None # Use datetime
    updated_at: Optional[datetime.datetime] = None # Use datetime



class JobDict(TypedDict):
    """Data for a batch job"""
    job_id: str
    user_id: str
    job_type: Union[str, None]

    model: str
    system_instruction: str
    temperature: float
    max_output_tokens: int
    top_k: int
    top_p: float

    display_name: str
    job_metadata: Dict[str, Any]
    job_metadata_schema: Optional[Dict[str, Any]]
    callback_url: str
    max_batch_size: int

    created_at: Union[str, None]
    updated_at: Union[str, None]
    started_at: Union[str, None]
    completed_at: Union[str, None]
    archived_at: Union[str, None]

    state: str
    state_message: Optional[str]
    request_queue: List[RequestData]
