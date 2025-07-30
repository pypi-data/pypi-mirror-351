"""
Tests for custom exceptions.
"""

from kythera_kdx.exceptions import (
    KytheraError,
    KytheraAPIError,
    KytheraAuthError,
    KytheraConnectionError,
    KytheraTimeoutError
)


class TestExceptions:
    """Test cases for custom exceptions."""
    
    def test_base_exception(self):
        """Test the base KytheraError exception."""
        error = KytheraError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_api_error(self):
        """Test KytheraAPIError with additional attributes."""
        error = KytheraAPIError(
            "API Error", 
            status_code=400, 
            response_data={"error": "Bad request"}
        )
        assert str(error) == "API Error"
        assert error.status_code == 400
        assert error.response_data == {"error": "Bad request"}
        assert isinstance(error, KytheraError)
    
    def test_auth_error(self):
        """Test KytheraAuthError."""
        error = KytheraAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, KytheraError)
    
    def test_connection_error(self):
        """Test KytheraConnectionError."""
        error = KytheraConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, KytheraError)
    
    def test_timeout_error(self):
        """Test KytheraTimeoutError."""
        error = KytheraTimeoutError("Request timed out")
        assert str(error) == "Request timed out"
        assert isinstance(error, KytheraError)
