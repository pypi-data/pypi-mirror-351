from typing import List, Dict, Optional, TypedDict, Literal

from ..core.exceptions import InvalidRequestError
from ..core.utils import handle_errors
from .base import BaseModel
from  ..core.helper import fetch_binary_data

# TypedDict for Text-to-Video parameters
class TextToVideoParams(TypedDict):
    models: List[str]
    prompt: str
    duration: Optional[float]
    loop: Optional[bool]
    aspect_ratio: Optional[str]
    fps: Optional[int]
    dimension: Optional[str]
    resolution: Optional[str]
    seed: Optional[int]

# TypedDict for Video Edit parameters
class VideoEditParams(TypedDict):
    models: List[str]
    prompt: str  # Changed from 'action_prompt' to 'prompt'
    videoUrl: str

# TypedDict for Video Status parameters
class VideoStatusParams(TypedDict):
    requestId: str

class Video(BaseModel):
    """Handles video-related requests to the AlleAI platform."""
    
    @handle_errors
    def generate(self, params: TextToVideoParams) -> dict:
        """Generate a video from text using multiple models.
        
        Args:
            params (TextToVideoParams): Parameters for text-to-video generation. Required:
                - models: List of model names (e.g., ["nova-reel"]).
                - prompt: The text prompt describing the desired video (max 512 characters).
            
            Optional:
                - duration: Length of the video in seconds (max 6 seconds, factors of 6 recommended).
                - loop: Whether the video should loop seamlessly (default: False).
                - aspect_ratio: Aspect ratio of the video (e.g., "16:9").
                - fps: Frames per second for the video (e.g., 24).
                - dimension: Video dimensions in format "WIDTHxHEIGHT" (e.g., "1280x720").
                - resolution: Video quality setting ("720p" or "1080p").
                - seed: Random seed for reproducibility (integer).
        
        Returns:
            dict: API response with generated video data.
        
        Raises:
            InvalidRequestError: If required parameters are missing or invalid.
            
        Examples:
            Generate a video with specific parameters:
            >>> from alleai.core import AlleAIClient
            >>> client = AlleAIClient(api_key="your-api-key")
            >>> response = client.video.generate({
            ...     "models": ["nova-reel"],
            ...     "prompt": "robotic arm assembling a car in a futuristic factory",
            ...     "duration": 6,
            ...     "loop": False,
            ...     "aspect_ratio": "16:9",
            ...     "fps": 24,
            ...     "dimension": "1280x720",
            ...     "resolution": "720p",
            ...     "seed": 8
            ... })
            >>> print(response)
        """
        # Required fields validation
        required_fields = {"models", "prompt"}
        missing_fields = required_fields - set(params.keys())
        if missing_fields:
            raise InvalidRequestError(
                message=f"Missing required parameters: {missing_fields}",
                code="MISSING_PARAMS"
            )
        
        # Validate models
        if not isinstance(params["models"], list) or not all(isinstance(m, str) for m in params["models"]):
            raise InvalidRequestError(
                message="'models' must be a list of strings.",
                code="INVALID_MODELS"
            )
        
        # Validate prompt
        if not isinstance(params["prompt"], str):
            raise InvalidRequestError(
                message="'prompt' must be a string.",
                code="INVALID_PROMPT"
            )
        if len(params["prompt"]) > 512:
            raise InvalidRequestError(
                message="'prompt' must not exceed 512 characters.",
                code="PROMPT_TOO_LONG"
            )
        
        # Set defaults for optional fields
        defaults = {
            "loop": False
        }
        for key, value in defaults.items():
            params.setdefault(key, value)  # type: ignore
        
        # Additional validation
        if "duration" in params and params["duration"] is not None:
            if not isinstance(params["duration"], (int, float)):
                raise InvalidRequestError(
                    message="'duration' must be a number.",
                    code="INVALID_DURATION"
                )
            if params["duration"] <= 0 or params["duration"] > 6:
                raise InvalidRequestError(
                    message="'duration' must be a positive number not exceeding 6 seconds.",
                    code="DURATION_OUT_OF_RANGE"
                )
        
        if "loop" in params and not isinstance(params["loop"], bool):
            raise InvalidRequestError(
                message="'loop' must be a boolean.",
                code="INVALID_LOOP"
            )
        
        if "aspect_ratio" in params and params["aspect_ratio"] is not None:
            if not isinstance(params["aspect_ratio"], str):
                raise InvalidRequestError(
                    message="'aspect_ratio' must be a string (e.g., '16:9').",
                    code="INVALID_ASPECT_RATIO"
                )
            if ":" not in params["aspect_ratio"]:
                raise InvalidRequestError(
                    message="'aspect_ratio' must be in the format 'width:height' (e.g., '16:9').",
                    code="INVALID_ASPECT_RATIO_FORMAT"
                )
        
        if "fps" in params and params["fps"] is not None and not isinstance(params["fps"], int):
            raise InvalidRequestError(
                message="'fps' must be an integer.",
                code="INVALID_FPS"
            )
        
        if "dimension" in params and params["dimension"] is not None:
            if not isinstance(params["dimension"], str):
                raise InvalidRequestError(
                    message="'dimension' must be a string in format 'WIDTHxHEIGHT' (e.g., '1280x720').",
                    code="INVALID_DIMENSION"
                )
            if "x" not in params["dimension"]:
                raise InvalidRequestError(
                    message="'dimension' must be in the format 'WIDTHxHEIGHT' (e.g., '1280x720').",
                    code="INVALID_DIMENSION_FORMAT"
                )
        
        if "resolution" in params and params["resolution"] is not None:
            if not isinstance(params["resolution"], str):
                raise InvalidRequestError(
                    message="'resolution' must be a string.",
                    code="INVALID_RESOLUTION"
                )
            if params["resolution"] not in ["720p", "1080p"]:
                raise InvalidRequestError(
                    message="'resolution' must be either '720p' or '1080p'.",
                    code="INVALID_RESOLUTION_VALUE"
                )
        
        if "seed" in params and params["seed"] is not None and not isinstance(params["seed"], int):
            raise InvalidRequestError(
                message="'seed' must be an integer.",
                code="INVALID_SEED"
            )
        
        return self._make_request("post", "/video/generate", params)
    
    def edit(self, params: VideoEditParams) -> dict:
        """Edit an existing video using multiple models.
        
        Args:
            params (VideoEditParams): Parameters for video editing. Required:
                - models: List of model names (e.g., ["model1", "model2"]).
                - prompt: The text prompt describing the desired edits.
                - videoUrl: URL of the video to edit or a base64 string of video file.
        
        Returns:
            dict: API response with edited video data (e.g., URLs or file paths).
        
        Raises:
            InvalidRequestError: If required parameters are missing or invalid.
        """
        # Required fields validation
        required_fields = {"models", "prompt", "videoUrl"}  # Changed 'action_prompt' to 'prompt'
        missing_fields = required_fields - set(params.keys())
        if missing_fields:
            raise InvalidRequestError(f"Missing required parameters: {missing_fields}")
        
        # Validate models
        if not isinstance(params["models"], list) or not all(isinstance(m, str) for m in params["models"]):
            raise InvalidRequestError("'models' must be a list of strings.")
        
        # Validate prompt and videoUrl (changed from 'action_prompt' to 'prompt')
        if not isinstance(params["prompt"], str):
            raise InvalidRequestError("'prompt' must be a string.")
        if not isinstance(params["videoUrl"], str):
            raise InvalidRequestError("'videoUrl' must be a string.")
        
        return self._make_request("post", "/video/edit", params)
    
    @handle_errors
    def get_video_status(self, params: VideoStatusParams) -> dict:
        """Check the status of a video generation job.
        
        Args:
            params (VideoStatusParams): Parameters for checking job status. Required:
                - requestId: The job ID of the video request in queue (e.g., "AlleAI-T123").
                
        Returns:
            dict: API response with job status information.
                
        Raises:
            InvalidRequestError: If required parameters are missing or invalid.
            
        Examples:
            Check the status of a video generation job:
            >>> from alleai.core import AlleAIClient
            >>> client = AlleAIClient(api_key="your-api-key")
            >>> response = client.video.get_video_status({
            ...     "requestId": "AlleAI-T123"
            ... })
            >>> print(response)
        """
        # Required fields validation
        required_fields = {"requestId"}
        missing_fields = required_fields - set(params.keys())
        if missing_fields:
            raise InvalidRequestError(
                message=f"Missing required parameters: {missing_fields}",
                code="MISSING_PARAMS"
            )
        
        # Validate requestId
        if not isinstance(params["requestId"], str) or not params["requestId"]:
            raise InvalidRequestError(
                message="'requestId' must be a non-empty string.",
                code="INVALID_REQUEST_ID"
            )
        
        return self._make_request("post", "/video/status", params)