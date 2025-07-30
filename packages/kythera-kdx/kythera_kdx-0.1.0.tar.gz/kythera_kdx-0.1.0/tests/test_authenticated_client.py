"""
Tests for the AuthenticatedClient class.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from kythera_kdx.authenticated_client import AuthenticatedClient
from kythera_kdx.exceptions import KytheraAuthError


class TestAuthenticatedClient:
    """Test cases for AuthenticatedClient."""

    def test_init_with_parameters(self):
        """Test initialization with all parameters provided."""
        client = AuthenticatedClient(
            base_url="https://test.api.com",
            tenant_id="test-tenant",
            client_id="test-client-id",
            client_secret="test-secret",
            timeout=60
        )
        
        assert client.base_url == "https://test.api.com"
        assert client.tenant_id == "test-tenant"
        assert client.client_id == "test-client-id"
        assert client.client_secret == "test-secret"
        assert client.timeout == 60
        assert client.authority == "https://login.microsoftonline.com/test-tenant"

    def test_init_from_environment(self):
        """Test initialization from environment variables."""
        env_vars = {
            "KYTHERA_BASE_URL": "https://env.api.com",
            "AZURE_TENANT_ID": "env-tenant",
            "AZURE_CLIENT_ID": "env-client-id",
            "AZURE_CLIENT_SECRET": "env-secret",
            "KYTHERA_SCOPES": "custom-scope"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            client = AuthenticatedClient()
            
            assert client.base_url == "https://env.api.com"
            assert client.tenant_id == "env-tenant"
            assert client.client_id == "env-client-id"
            assert client.client_secret == "env-secret"
            assert client.scopes == ["custom-scope"]

    def test_init_defaults(self):
        """Test initialization with default values."""
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client"}, clear=False):
            client = AuthenticatedClient()
            
            assert client.base_url == "https://api.kythera.com"
            assert client.tenant_id == "common"
            assert client.client_id == "test-client"
            assert client.client_secret is None
            assert client.scopes == ["https://api.kythera.com/.default"]

    def test_init_missing_client_id(self):
        """Test that initialization fails without client_id."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KytheraAuthError, match="client_id is required"):
                AuthenticatedClient()

    @patch('kythera_kdx.authenticated_client.ConfidentialClientApplication')
    def test_initialize_confidential_app(self, mock_confidential_app):
        """Test initialization of confidential client application."""
        mock_app = Mock()
        mock_confidential_app.return_value = mock_app
        
        client = AuthenticatedClient(
            client_id="test-client",
            client_secret="test-secret"
        )
        
        mock_confidential_app.assert_called_once_with(
            client_id="test-client",
            client_credential="test-secret",
            authority="https://login.microsoftonline.com/common"
        )
        assert client._app == mock_app

    @patch('kythera_kdx.authenticated_client.PublicClientApplication')
    def test_initialize_public_app(self, mock_public_app):
        """Test initialization of public client application."""
        mock_app = Mock()
        mock_public_app.return_value = mock_app
        
        client = AuthenticatedClient(client_id="test-client")
        
        mock_public_app.assert_called_once_with(
            client_id="test-client",
            authority="https://login.microsoftonline.com/common"
        )
        assert client._app == mock_app

    def test_is_token_expired(self):
        """Test token expiration checking."""
        client = AuthenticatedClient(client_id="test-client")
        
        # No token set - should be expired
        assert client._is_token_expired() == True
        
        # Set token with future expiration
        import time
        client._token_expires_at = time.time() + 3600  # 1 hour from now
        assert client._is_token_expired() == False
        
        # Set token with past expiration
        client._token_expires_at = time.time() - 3600  # 1 hour ago
        assert client._is_token_expired() == True

    def test_token_info(self):
        """Test get_token_info method."""
        # Test with service principal (has client_secret)
        client = AuthenticatedClient(
            client_id="test-client",
            client_secret="test-secret"
        )
        
        token_info = client.get_token_info()
        assert token_info["has_token"] == False
        assert token_info["is_expired"] == True
        assert token_info["auth_type"] == "service_principal"
        
        # Test with device flow (no client_secret)
        client2 = AuthenticatedClient(client_id="test-client")
        token_info2 = client2.get_token_info()
        assert token_info2["auth_type"] == "device_flow"

    def test_clear_token_cache(self):
        """Test clearing token cache."""
        client = AuthenticatedClient(client_id="test-client")
        
        # Set some token data
        client._cached_token = "test-token"
        client._token_expires_at = 12345
        
        # Clear cache
        client.clear_token_cache()
        
        assert client._cached_token is None
        assert client._token_expires_at is None

    def test_context_manager(self):
        """Test context manager functionality."""
        with patch('kythera_kdx.authenticated_client.PublicClientApplication'):
            client = AuthenticatedClient(client_id="test-client")
            
            # Mock the close method to verify it's called
            client.close = Mock()
            
            with client as ctx_client:
                assert ctx_client is client
            
            # Verify close was called
            client.close.assert_called_once()


# Integration test (requires actual Azure AD setup)
def test_service_principal_integration():
    """
    Integration test for service principal authentication.
    
    This test requires actual Azure AD credentials and should only be run
    when those are available in the environment.
    """
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    
    if not all([client_id, client_secret, tenant_id]):
        pytest.skip("Azure AD credentials not available")
    
    try:
        client = AuthenticatedClient(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id
        )
        
        # Test token acquisition
        token_info = client.get_token_info()
        assert token_info["auth_type"] == "service_principal"
        
        # This would trigger actual token acquisition
        # token = client._get_access_token()
        # assert token is not None
        
    except Exception as e:
        pytest.fail(f"Service principal authentication failed: {e}")


if __name__ == "__main__":
    # Run basic tests
    test_client = TestAuthenticatedClient()
    test_client.test_init_with_parameters()
    test_client.test_init_defaults()
    test_client.test_is_token_expired()
    test_client.test_token_info()
    test_client.test_clear_token_cache()
    
    print("All basic tests passed!")
    print("Run with pytest for complete test suite.")
