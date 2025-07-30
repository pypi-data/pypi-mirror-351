# AlleAI Python SDK

[![PyPI version](https://badge.fury.io/py/alleai-sdk.svg)](https://badge.fury.io/py/alleai-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/alleai-sdk)](https://pypi.org/project/alleai-sdk/)
[![License](https://img.shields.io/github/license/pYGOD3512/alle-ai-sdk-python)](https://github.com/pYGOD3512/alle-ai-sdk-python/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/pYGOD3512/alle-ai-sdk-python/blob/main/docs)

A powerful Python SDK for interacting with the AlleAI platform, providing easy access to state-of-the-art AI models for image generation, audio processing, and more.

## Features

- **Chat Completions**
  - Multiple model support (GPT-4O, O4-Mini, Claude-3-Sonnet)
  - System message configuration
  - Custom temperature settings (0.0-1.0)
  - Token management (max_tokens)
  - Stream support
  - Frequency and presence penalties
  - Multiple response formats

- **Image Processing**
  - High-quality image generation
  - Advanced image editing
  - Multiple AI models (Grok-2, DALL-E-3)
  - Custom dimensions
  - Seed-based reproducibility

- **Audio Processing**
  - Professional-grade Text-to-Speech
  - Accurate Speech-to-Text
  - Multiple voice options
  - Format conversion

- **Video Generation**
  - AI-powered video creation
  - Custom duration control
  - Aspect ratio options
  - Resolution settings

## Installation

Install the package using pip:

```bash
pip install alleai-sdk
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Valid AlleAI API key
- Internet connection
- `.env` file with API configuration

### Quick Setup

1. Create a `.env` file in your project root:

```env
ALLEAI_API_KEY=your_api_key_here
```

2. Initialize the client:

```python
from alleai.core import AlleAIClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("ALLEAI_API_KEY")

# Initialize client
client = AlleAIClient(api_key=api_key)

# Chat completion example
chat = client.chat.completions({
    "models": ["gpt-4o", "o4-mini", "claude-3-sonnet"],
    "messages": [
        {
            "system": [
                {
                    "type": "text",
                    "text": "You are a helpful assistant."
                }
            ]
        },
        {
            "user": [
                {
                    "type": "text",
                    "text": "tell me about photosynthesis?"
                }
            ]
        }
    ],
    "temperature": 0.7,      # Controls randomness (0.0 to 1.0)
    "max_tokens": 2000,      # Maximum response length
    "top_p": 1,              # Controls diversity
    "frequency_penalty": 0.2, # Penalizes repeated tokens
    "presence_penalty": 0.3,  # Penalizes new tokens
    "stream": False          # Enable streaming responses
})
print(chat)

# Generate an image
image_response = client.image.generate({
    "models": ["grok-2-image", "dall-e-3"],
    "prompt": "futuristic city, flying cars, robotic pedestrians.",
    "model_specific_params": {
        "grok-2-image": {
            "n": 1,
            "height": 1024,
            "width": 1024
        }
    },
    "n": 1,
    "height": 1024,
    "width": 1024,
    "seed": 8  # For reproducible results
})

# Convert text to speech
tts_response = client.audio.tts({
    "models": ["elevenlabs-multilingual-v2", "gpt-4o-mini-tts"],
    "prompt": "Hello! You're listening to a test of a text-to-speech model...",
    "voice": "nova",
    "model_specific_params": {
        "gpt-4o-mini-tts": {
            "voice": "alternative-voice"
        }
    }
})

# Transcribe audio
stt_response = client.audio.stt({
    "models": ["whisper-v3"],
    "audio_file": "path/to/your/audio.mp3"
})
```

## Documentation

### Image Generation

```python
# Generate an image
response = client.image.generate({
    "models": ["nova-canvas"],
    "prompt": "Your creative prompt here",
    "model_specific_params": {
        "nova-canvas": {
            "n": 1,
            "height": 1024,
            "width": 1024
        }
    },
    "seed": 42  # Optional: for reproducible results
})

# Edit an existing image
response = client.image.edit({
    "models": ["nova-canvas"],
    "image_file": "path/to/image.jpg",
    "prompt": "Replace the sky with a sunset"
})
```

### Audio Processing

```python
# Text to Speech
response = client.audio.tts({
    "models": ["gpt-4o-mini-tts"],
    "prompt": "Text to convert to speech",
    "voice": "nova"
})

# Speech to Text
response = client.audio.stt({
    "models": ["whisper-v3"],
    "audio_file": "path/to/audio.mp3"
})

# Generate Audio
response = client.audio.generate({
    "models": ["lyria"],
    "prompt": "Create a relaxing ambient track"
})
```

## Video Generation

```python
# Generate a video
video = client.video.generate({
    "models": ["nova-reel"],
    "prompt": "robotic arm assembling a car in a futuristic factory",
    "duration": 6,           # Video length in seconds
    "loop": False,           # Enable looping
    "aspect_ratio": "16:9",  # Video aspect ratio
    "fps": 24,              # Frames per second
    "dimension": "1280x720", # Video dimensions
    "resolution": "720p",    # Output resolution
    "seed": 8               # For reproducible results
})
print(video)
```

## Video Status Check

```python
# Check video generation status
response = client.video.get_video_status({
    "requestId": "your-request-id"
})
print(response)
```

## Error Handling

The SDK includes comprehensive error handling:

```python
from alleai.core.exceptions import InvalidRequestError

try:
    response = client.image.generate({
        "models": ["nova-canvas"],
        "prompt": "Your prompt here"
    })
except InvalidRequestError as e:
    print(f"Error: {e.message}")
    print(f"Error Code: {e.code}")
```

## Requirements

- Python 3.8 or higher
- `requests` library (automatically installed with the package)

## Best Practices

1. **Environment Variables**
   - Always use `.env` file for API keys
   - Never hardcode sensitive information

2. **Error Handling**
   - Implement proper error handling
   - Log errors appropriately
   - Handle rate limits gracefully

3. **Resource Management**
   - Close connections when done
   - Handle timeouts
   - Implement retry logic

## Support

For support, please:
- Check our [documentation](https://github.com/pYGOD3512/alle-ai-sdk-python/blob/main/docs)
- Open an issue in our [GitHub repository](https://github.com/pYGOD3512/alle-ai-sdk-python/issues)
- Contact our support team at support@alle.ai

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

If you discover any security vulnerabilities, please contact us immediately at security@alle.ai.

