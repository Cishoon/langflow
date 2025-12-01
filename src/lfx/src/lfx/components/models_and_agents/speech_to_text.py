from pathlib import Path

from pydantic.v1 import SecretStr

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DropdownInput, FileInput, MessageInput, Output, SecretStrInput, StrInput
from lfx.schema.message import Message

# Qwen ASR models
QWEN_ASR_MODELS = [
    "qwen3-asr-flash",
]

# DashScope API base URL
DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/api/v1"

# Supported audio file types
AUDIO_FILE_TYPES = [
    "mp3",
    "wav",
    "flac",
    "m4a",
    "ogg",
    "aac",
    "wma",
    "opus",
    "webm",
    "amr",
]


class SpeechToTextComponent(Component):
    display_name = "Speech to Text"
    description = "Convert audio to text using speech recognition models."
    icon = "AudioLines"
    name = "SpeechToText"

    inputs = [
        DropdownInput(
            name="provider",
            display_name="Provider",
            options=["Qwen"],
            value="Qwen",
            info="Select the speech recognition provider",
            real_time_refresh=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            options=QWEN_ASR_MODELS,
            value="qwen3-asr-flash",
            info="Select the ASR model to use",
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="DashScope API Key for Qwen ASR",
            required=True,
        ),
        MessageInput(
            name="audio_input",
            display_name="Audio Input",
            info="Audio message from AudioInput component",
            input_types=["Message"],
        ),
        FileInput(
            name="audio_file",
            display_name="Audio File",
            file_types=AUDIO_FILE_TYPES,
            info="Direct audio file input (alternative to Audio Input)",
            advanced=True,
            temp_file=True,
        ),
        StrInput(
            name="audio_url",
            display_name="Audio URL",
            info="URL of the audio file (alternative to file upload)",
            advanced=True,
        ),
        StrInput(
            name="language",
            display_name="Language",
            info="Language code (e.g., 'zh', 'en'). Leave empty for auto-detection.",
            advanced=True,
        ),
        BoolInput(
            name="enable_itn",
            display_name="Enable ITN",
            info="Enable Inverse Text Normalization (convert numbers, dates to written form)",
            value=False,
            advanced=True,
        ),
        StrInput(
            name="api_base",
            display_name="API Base URL",
            info="Base URL for DashScope API",
            value=DASHSCOPE_API_BASE,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Transcribed Text", name="text_output", method="transcribe"),
    ]

    def _get_audio_path(self) -> str:
        """Get audio file path from various input sources."""
        # Priority: audio_input (Message) > audio_file > audio_url
        if self.audio_input:
            if isinstance(self.audio_input, Message):
                files = self.audio_input.files or []
                if files:
                    return files[0] if isinstance(files[0], str) else str(files[0])
            elif isinstance(self.audio_input, str):
                return self.audio_input

        if self.audio_file:
            return self.audio_file

        if self.audio_url:
            return self.audio_url

        msg = "No audio input provided. Please provide audio via AudioInput, file upload, or URL."
        raise ValueError(msg)

    async def transcribe(self) -> Message:
        """Transcribe audio to text using the selected provider."""
        if self.provider == "Qwen":
            return await self._transcribe_qwen()
        msg = f"Unknown provider: {self.provider}"
        raise ValueError(msg)

    async def _transcribe_qwen(self) -> Message:
        """Transcribe audio using Qwen ASR via DashScope."""
        try:
            import dashscope
        except ImportError as e:
            msg = "dashscope not installed. Please install with `uv pip install dashscope`"
            raise ImportError(msg) from e

        # Set API base URL
        dashscope.base_http_api_url = self.api_base or DASHSCOPE_API_BASE

        # Get audio path
        audio_path = self._get_audio_path()

        # Format audio path for DashScope
        # Local files need file:// prefix, URLs are used as-is
        if audio_path.startswith(("http://", "https://")):
            audio_uri = audio_path
        else:
            # Verify file exists
            if not Path(audio_path).exists():
                msg = f"Audio file not found: {audio_path}"
                raise FileNotFoundError(msg)
            # Use absolute path with file:// prefix
            audio_uri = f"file://{Path(audio_path).absolute()}"

        # Build messages for MultiModalConversation
        messages = [
            {"role": "system", "content": [{"text": ""}]},
            {"role": "user", "content": [{"audio": audio_uri}]},
        ]

        # Build ASR options
        asr_options = {
            "enable_itn": self.enable_itn,
        }
        if self.language:
            asr_options["language"] = self.language

        # Get API key
        api_key = None
        if self.api_key:
            if isinstance(self.api_key, SecretStr):
                api_key = self.api_key.get_secret_value()
            else:
                api_key = str(self.api_key)

        if not api_key:
            msg = "API key is required for Qwen ASR"
            raise ValueError(msg)

        try:
            response = dashscope.MultiModalConversation.call(
                api_key=api_key,
                model=self.model_name,
                messages=messages,
                result_format="message",
                asr_options=asr_options,
            )
        except Exception as e:
            msg = f"Error calling Qwen ASR API: {e}"
            raise RuntimeError(msg) from e

        # Parse response
        if hasattr(response, "output") and response.output:
            choices = response.output.get("choices", [])
            if choices:
                message_content = choices[0].get("message", {}).get("content", [])
                if message_content:
                    transcribed_text = message_content[0].get("text", "")

                    # Get additional info from annotations
                    annotations = choices[0].get("message", {}).get("annotations", [])
                    language_detected = None
                    emotion = None
                    for ann in annotations:
                        if ann.get("type") == "audio_info":
                            language_detected = ann.get("language")
                            emotion = ann.get("emotion")

                    # Build status message
                    status_parts = [f"Transcribed: {len(transcribed_text)} chars"]
                    if language_detected:
                        status_parts.append(f"Language: {language_detected}")
                    if emotion:
                        status_parts.append(f"Emotion: {emotion}")
                    self.status = " | ".join(status_parts)

                    return Message(text=transcribed_text)

        # Handle error response
        if hasattr(response, "code") and response.code:
            msg = f"Qwen ASR error: {response.code} - {getattr(response, 'message', 'Unknown error')}"
            raise RuntimeError(msg)

        msg = "Failed to get transcription from Qwen ASR response"
        raise RuntimeError(msg)
