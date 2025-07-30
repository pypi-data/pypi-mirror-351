import requests
import os
from urllib.parse import urlparse
from typing import Union

def fetch_binary_data(source: str) -> bytes:
    """
    Fetch binary data from either a URL or local file path.
    Explicitly fails if the input is neither.

    Args:
        source: Must be either:
                - A valid URL (with http://, https://, etc.)
                - An existing local file path

    Returns:
        Binary content as bytes

    Raises:
        ValueError: If input is neither valid URL nor accessible file
        requests.RequestException: For URL fetch errors
        IOError: For file read errors
    """
    # Check URL first (MUST have scheme like http://)
    parsed = urlparse(source)
    if parsed.scheme and parsed.netloc:  # Valid URL structure
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise requests.RequestException(
                f"URL fetch failed for '{source}': {str(e)}"
            ) from e

    # Treat as file path (absolute or relative)
    if os.path.isfile(source):  # Check if file exists
        try:
            with open(source, 'rb') as f:
                return f.read()
        except IOError as e:
            raise IOError(
                f"Could not read file '{source}': {str(e)}"
            ) from e

    # Final fallback
    raise ValueError(
        f"Input must be either:\n"
        f"1. A valid URL (e.g., 'https://example.com')\n"
        f"2. An existing file path (e.g., '/path/to/file')\n"
        f"Got: '{source}'"
    )