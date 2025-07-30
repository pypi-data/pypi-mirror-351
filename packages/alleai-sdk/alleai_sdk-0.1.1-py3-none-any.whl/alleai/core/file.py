import base64
import os
import requests
from urllib.parse import urlparse
from typing import Literal, Union

class FileHandler:
    def __init__(self, max_size_mb=20):
        """Initialize FileHandler with optional max file size (in MB)."""
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        # Supported file extensions by type (case-insensitive)
        self.supported_extensions = {
            'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
            'video': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'},
            'audio': {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}
        }

    def _validate_file_type(self, file_ext: str, file_type: str) -> bool:
        """
        Validate if the file extension is supported for the given file type.
        
        Args:
            file_ext (str): File extension (e.g., '.jpg', '.mp3')
            file_type (str): Type of file ('image', 'video', 'audio')
            
        Returns:
            bool: True if supported, False otherwise
        """
        file_ext = file_ext.lower()
        return file_ext in self.supported_extensions.get(file_type, set())

    def _get_file_extension(self, path: str) -> str:
        """Extract file extension from path or URL."""
        return os.path.splitext(path)[1].lower()

    def attach_file(self, path: str, file_type: Literal['image', 'video', 'audio']) -> bytes:
        """
        Load a file from local path or URL and return its binary content.
        
        Args:
            path (str): Local file path or URL
            file_type (str): Type of file ('image', 'video', 'audio')
        
        Returns:
            bytes: Binary content of the file
        
        Raises:
            FileNotFoundError: If the local file doesn't exist
            ValueError: If the file type is not supported or file exceeds max size
            requests.RequestException: If URL fetch fails
        """
        # Check if path is URL or local file
        is_url = bool(urlparse(path).scheme)
        
        # Get file extension and validate type
        file_ext = self._get_file_extension(path)
        if not self._validate_file_type(file_ext, file_type):
            supported_exts = self.supported_extensions.get(file_type, set())
            raise ValueError(
                f"File type '{file_ext}' not supported for {file_type}. "
                f"Supported extensions: {', '.join(supported_exts)}"
            )

        if is_url:
            # Handle URL
            response = requests.get(path, stream=True)
            response.raise_for_status()
            
            # Check content length if available
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_size_bytes:
                raise ValueError(
                    f"File size ({int(content_length) / 1024 / 1024:.2f}MB) "
                    f"exceeds max limit ({self.max_size_bytes / 1024 / 1024:.0f}MB)"
                )
                
            return response.content
        else:
            # Handle local file
            if not os.path.isfile(path):
                raise FileNotFoundError(f"File not found: {path}")

            # Check file size
            file_size = os.path.getsize(path)
            if file_size > self.max_size_bytes:
                raise ValueError(
                    f"File size ({file_size / 1024 / 1024:.2f}MB) "
                    f"exceeds max limit ({self.max_size_bytes / 1024 / 1024:.0f}MB)"
                )

            # Read file binary content
            with open(path, "rb") as file:
                return file.read()