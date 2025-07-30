# alleai/__init__.py

"""
AlleAI SDK - A Python SDK for interacting with the AlleAI platform.
"""

__version__ = "0.1.0"

from .core.client import AlleAIClient
from .core.exceptions import (
    AlleAIError, APIError, AuthenticationError, 
    InvalidRequestError, RateLimitError, 
    ServiceUnavailableError, ConnectionError
)
from .core.utils import handle_errors
from .core.logging_config import setup_logging

__all__ = [
    "AlleAIClient",
    "AlleAIError", "APIError", "AuthenticationError", 
    "InvalidRequestError", "RateLimitError", 
    "ServiceUnavailableError", "ConnectionError",
    "handle_errors", "setup_logging"
]
