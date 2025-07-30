import requests


class AjaxAiApiError(requests.HTTPError):
    """Base exception for AjaxAI API errors."""
    def __init__(self, message, status_code=None, response_data=None, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.status_code = status_code
        self.response_data = response_data


class AjaxAiJobNotFoundError(AjaxAiApiError):
    """Raised when a job is not found (404)."""
    pass


class AjaxAiAuthorizationError(AjaxAiApiError):
    """Raised for authorization errors (401, 403)."""
    pass


class AjaxAiRateLimitError(AjaxAiApiError):
     """Raised for rate limiting errors (429)."""
     pass


class AjaxAiServerError(AjaxAiApiError):
     """Raised for server-side errors (5xx)."""
     pass