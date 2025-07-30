"""
Tests for utility functions.
"""

import pytest
import os
from unittest.mock import patch
from kythera_kdx.utils import get_api_key_from_env, validate_api_key, format_endpoint


class TestUtils:
    """Test cases for utility functions."""
    
    @patch.dict(os.environ, {"KYTHERA_API_KEY": "test-key"})
    def test_get_api_key_from_env_found(self):
        """Test getting API key from environment when it exists."""
        api_key = get_api_key_from_env()
        assert api_key == "test-key"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_from_env_not_found(self):
        """Test getting API key from environment when it doesn't exist."""
        api_key = get_api_key_from_env()
        assert api_key is None
    
    def test_validate_api_key_valid(self):
        """Test API key validation with valid keys."""
        assert validate_api_key("valid-api-key") is True
        assert validate_api_key("another-key-123") is True
    
    def test_validate_api_key_invalid(self):
        """Test API key validation with invalid keys."""
        assert validate_api_key("") is False
        assert validate_api_key("   ") is False
        assert validate_api_key(None) is False
        assert validate_api_key(123) is False
    
    def test_format_endpoint(self):
        """Test endpoint formatting."""
        assert format_endpoint("users") == "/users"
        assert format_endpoint("/users") == "/users"
        assert format_endpoint("api/v1/users") == "/api/v1/users"
        assert format_endpoint("/api/v1/users") == "/api/v1/users"
        assert format_endpoint("") == "/"
        assert format_endpoint("   users   ") == "/users"
