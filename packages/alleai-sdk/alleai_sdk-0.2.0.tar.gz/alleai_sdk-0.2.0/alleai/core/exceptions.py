class AlleAIError(Exception):
    """Base exception class for AlleAI SDK errors."""
    def __init__(self, message=None, code=None, details=None):
        self.message = message or "An unknown error occurred"
        self.code = code
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message

class APIError(AlleAIError):
    """Raised when the API returns an unexpected error."""
    pass

class AuthenticationError(AlleAIError):
    """Raised when authentication fails (e.g., invalid API key)."""
    pass

class InvalidRequestError(AlleAIError):
    """Raised when the request is malformed or invalid."""
    pass

class RateLimitError(AlleAIError):
    """Raised when the API rate limit is exceeded."""
    pass

class ServiceUnavailableError(AlleAIError):
    """Raised when the service is temporarily unavailable."""
    pass

class ConnectionError(AlleAIError):
    """Raised when there is an issue connecting to the API."""
    pass