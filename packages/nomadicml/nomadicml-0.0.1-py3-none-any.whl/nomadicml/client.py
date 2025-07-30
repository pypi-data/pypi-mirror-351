"""
NomadicML API client for interacting with the DriveMonitor backend.
"""

import json
import logging
from typing import Dict, Optional, Any, BinaryIO, Tuple
import requests

from .exceptions import NomadicMLError, AuthenticationError, APIError
from .utils import validate_api_key, format_error_message

logger = logging.getLogger("nomadicml")

DEFAULT_BASE_URL = "https://szwckme9pz.us-west-2.awsapprunner.com"
DEFAULT_COLLECTION_NAME = "videos"
DEFAULT_TIMEOUT = 30  # seconds


class NomadicML:
    """
    NomadicML client for interacting with the DriveMonitor API.
    
    This is the base client that handles authentication and HTTP requests.
    
    Args:
        api_key: Your API key for authentication.
        base_url: The base URL of the API. Defaults to the production API.
        timeout: The default timeout for API requests in seconds.
        collection_name: The Firestore collection name to use for videos.
    """

    def __init__(
        self, 
        api_key: str, 
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ):
        validate_api_key(api_key)
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.collection_name = collection_name
        
        # Set up a session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "User-Agent": f"NomadicML-Python-SDK/0.1.0",
        })
        
        logger.debug(f"Initialized NomadicML client with base URL: {self.base_url}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Tuple[str, BinaryIO, str]]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make an HTTP request to the API.
        
        Args:
            method: The HTTP method to use.
            endpoint: The API endpoint.
            params: Query parameters.
            data: Form data.
            json_data: JSON data.
            files: Files to upload.
            timeout: Request timeout in seconds.
            
        Returns:
            The HTTP response.
            
        Raises:
            AuthenticationError: If authentication fails.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        if timeout is None:
            timeout = self.timeout
            
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                files=files,
                timeout=timeout,
            )
            
            # Check for error responses
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed. Check your API key.")
                
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except (ValueError, json.JSONDecodeError):
                    error_data = {"message": response.text}
                
                error_message = format_error_message(error_data)
                raise APIError(response.status_code, error_message, error_data)
                
            return response
            
        except requests.RequestException as e:
            # Handle network errors
            raise NomadicMLError(f"Request failed: {str(e)}")
    
    def verify_auth(self) -> Dict[str, Any]:
        """
        Verify that the API key is valid.
        
        Returns:
            A dictionary with authentication information.
            
        Raises:
            AuthenticationError: If authentication fails.
        """
        response = self._make_request("POST", "/api/keys/verify")
        return response.json()
