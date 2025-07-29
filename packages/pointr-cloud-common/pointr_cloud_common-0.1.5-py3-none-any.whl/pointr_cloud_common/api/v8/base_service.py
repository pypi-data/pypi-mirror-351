import logging
from typing import Dict, Any, Optional

class V8ApiError(Exception):
    """Exception raised for V8 API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class BaseApiService:
    """Base class for V8 API services."""

    def __init__(self, api_service):
        """Initialize the service."""
        self.api_service = api_service
        self.logger = logging.getLogger(self.__class__.__name__)

    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the V8 API."""
        return self.api_service._make_request(method, endpoint, payload)
