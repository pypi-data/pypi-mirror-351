import functools
import logging
import traceback
from .exceptions import AlleAIError

def handle_errors(func):
    """Decorator to handle exceptions in a user-friendly way.
    
    This decorator catches AlleAI SDK exceptions and presents them in a clean,
    professional manner without exposing implementation details.
    
    Examples:
        @handle_errors
        def my_function():
            # Implementation that might raise exceptions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AlleAIError as e:
            # Log the full exception details for debugging
            logging.error(f"AlleAI SDK Error: {type(e).__name__}: {e}")
            if hasattr(e, 'details') and e.details:
                logging.debug(f"Error details: {e.details}")
            
            # Return a user-friendly message
            print(f"Error: {e}")
            return None
        except Exception as e:
            # For unexpected errors, don't expose details to the user
            logging.error(f"Unexpected error: {type(e).__name__}: {e}")
            logging.debug(traceback.format_exc())
            
            # Generic message for unexpected errors
            print("An unexpected error occurred. Please try again later.")
            return None
    return wrapper 