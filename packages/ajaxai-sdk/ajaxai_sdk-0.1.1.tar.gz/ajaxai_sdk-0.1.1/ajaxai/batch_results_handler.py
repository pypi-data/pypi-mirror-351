import logging
from .types import BatchRequestResult, BatchRequestResultDict, RequestData, RequestSummary, UsageData


logger = logging.getLogger(__name__)


class BatchResultsHandler:
    """
    Handles batches of results from a streaming endpoint, converting them to pydantic models.
    """
    
    def __init__(self, client, job_id: str):
        """
        Initialize the handler.
        
        Args:
            client: The API client
            job_id: ID of the job
        """
        self.client = client
        self.job_id = job_id
    
    def process_result(self, result: BatchRequestResultDict) -> BatchRequestResult:
        """
        Process a single result into a pydantic model.
        
        Args:
            batch: Raw batch from the streaming API
            
        Returns:
            List of BatchRequestResult objects
        """
        
        try:
            # Extract needed components
            request_dict = result.get("request", {})
            response_dict = result.get("response")
            metadata_dict = result.get("metadata")
            summary_dict = result.get("summary")
            usage_dict = result.get("usage")
            
            # Convert dictionaries to models
            request = RequestData.model_validate(request_dict) if request_dict else None
            summary = RequestSummary.model_validate(summary_dict) if summary_dict else None
            usage = UsageData.model_validate(usage_dict) if usage_dict else None
                
            # Create BatchRequestResult
            batch_result = BatchRequestResult(
                request=request,
                response=response_dict,
                metadata=metadata_dict,
                summary=summary,
                usage=usage
            )
            return batch_result
            
        except Exception as e:
            logger.error(f"Error processing result: {str(e)}", exc_info=True)
            # Skip this result and continue
            return None
    