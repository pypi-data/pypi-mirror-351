import requests
import logging
from typing import Optional, Callable
from .exceptions import APIError, AuthenticationError, InvalidRequestError, RateLimitError, ServiceUnavailableError, ConnectionError
from ..models import Chat, Image, Video, Audio
import json

def _is_html_response(response_text: str) -> bool:
    """Check if the response is HTML format."""
    return response_text.strip().startswith(('<!DOCTYPE', '<html', '<?xml'))

def _handle_error_response(response) -> str:
    """Handle error response and return appropriate error message."""
    try:
        # Try to parse as JSON first
        error_data = response.json()
        # Check if there's HTML in details.raw
        if isinstance(error_data, dict) and 'details' in error_data and 'raw' in error_data['details']:
            if _is_html_response(error_data['details']['raw']):
                return "The server returned an error in an unsupported format. Please try again later."
        return error_data.get('message', str(response.text))
    except json.JSONDecodeError:
        # Check if response is HTML
        if _is_html_response(response.text):
            return "The server returned an error in an unsupported format. Please try again later."
        return str(response.text)

class AlleAIClient:
    """A client for interacting with the AlleAI platform API."""

    def __init__(self, api_key: str, base_url: str = "https://boar-ace-gecko.ngrok-free.app/api/v1"):
        """Initialize the client with an API key and optional base URL.

        Args:
            api_key (str): The API key for authentication, required.
            base_url (str, optional): The base URL of the AlleAI API.".

        Raises:
            TypeError: If api_key or base_url is not a string.
        """
        if not isinstance(api_key, str):
            raise TypeError("'api_key' must be a string.")
        if not isinstance(base_url, str):
            raise TypeError("'base_url' must be a string.")

        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-KEY": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # Initialize feature handlers
        self.chat = Chat(self._request)
        self.image = Image(self._request, self._requestFormData)
        self.video = Video(self._request, self._requestFormData)
        self.audio = Audio(self._request, self._requestFormData)

    def _request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Internal method to make HTTP requests to the API."""
        
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            response_data = response.json()
            return json.dumps(response_data, indent=4)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            
            # Get error message using the helper function
            error_message = _handle_error_response(e.response)
            
            # Map status codes to user-friendly messages
            status_messages = {
                400: "Bad request. Please check your request parameters.",
                401: "Authentication failed. Please check your API key.",
                403: "You don't have permission to access this resource.",
                404: "The requested resource was not found.",
                429: "Rate limit exceeded. Please try again later.",
                500: "The server encountered an internal error.",
                502: "Bad gateway. The server received an invalid response.",
                503: "Service unavailable. Please try again later.",
                504: "Gateway timeout. The server didn't respond in time."
            }
            
            # Get a user-friendly message based on status code
            user_message = status_messages.get(
                status_code, 
                error_message
            )
            
            # Log the full error for debugging (this won't be shown to users)
            logging.debug(f"API Error {status_code}: {error_message}")
            
            # Raise appropriate exception with user-friendly message
            if status_code == 401:
                raise AuthenticationError(message=user_message, code="AUTH_ERROR")
            elif status_code == 400:
                raise InvalidRequestError(message=user_message, code="INVALID_REQUEST")
            elif status_code == 429:
                raise RateLimitError(message=user_message, code="RATE_LIMIT")
            elif status_code >= 500:
                raise ServiceUnavailableError(message=user_message, code="SERVICE_ERROR")
            else:
                raise APIError(message=user_message, code=f"API_ERROR_{status_code}")
                
        except requests.exceptions.ConnectionError as e:
            # Log the full error for debugging
            logging.debug(f"Connection Error: {str(e)}")
            raise ConnectionError(
                message="Could not connect to the API. Please check your internet connection.", 
                code="CONNECTION_ERROR"
            )
        except requests.exceptions.Timeout as e:
            logging.debug(f"Timeout Error: {str(e)}")
            raise APIError(
                message="Request timed out. Please try again later.", 
                code="TIMEOUT_ERROR"
            )
        except requests.exceptions.RequestException as e:
            logging.debug(f"Request Exception: {str(e)}")
            raise APIError(
                message="An error occurred while making the request.", 
                code="REQUEST_ERROR"
            )
        except Exception as e:
            # Catch any other unexpected errors
            logging.error(f"Unexpected error: {str(e)}")
            raise APIError(
                message="An unexpected error occurred. Please try again later.",
                code="UNEXPECTED_ERROR"
            )

    def _requestFormData(self, method: str, endpoint: str, form_data: dict) -> dict:
        """Internal method to make HTTP requests with FormData to the API."""
        url = f"{self.base_url}{endpoint}"
        try:
            # Create headers without Content-Type (requests will set it automatically with boundary)
            headers = {
                "X-API-KEY": self.api_key,
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                files=form_data
            )
            response.raise_for_status()
            response_data = response.json()
            return json.dumps(response_data, indent=4)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            
            # Get error message using the helper function
            error_message = _handle_error_response(e.response)
            
            # Map status codes to user-friendly messages
            status_messages = {
                400: "Bad request. Please check your request parameters.",
                401: "Authentication failed. Please check your API key.",
                403: "You don't have permission to access this resource.",
                404: "The requested resource was not found.",
                429: "Rate limit exceeded. Please try again later.",
                500: "The server encountered an internal error.",
                502: "Bad gateway. The server received an invalid response.",
                503: "Service unavailable. Please try again later.",
                504: "Gateway timeout. The server didn't respond in time."
            }
            
            # Get a user-friendly message based on status code
            user_message = status_messages.get(
                status_code, 
                error_message
            )
            
            # Log the full error for debugging (this won't be shown to users)
            logging.debug(f"API Error {status_code}: {error_message}")
            
            # Raise appropriate exception with user-friendly message
            if status_code == 401:
                raise AuthenticationError(message=user_message, code="AUTH_ERROR")
            elif status_code == 400:
                raise InvalidRequestError(message=user_message, code="INVALID_REQUEST")
            elif status_code == 429:
                raise RateLimitError(message=user_message, code="RATE_LIMIT")
            elif status_code >= 500:
                raise ServiceUnavailableError(message=user_message, code="SERVICE_ERROR")
            else:
                raise APIError(message=user_message, code=f"API_ERROR_{status_code}")
                
        except requests.exceptions.ConnectionError as e:
            # Log the full error for debugging
            logging.debug(f"Connection Error: {str(e)}")
            raise ConnectionError(
                message="Could not connect to the API. Please check your internet connection.", 
                code="CONNECTION_ERROR"
            )
        except requests.exceptions.Timeout as e:
            logging.debug(f"Timeout Error: {str(e)}")
            raise APIError(
                message="Request timed out. Please try again later.", 
                code="TIMEOUT_ERROR"
            )
        except requests.exceptions.RequestException as e:
            logging.debug(f"Request Exception: {str(e)}")
            raise APIError(
                message="An error occurred while making the request.", 
                code="REQUEST_ERROR"
            )
        except Exception as e:
            # Catch any other unexpected errors
            logging.error(f"Unexpected error: {str(e)}")
            raise APIError(
                message="An unexpected error occurred. Please try again later.",
                code="UNEXPECTED_ERROR"
            )