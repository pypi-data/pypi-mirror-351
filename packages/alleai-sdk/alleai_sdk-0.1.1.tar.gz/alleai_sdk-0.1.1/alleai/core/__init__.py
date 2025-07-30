from .exceptions import (
    AlleAIError, APIError, AuthenticationError, 
    InvalidRequestError, RateLimitError, 
    ServiceUnavailableError, ConnectionError
)
from .utils import handle_errors
from .logging_config import setup_logging

# Setup default logging
setup_logging()

# Import client after other dependencies
from .client import AlleAIClient

# Initialize FileHandler and expose attach_file at the end
from .file import FileHandler
_file_handler = FileHandler(max_size_mb=20)
attach_file = _file_handler.attach_file

__all__ = [
    "AlleAIClient", 
    "AlleAIError", "APIError", "AuthenticationError", 
    "InvalidRequestError", "RateLimitError", 
    "ServiceUnavailableError", "ConnectionError",
    "handle_errors", "setup_logging",
    "attach_file"
]