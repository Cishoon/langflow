from lfx.base.io.chat import ChatComponent
from lfx.io import FileInput, MessageTextInput, Output
from lfx.schema.message import Message

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


class AudioInput(ChatComponent):
    display_name = "Audio Input"
    description = "Get audio file inputs for speech-to-text processing."
    icon = "Mic"
    name = "AudioInput"
    minimized = True

    inputs = [
        FileInput(
            name="audio_file",
            display_name="Audio File",
            file_types=AUDIO_FILE_TYPES,
            info="Audio file to be processed (mp3, wav, flac, m4a, ogg, etc.)",
            required=True,
            temp_file=True,
        ),
        MessageTextInput(
            name="audio_url",
            display_name="Audio URL",
            info="URL of the audio file (alternative to uploading a file)",
            advanced=True,
        ),
        MessageTextInput(
            name="session_id",
            display_name="Session ID",
            info="The session ID for tracking. If empty, the current session ID will be used.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Audio Message", name="audio_message", method="audio_response"),
    ]

    async def audio_response(self) -> Message:
        """Output a Message containing the audio file path."""
        # Determine audio source
        audio_path = None
        if self.audio_file:
            audio_path = self.audio_file
        elif self.audio_url:
            audio_path = self.audio_url

        if not audio_path:
            msg = "Either an audio file or audio URL must be provided"
            raise ValueError(msg)

        session_id = self.session_id or (self.graph.session_id if hasattr(self, "graph") and self.graph else "")

        # Create message with audio file
        message = await Message.create(
            text="",  # No text content, just audio
            session_id=session_id,
            files=[audio_path] if audio_path else [],
        )

        self.status = f"Audio loaded: {audio_path}"
        return message
