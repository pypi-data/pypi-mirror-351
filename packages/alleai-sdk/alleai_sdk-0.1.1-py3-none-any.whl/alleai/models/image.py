from typing import List, TypedDict, Literal, Optional, Dict, Any
from ..core.exceptions import InvalidRequestError
from ..core.utils import handle_errors
from .base import BaseModel
from ..core.helper import fetch_binary_data
from ..core.file import FileHandler

# Get a FileHandler instance for this module
_file_handler = FileHandler()

# TypedDict for image.generate parameters
class ImageGenerateParams(TypedDict):
    models: List[str]
    prompt: str
    model_specific_params: Optional[Dict[str, Dict[str, Any]]]
    n: Optional[int]
    width: Optional[int]
    height: Optional[int]
    seed: Optional[int]

# TypedDict for image.edit parameters
class ImageEditParams(TypedDict):
    models: List[str]
    image_file: str
    prompt: str


class Image(BaseModel):
    """Handles image-related requests to the AlleAI platform.

    Examples:
        Generate an AI-generated image:
        >>> from alleai.core import AlleAIClient
        >>> client = AlleAIClient(api_key="your-api-key")
        >>> response = client.image.generate({
        ...     "models": ["nova-canvas"],
        ...     "prompt": "A futuristic cityscape at sunset with neon lights and flying cars",
        ...     "model_specific_params": {
        ...         "nova-canvas": {
        ...             "n": 1,
        ...             "height": 1024,
        ...             "width": 1024
        ...         }
        ...     },
        ...     "n": 1,
        ...     "height": 1024,
        ...     "width": 1024,
        ...     "seed": 8
        ... })
        >>> print(response)
    """
    @handle_errors
    def generate(self, params: ImageGenerateParams) -> dict:
        """Generate images using multiple models.

        Args:
            params (ImageGenerateParams): Parameters for image generation. Required:
                - models: List of model names (e.g., ["nova-canvas", "titan-image-generator"]).
                - prompt: The text prompt describing the desired image.

            Optional:
                - model_specific_params: Dictionary containing model-specific configurations.
                  Example: {"nova-canvas": {"n": 1, "height": 1024, "width": 1024}}
                - n: Number of images to generate (default: 1).
                - width: Image width in pixels (e.g., 1024).
                - height: Image height in pixels (e.g., 1024).
                - seed: Random seed for reproducibility (integer).

        Returns:
            dict: API response with generated image data.

        Raises:
            InvalidRequestError: If required parameters are missing or invalid.

        Examples:
            Generate an AI-generated image:
            >>> from alleai.core import AlleAIClient
            >>> client = AlleAIClient(api_key="your-api-key")
            >>> response = client.image.generate({
            ...     "models": ["nova-canvas"],
            ...     "prompt": "A futuristic cityscape at sunset with neon lights and flying cars",
            ...     "model_specific_params": {
            ...         "nova-canvas": {
            ...             "n": 1,
            ...             "height": 1024,
            ...             "width": 1024
            ...         }
            ...     },
            ...     "n": 1,
            ...     "height": 1024,
            ...     "width": 1024,
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
        if not isinstance(params["prompt"], str) or params["prompt"] == "":
            raise InvalidRequestError(
                message="'prompt' must be a non-empty string.",
                code="INVALID_PROMPT"
            )

        # Set defaults for optional fields
        defaults = {
            "n": 1
        }
        for key, value in defaults.items():
            params.setdefault(key, value)  # type: ignore

        # Additional validation for optional fields
        if "width" in params and params["width"] is not None and not isinstance(params["width"], int):
            raise InvalidRequestError(
                message="'width' must be an integer.",
                code="INVALID_WIDTH"
            )
        if "height" in params and params["height"] is not None and not isinstance(params["height"], int):
            raise InvalidRequestError(
                message="'height' must be an integer.",
                code="INVALID_HEIGHT"
            )
        if "n" in params and not isinstance(params["n"], int):
            raise InvalidRequestError(
                message="'n' must be an integer.",
                code="INVALID_N"
            )
        if "seed" in params and params["seed"] is not None and not isinstance(params["seed"], int):
            raise InvalidRequestError(
                message="'seed' must be an integer.",
                code="INVALID_SEED"
            )
        if "model_specific_params" in params and params["model_specific_params"] is not None:
            if not isinstance(params["model_specific_params"], dict):
                raise InvalidRequestError(
                    message="'model_specific_params' must be a dictionary.",
                    code="INVALID_MODEL_PARAMS"
                )
            for model, model_params in params["model_specific_params"].items():
                if not isinstance(model_params, dict):
                    raise InvalidRequestError(
                        message=f"Parameters for model '{model}' must be a dictionary.",
                        code="INVALID_MODEL_PARAMS_FORMAT"
                    )

        # Make the API request
        return self._make_request("post", "/image/generate", params)

    @handle_errors
    def edit(self, params: ImageEditParams) -> dict:
        """Edit an existing image using multiple models.

        Args:
            params (ImageEditParams): Parameters for image editing. Required:
                - models: List of model names (e.g., ["nova-canvas"]).
                - image_file: Either an image URL or local file path.
                - prompt: The text prompt describing the desired changes.

        Returns:
            dict: API response with edited image data.

        Raises:
            InvalidRequestError: If required parameters are missing or invalid.
            ValueError: If the file type is not supported or file size exceeds limit.

        Examples:
            Edit an image using an AI model:
            >>> from alleai.core import AlleAIClient
            >>> client = AlleAIClient(api_key="your-api-key")
            >>> response = client.image.edit({
            ...     "models": ["nova-canvas"],
            ...     "image_file": "https://example.com/image.jpg",  # or local file path
            ...     "prompt": "Replace the sky with a vibrant sunset and add glowing city lights."
            ... })
            >>> print(response)
        """
        # Required fields validation
        required_fields = {"models", "image_file", "prompt"}
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

        # Validate image_file
        if not isinstance(params["image_file"], str) or params["image_file"] == "":
            raise InvalidRequestError(
                message="'image_file' must be a non-empty string (URL or file path)",
                code="INVALID_IMAGE_FILE"
            )

        # Validate prompt
        if not isinstance(params["prompt"], str) or params["prompt"] == "":
            raise InvalidRequestError(
                message="'prompt' must be a non-empty string",
                code="INVALID_PROMPT"
            )

        # Use FileHandler's attach_file to handle the image file with type validation
        try:
            buffer = _file_handler.attach_file(params["image_file"], file_type="image")
        except (ValueError, FileNotFoundError) as e:
            raise InvalidRequestError(
                message=str(e),
                code="INVALID_IMAGE_FILE"
            )

        # Create form data for the request
        form_data = {
            f"models[{i}]": (None, value)
            for i, value in enumerate(params["models"])
        }
        form_data["image_file"] = ("image.jpg", buffer, "image/jpeg")
        form_data["prompt"] = (None, params["prompt"])

        # Make the API request
        return self._requestFormData("post", "/image/edit", form_data)
    