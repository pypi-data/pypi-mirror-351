import logging
import os
import sys

def setup_logging(level=logging.INFO, log_file=None):
    """Set up logging configuration for the AlleAI SDK.
    
    Args:
        level: The logging level (default: logging.INFO)
        log_file: Optional file path to save logs
    """
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (without sensitive information)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (with detailed information for debugging)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)  # Full logging to file
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Prevent logging from propagating to the root logger
    root_logger.propagate = False
    
    # Set requests and urllib3 loggers to WARNING level to reduce noise
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger 