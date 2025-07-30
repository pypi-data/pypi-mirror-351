from typing import List, Dict, Optional, TypedDict, Literal, Any
from ..core.exceptions import InvalidRequestError
from ..core.utils import handle_errors
from .base import BaseModel
from ..core.helper import fetch_binary_data
from ..core.file import FileHandler

# Get a FileHandler instance for this module
_file_handler = FileHandler()

# TypedDict for Text-to-Speech (TTS) parameters


class TTSParams(TypedDict):
    models: List[str]
    prompt: str
    voice: Optional[str]
    model_specific_params: Optional[Dict[str, Dict[str, Any]]]

# TypedDict for Speech-to-Text (STT) parameters


class STTParams(TypedDict):
    models: List[str]
    audio_file: str


# TypedDict for Audio Generation parameters


class AudioGenerateParams(TypedDict):
    models: List[str]
    prompt: str
    model_specific_params: Optional[Dict[str, Dict[str, Any]]]


class Audio(BaseModel):
    """Handles audio-related requests to the AlleAI platform.

    Examples:
        Basic text-to-speech conversion:
           >>> from alleai.core import AlleAIClient
           >>> client = AlleAIClient(api_key="your-api-key")
           >>> response = client.audio.tts({
           ...     "models": ["gpt-4o-mini-tts"],
           ...     "prompt": "The first thing I ever said",
           ...     "voice": "nova"
           ... })
           >>> print(response)
    """

    
    @handle_errors
    def tts(self, params: TTSParams) -> dict:
        """Convert text to speech using multiple models.

        Args:
            params (TTSParams): Parameters for text-to-speech. Required:
                - models: List of model names (e.g., ["gpt-4o-mini-tts"]).
                - prompt: The text to convert to speech.

            Optional:
                - voice: Voice to use for text-to-speech (e.g., "nova").
                - model_specific_params: Dictionary containing model-specific configurations.
                  Example: {"gpt-4o-mini-tts": {"voice": "alternative-voice"}}

        Returns:
            dict: API response with audio data.

        Raises:
            InvalidRequestError: If required parameters are missing or invalid.

        Examples:
            Convert text to speech:
            >>> from alleai.core import AlleAIClient
            >>> client = AlleAIClient(api_key="your-api-key")
            >>> response = client.audio.tts({
            ...     "models": ["gpt-4o-mini-tts"],
            ...     "prompt": "The first thing I ever said",
            ...     "voice": "nova",
            ...     "model_specific_params": {
            ...         "gpt-4o-mini-tts": {
            ...             "voice": "alternative-voice"
            ...         }
            ...     }
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

        # Validate that only one model is provided
        if len(params["models"]) != 1:
            raise InvalidRequestError(
                message="For now, audio processing requires exactly one model.",
                code="INVALID_MODEL_COUNT"
            )

        # Validate prompt
        if not isinstance(params["prompt"], str) or params["prompt"] == "":
            raise InvalidRequestError(
                message="'prompt' must be a non-empty string.",
                code="INVALID_PROMPT"
            )

        # Validate model_specific_params if present
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

        return self._make_request("post", "/audio/tts", params)

    @handle_errors
    def stt(self, params: STTParams) -> dict:
        """Convert speech to text using multiple models.

        Args:
            params (STTParams): Parameters for speech-to-text. Required:
                - models: List of model names (e.g., ["whisper-v3"]).
                - audio_file: Either an audio URL or local file path.

        Returns:
            dict: API response with transcription data.

        Raises:
            InvalidRequestError: If required parameters are missing or invalid.
            ValueError: If the file type is not supported or file size exceeds limit.

        Examples:
            Transcribe audio:
            >>> from alleai.core import AlleAIClient
            >>> client = AlleAIClient(api_key="your-api-key")
            >>> response = client.audio.stt({
            ...     "models": ["whisper-v3"],
            ...     "audio_file": "https://example.com/audio.mp3"  # or local file path
            ... })
            >>> print(response)
        """
        # Required fields validation
        required_fields = {"models", "audio_file"}
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

        # Validate that only one model is provided
        if len(params["models"]) != 1:
            raise InvalidRequestError(
                message="For now, audio processing requires exactly one model.",
                code="INVALID_MODEL_COUNT"
            )

        # Validate audio_file
        if not isinstance(params["audio_file"], str) or params["audio_file"] == "":
            raise InvalidRequestError(
                message="'audio_file' must be a non-empty string (URL or file path).",
                code="INVALID_AUDIO_FILE"
            )

        # Use FileHandler's attach_file to handle the audio file with type validation
        try:
            buffer = _file_handler.attach_file(params["audio_file"], file_type="audio")
        except (ValueError, FileNotFoundError) as e:
            raise InvalidRequestError(
                message=str(e),
                code="INVALID_AUDIO_FILE"
            )

        # Create form data for the request
        form_data = {
            f"models[{i}]": (None, value)
            for i, value in enumerate(params["models"])
        }
        form_data["audio_file"] = ("audio.mp3", buffer, "audio/mpeg")

        return self._requestFormData("post", "/audio/stt", form_data)

    @handle_errors
    def generate(self, params: AudioGenerateParams) -> dict:
        """Generate audio content using multiple models.

        Args:
            params (AudioGenerateParams): Parameters for audio generation. Required:
                - models: List of model names (e.g., ["lyria"]).
                - prompt: The text prompt describing the desired audio.

            Optional:
                - model_specific_params: Dictionary containing model-specific configurations.
                  Example: {"lyria": {"quality": "hd"}}

        Returns:
            dict: API response with generated audio data.

        Raises:
            InvalidRequestError: If required parameters are missing or invalid.

        Examples:
            Generate audio:
            >>> from alleai.core import AlleAIClient
            >>> client = AlleAIClient(api_key="your-api-key")
            >>> response = client.audio.generate({
            ...     "models": ["lyria"],
            ...     "prompt": "Create a relaxing ambient track",
            ...     "model_specific_params": {}
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

        # Validate that only one model is provided
        if len(params["models"]) != 1:
            raise InvalidRequestError(
                message="For now, audio processing requires exactly one model.",
                code="INVALID_MODEL_COUNT"
            )

        # Validate prompt
        if not isinstance(params["prompt"], str) or params["prompt"] == "":
            raise InvalidRequestError(
                message="'prompt' must be a non-empty string.",
                code="INVALID_PROMPT"
            )

        # Validate model_specific_params if present
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

        return self._make_request("post", "/audio/generate", params)
