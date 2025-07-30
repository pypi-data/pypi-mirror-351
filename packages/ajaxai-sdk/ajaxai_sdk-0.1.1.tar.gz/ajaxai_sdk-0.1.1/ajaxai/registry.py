# sdk/ajaxai/registry.py
import logging
from typing import Dict, Callable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .batch_job import AjaxAiBatchJob


logger = logging.getLogger(__name__)


CALLBACK_REGISTRY: Dict[str, Callable[["AjaxAiBatchJob"], None]] = {}

def ajaxai_callback(job_type: str):
    """
    Decorator to register a function as a callback handler for a specific job type.

    When a function is decorated with @ajaxai_callback('my_job_type'),
    it gets added to the internal CALLBACK_REGISTRY when the module
    containing the function is imported.

    Args:
        job_type: The string identifier for the job type this function handles.

    Example:
        ```python
        from sdk.src.ajaxai.registry import ajaxai_callback
        from sdk.src.ajaxai.batch_job import AjaxAiBatchJob

        @ajaxai_callback('content_generation')
        def handle_content_generation(job: AjaxAiBatchJob):
            print(f"Handling completed content generation job: {job.job_id}")
            # ... processing logic ...
        ```
    """
    if not isinstance(job_type, str) or not job_type:
        raise TypeError("job_type provided to @ajaxai_callback must be a non-empty string.")

    def decorator(func: Callable[["AjaxAiBatchJob"], None]):
        """The actual decorator function."""
        if not callable(func):
            raise TypeError(f"Object decorated with @ajaxai_callback for job_type '{job_type}' must be callable.")

        if job_type in CALLBACK_REGISTRY:
            # Warn if overwriting, might indicate duplicate job types or definitions
            logger.warning(
                f"Overwriting callback for job_type '{job_type}'. "
                f"Previous: {CALLBACK_REGISTRY[job_type].__name__}, New: {func.__name__}"
            )

        # --- Registration Step ---
        # Add the decorated function to the registry dictionary.
        CALLBACK_REGISTRY[job_type] = func
        logger.debug(f"Registered callback '{func.__name__}' for job_type '{job_type}'.")

        # Return the original function unmodified.
        # This allows the function to be called normally if needed,
        # although typically callbacks are only called by the dispatcher.
        return func
    return decorator

def get_callback(job_type: str) -> Optional[Callable[["AjaxAiBatchJob"], None]]:
    """
    Retrieves a callback function from the registry for a given job type.

    Args:
        job_type: The job type string.

    Returns:
        The registered callable function, or None if no callback is registered
        for the given job type.
    """
    return CALLBACK_REGISTRY.get(job_type)
