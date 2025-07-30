# sdk/ajaxai/request.py
from dataclasses import dataclass
import json
import logging
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel


logger = logging.getLogger(__name__)

class DefaultTextOutput(BaseModel):
    """Default output model for simple text responses"""
    text: str


@dataclass
class AjaxAiRequestItem:
    """A request to be processed by Gemini in a batch job"""
    request_id: str
    content_parts: Optional[List[Dict[str, Any]]] = None
    request_metadata: BaseModel | None = None
    request_metadata_model: Type[BaseModel] | None = None
    output_model: Type[BaseModel] | None = DefaultTextOutput
    status: str = "draft"
    job_id: str = None

    def __post_init__(self):
        if self.request_metadata is not None and not isinstance(self.request_metadata, BaseModel):
            raise TypeError(f"Request metadata must be an instance of a Pydantic BaseModel, but got {type(self.request_metadata)}")
        # Automatically set request_metadata_model type if not provided explicitly
        if self.request_metadata_model is None:
             self.request_metadata_model = type(self.request_metadata)
        if self.content_parts is None:
            self.content_parts = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AjaxAiRequestItem":
        """Create a request item from a dictionary"""
        request_metadata_model: Type[BaseModel] = None
        if data["request_metadata_model"]:
            request_metadata_model = data["request_metadata_model"]

        if request_metadata_model and data["request_metadata_dict"]:
            request_metadata = request_metadata_model.model_validate(data["request_metadata_dict"])
        else:
            request_metadata = data["request_metadata_dict"]

        return cls(
            request_id=data["request_id"],
            content_parts=data["content_parts"],
            request_metadata=request_metadata,
            request_metadata_model=request_metadata_model,
            output_model=data["output_model"],
            status=data["status"],
            job_id=data["job_id"]
        )
    
    @classmethod
    def from_json(cls, json_data: str) -> "AjaxAiRequestItem":
        """Create a request item from a JSON string"""
        return cls.from_dict(json.loads(json_data))
    
    def add_text(self, text: str):
        """Add text content to the request"""
        self.content_parts.append({"type": "text", "content": text})
        return self
    
    def add_image(self, image):
        """Add image content to the request (URL, file path, bytes, or GCS URI)"""
        self.content_parts.append({"type": "image", "content": image})
        return self
    
    def add_video(self, video):
        """Add video content to the request (URL, file path, or GCS URI)"""
        self.content_parts.append({"type": "video", "content": video})
        return self
    
    def add_document(self, document):
        """Add document content to the request (URL, file path, or GCS URI)"""
        self.content_parts.append({"type": "document", "content": document})
        return self
    
    def add_request_metadata(self, request_metadata: BaseModel):
        """Add metadata for tracking or analysis"""
        if not isinstance(request_metadata, BaseModel):
            raise TypeError(f"Request metadata must be an instance of a Pydantic BaseModel, but got {type(request_metadata)}")
        self.request_metadata = request_metadata
        return self

    def serialize_request(self):
        """Serialize the request to a dictionary"""
        
        return {
            "request_id": self.request_id,
            "content_parts": self.content_parts,
            "request_metadata_dict": self.request_metadata.model_dump() if self.request_metadata else {},
            "request_metadata_schema": self._get_request_metadata_schema_str(),
            "output_schema": self._get_output_schema_str(),
            "status": self.status,
            "job_id": self.job_id
        }
    
    def _get_output_schema_str(self) -> Optional[str]:
        """Get the output schema as a JSON string"""
        if self.output_model and issubclass(self.output_model, BaseModel): # and self.output_model is not DefaultTextOutput:
            try:
                schema_dict = self.output_model.model_json_schema()
                output_schema_str = json.dumps(schema_dict)
                logger.debug(f"Generated schema for request {self.request_id} (Model: {self.output_model.__name__})")
                return output_schema_str
            except Exception as e:
                # Log error but allow request to proceed without schema (will default to text)
                logger.error(f"Failed to generate JSON schema for request {self.request_id}, model {self.output_model.__name__}: {e}. Request will default to text output.", exc_info=True)
                return None # Ensure it's None on error
        else:
            return None

    def _get_request_metadata_schema_str(self) -> Optional[str]:
        """Get the request metadata schema as a JSON string"""
        if self.request_metadata_model and issubclass(self.request_metadata_model, BaseModel): # and self.request_metadata_model is not DefaultTextOutput:
            try:
                schema_dict = self.request_metadata_model.model_json_schema()
                request_metadata_schema_str = json.dumps(schema_dict)
                logger.debug(f"Generated schema for request {self.request_id} (Model: {self.request_metadata_model.__name__})")
                return request_metadata_schema_str
            except Exception as e:
                logger.error(f"Failed to generate JSON schema for request {self.request_id}, model {self.request_metadata_model.__name__}: {e}. Request will default to text output.", exc_info=True)
                return None # Ensure it's None on error
        else:
            return None
