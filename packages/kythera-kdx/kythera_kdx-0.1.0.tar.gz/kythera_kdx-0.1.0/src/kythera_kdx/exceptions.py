"""
Custom exceptions for the Kythera KDX package.
"""

from typing import Optional, List, Dict, Any


class KytheraError(Exception):
    """Base exception class for all Kythera-related errors."""
    pass


class KytheraAPIError(KytheraError):
    """Exception raised when the Kythera API returns an error response."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class KytheraAuthError(KytheraError):
    """Exception raised when authentication with the Kythera API fails."""
    pass


class KytheraConnectionError(KytheraError):
    """Exception raised when connection to the Kythera API fails."""
    pass


class KytheraTimeoutError(KytheraError):
    """Exception raised when a request to the Kythera API times out."""
    pass


class KytheraValidationError(KytheraError):
    """Exception raised when request/response validation fails."""
    
    def __init__(self, message: str, validation_errors: Optional[List[str]] = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []
