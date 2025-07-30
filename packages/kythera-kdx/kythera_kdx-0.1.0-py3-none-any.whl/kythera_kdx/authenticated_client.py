"""
Authenticated client class for interacting with the Kythera API using MSAL authentication.

This module provides a unified client that combines authentication and API request capabilities,
supporting both confidential client (service principal) and public client (device flow) authentication.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urljoin
import httpx
from msal import ConfidentialClientApplication, PublicClientApplication
from msal_extensions import (
    PersistedTokenCache,
    FilePersistence,
    build_encrypted_persistence,
)

from .exceptions import (
    KytheraAPIError,
    KytheraAuthError,
    KytheraConnectionError,
    KytheraTimeoutError,
)

logger = logging.getLogger(__name__)


def _get_default_cache_location() -> str:
    """Get the default cache location based on the operating system."""
    if os.name == "nt":  # Windows
        cache_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "kythera-kdx")
    else:  # Unix-like systems
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "kythera-kdx")
    
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "token_cache.bin")


class AuthenticatedClient:
    """
    Authenticated client for interacting with the Kythera API.

    This class provides unified authentication and API request capabilities,
    supporting both service principal authentication (with client_secret) and
    interactive device flow authentication (without client_secret).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
        scopes: Optional[List[str]] = None,
        cache_location: Optional[str] = None,
    ):
        """
        Initialize the authenticated Kythera client.

        Args:
            base_url: The base URL for the Kythera API
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret (for service principal auth)
            timeout: Request timeout in seconds
            scopes: List of OAuth scopes to request
            cache_location: Custom location for token cache (optional)
        """
        # Load configuration from environment if not provided
        self.base_url = (
            base_url or os.getenv("KYTHERA_BASE_URL", "https://kdx-api.app.lgcy.com.br")
        ).rstrip("/")
        self.tenant_id = tenant_id or os.getenv(
            "KYTHERA_TENANT_ID", "497a1564-7d5b-48d3-a55e-791eaeef5819"
        )
        self.client_id = client_id or os.getenv(
            "KYTHERA_CLIENT_ID", "ffac81db-8b9f-4747-8a3e-526e1e9c9d68"
        )
        self.client_secret = client_secret or os.getenv("KYTHERA_CLIENT_SECRET")
        self.timeout = timeout
        self.scopes = scopes or [
            os.getenv("KYTHERA_SCOPES", f"{self.client_id}/.default")
        ]

        # Validate required configuration
        if not self.client_id:
            raise KytheraAuthError(
                "client_id is required. Provide it as parameter or set AZURE_CLIENT_ID environment variable."
            )        # Build authority URL
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"

        # Set up token cache
        self.cache_location = cache_location or _get_default_cache_location()
        self._token_cache = self._create_token_cache()

        # Authentication state
        self._cached_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._app: Optional[
            Union[ConfidentialClientApplication, PublicClientApplication]
        ] = None

        # Initialize HTTP client
        self.session = httpx.Client(timeout=self.timeout)
        self.session.headers.update({"Content-Type": "application/json"})        # Initialize MSAL application
        self._initialize_app()

    def _create_token_cache(self) -> PersistedTokenCache:
        """Create a persisted token cache."""
        try:
            # Try to use encrypted persistence if available
            persistence = build_encrypted_persistence(self.cache_location)
        except Exception as e:
            logger.warning(f"Failed to create encrypted persistence, falling back to file: {e}")
            # Fall back to file persistence
            persistence = FilePersistence(self.cache_location)
        
        return PersistedTokenCache(persistence)    
    
    def _initialize_app(self) -> None:
        """Initialize the MSAL application (confidential or public client)."""
        try:
            if self.client_secret:
                # Confidential client application (service principal)
                self._app = ConfidentialClientApplication(
                    client_id=self.client_id,
                    client_credential=self.client_secret,
                    authority=self.authority,
                    token_cache=self._token_cache,
                )
                logger.info(
                    "Initialized MSAL ConfidentialClientApplication for service principal with token cache"
                )
            else:
                # Public client application (device flow)
                self._app = PublicClientApplication(
                    client_id=self.client_id,
                    authority=self.authority,
                    token_cache=self._token_cache,
                )
                logger.info("Initialized MSAL PublicClientApplication for device flow with token cache")
        except Exception as e:
            raise KytheraAuthError(f"Failed to initialize MSAL application: {e}")

    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or will expire soon."""
        if not self._token_expires_at:
            return True

        # Add 5 minute buffer before expiration
        buffer_seconds = 300
        return time.time() >= (self._token_expires_at - buffer_seconds)

    def _acquire_token_for_service_principal(self, force_refresh: bool = False) -> str:
        """Acquire token using client credentials flow (service principal)."""
        if not force_refresh and not self._is_token_expired() and self._cached_token:
            return self._cached_token

        if not self._app or not isinstance(self._app, ConfidentialClientApplication):
            raise KytheraAuthError(
                "Expected ConfidentialClientApplication for service principal flow"
            )

        try:
            result = self._app.acquire_token_for_client(scopes=self.scopes)

            if result and "access_token" in result:
                access_token = result["access_token"]
                if not access_token:
                    raise KytheraAuthError("Received empty access token")

                self._cached_token = access_token
                # MSAL returns expires_in (seconds from now)
                expires_in = result.get("expires_in", 3600)
                if isinstance(expires_in, (int, float)):
                    self._token_expires_at = time.time() + expires_in
                else:
                    self._token_expires_at = time.time() + 3600  # Default 1 hour
                logger.info(
                    "Successfully acquired access token using service principal"
                )
                return self._cached_token  # type: ignore[return-value]
            else:
                error_msg = "Unknown error"
                if result and isinstance(result, dict):
                    error_msg = result.get(
                        "error_description", result.get("error", "Unknown error")
                    )
                raise KytheraAuthError(f"Failed to acquire token: {error_msg}")

        except Exception as e:
            raise KytheraAuthError(f"Service principal token acquisition failed: {e}")

    def _acquire_token_for_device_flow(self, force_refresh: bool = False) -> str:
        """Acquire token using device code flow (interactive)."""
        if not force_refresh and not self._is_token_expired() and self._cached_token:
            return self._cached_token

        if not self._app or not isinstance(self._app, PublicClientApplication):
            raise KytheraAuthError("Expected PublicClientApplication for device flow")

        try:
            # Try to get token silently first
            accounts = self._app.get_accounts()
            if accounts and not force_refresh:
                result = self._app.acquire_token_silent(
                    scopes=self.scopes, account=accounts[0]
                )
                if result and "access_token" in result:
                    access_token = result["access_token"]
                    if access_token:
                        self._cached_token = access_token
                        expires_in = result.get("expires_in", 3600)
                        if isinstance(expires_in, (int, float)):
                            self._token_expires_at = time.time() + expires_in
                        else:
                            self._token_expires_at = (
                                time.time() + 3600
                            )  # Default 1 hour
                        logger.info("Successfully acquired access token silently")
                        return self._cached_token  # type: ignore[return-value]

            # If silent acquisition fails, use device code flow
            flow = self._app.initiate_device_flow(scopes=self.scopes)
            if "user_code" not in flow:
                raise KytheraAuthError("Failed to create device flow")

            print(flow["message"])  # This contains the device code instructions

            result = self._app.acquire_token_by_device_flow(flow)

            if result and "access_token" in result:
                access_token = result["access_token"]
                if not access_token:
                    raise KytheraAuthError("Received empty access token")

                self._cached_token = access_token
                expires_in = result.get("expires_in", 3600)
                if isinstance(expires_in, (int, float)):
                    self._token_expires_at = time.time() + expires_in
                else:
                    self._token_expires_at = time.time() + 3600  # Default 1 hour
                logger.info("Successfully acquired access token using device code flow")
                return self._cached_token  # type: ignore[return-value]
            else:
                error_msg = "Unknown error"
                if result and isinstance(result, dict):
                    error_msg = result.get(
                        "error_description", result.get("error", "Unknown error")
                    )
                raise KytheraAuthError(f"Failed to acquire token: {error_msg}")

        except Exception as e:
            raise KytheraAuthError(f"Device flow token acquisition failed: {e}")

    def _get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid access token using the appropriate authentication flow.

        Args:
            force_refresh: Force token refresh even if current token is valid

        Returns:
            Valid access token

        Raises:
            KytheraAuthError: If token acquisition fails
        """
        if not self._app:
            raise KytheraAuthError("MSAL application not initialized")

        if self.client_secret:
            # Service principal - use client credentials flow
            return self._acquire_token_for_service_principal(force_refresh)
        else:
            # Interactive - use device code flow
            return self._acquire_token_for_device_flow(force_refresh)

    def _ensure_authenticated(self, force_refresh: bool = False) -> None:
        """Ensure we have a valid access token and update the session headers."""
        try:
            access_token = self._get_access_token(force_refresh)
            self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        except Exception as e:
            raise KytheraAuthError(f"Failed to authenticate: {e}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Make a request to the Kythera API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data for POST/PUT requests
            params: Query parameters

        Returns:
            API response as dictionary or list of dictionaries

        Raises:
            KytheraAPIError: When API returns an error
            KytheraAuthError: When authentication fails
            KytheraConnectionError: When connection fails
            KytheraTimeoutError: When request times out
        """
        url = urljoin(self.base_url, endpoint)

        try:
            # Ensure we have valid authentication
            self._ensure_authenticated()

            response = self.session.request(
                method=method, url=url, json=data, params=params
            )

            if response.status_code == 401:
                # Try to refresh token once
                try:
                    self._ensure_authenticated(force_refresh=True)

                    # Retry the request with new token
                    response = self.session.request(
                        method=method, url=url, json=data, params=params
                    )

                    if response.status_code == 401:
                        raise KytheraAuthError(
                            "Authentication failed after token refresh"
                        )
                except Exception as e:
                    raise KytheraAuthError(f"Authentication failed: {e}")

            if not response.is_success:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {}

                raise KytheraAPIError(
                    f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

            return response

        except httpx.TimeoutException:
            raise KytheraTimeoutError(f"Request timed out after {self.timeout} seconds")
        except httpx.ConnectError as e:
            raise KytheraConnectionError(f"Failed to connect to Kythera API: {e}")
        except httpx.RequestError as e:
            raise KytheraAPIError(f"Request failed: {e}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """Make a GET request to the API."""
        return self._make_request("GET", endpoint, params=params)

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """Make a POST request to the API."""
        return self._make_request("POST", endpoint, data=data)

    def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """Make a PUT request to the API."""
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> httpx.Response:
        """Make a DELETE request to the API."""
        return self._make_request("DELETE", endpoint)

    def clear_token_cache(self) -> None:
        """Clear the token cache."""
        self._cached_token = None
        self._token_expires_at = None
        logger.info("Token cache cleared")

    def is_authenticated(self) -> bool:
        """Check if we have a valid, non-expired token."""
        return bool(self._cached_token and not self._is_token_expired())

    def get_token_info(self) -> Dict[str, Any]:
        """
        Get information about the current token.

        Returns:
            Dictionary with token information
        """
        return {
            "has_token": bool(self._cached_token),
            "is_expired": self._is_token_expired(),
            "expires_at": self._token_expires_at,
            "time_to_expiry": (
                self._token_expires_at - time.time() if self._token_expires_at else None
            ),
            "auth_type": "service_principal" if self.client_secret else "device_flow",
        }

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
