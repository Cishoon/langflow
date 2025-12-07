from __future__ import annotations

import tempfile
from typing import Any
from uuid import uuid4

import httpx
from pydantic.v1 import SecretStr

from lfx.custom.custom_component.component import Component
from lfx.io import DropdownInput, MessageInput, MessageTextInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message
from lfx.services.deps import get_storage_service

DEFAULT_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "alloy"
DEFAULT_API_BASE = "https://api.openai.com/v1"

AUDIO_FORMATS = ["mp3", "wav", "flac"]


class TextToSpeechComponent(Component):
    display_name = "Text to Speech"
    description = "Convert text to spoken audio using OpenAI-compatible TTS APIs."
    icon = "AudioWaveform"
    name = "TextToSpeech"

    inputs = [
        MessageTextInput(
            name="text",
            display_name="Text",
            info="Plain text to convert to speech. If empty, will use Message Input text.",
        ),
        MessageInput(
            name="message_input",
            display_name="Message Input",
            info="Upstream message or data containing text.",
            input_types=["Message", "Data"],
            advanced=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="OpenAI or OpenAI-compatible API key.",
            required=True,
        ),
        StrInput(
            name="api_base",
            display_name="API Base URL",
            info="Override the API base URL for OpenAI-compatible providers.",
            value=DEFAULT_API_BASE,
            advanced=True,
        ),
        StrInput(
            name="model_name",
            display_name="Model",
            info="TTS model to use.",
            value=DEFAULT_TTS_MODEL,
            advanced=True,
        ),
        DropdownInput(
            name="voice",
            display_name="Voice",
            options=["alloy", "shimmer", "verse"],
            value=DEFAULT_VOICE,
            info="Voice to use for synthesis.",
        ),
        DropdownInput(
            name="audio_format",
            display_name="Audio Format",
            options=AUDIO_FORMATS,
            value="mp3",
            info="Output audio format.",
        ),
    ]

    outputs = [
        Output(display_name="Speech Audio", name="audio_output", method="synthesize"),
    ]

    def _get_api_key(self) -> str:
        if not self.api_key:
            msg = "API key is required for Text to Speech."
            raise ValueError(msg)
        if isinstance(self.api_key, SecretStr):
            return self.api_key.get_secret_value()
        return str(self.api_key)

    def _get_text(self) -> str:
        if getattr(self, "text", None):
            return str(self.text)

        if getattr(self, "message_input", None):
            message_input = self.message_input
            if isinstance(message_input, Message) and message_input.text:
                return str(message_input.text)
            if isinstance(message_input, Data):
                text_value = message_input.get_text()
                if text_value:
                    return str(text_value)
            if isinstance(message_input, dict):
                text_value = message_input.get("text")
                if text_value:
                    return str(text_value)
            if isinstance(message_input, str):
                return message_input

        msg = "No text provided. Please set Text or connect a Message Input."
        raise ValueError(msg)

    async def _persist_bytes(self, data: bytes, *, suffix: str) -> tuple[str, str]:
        """Save bytes to storage service if available; fallback to temp file.

        Returns:
            logical_path: Path stored on storage service (or temp path)
            absolute_path: Resolved filesystem path
        """
        storage_service = get_storage_service()
        flow_id = str(getattr(self.graph, "flow_id", "") or "default")
        file_name = f"tts-{uuid4().hex}{suffix}"

        if storage_service:
            await storage_service.save_file(flow_id, file_name, data)
            logical_path = f"{flow_id}/{file_name}"
            resolved_path = storage_service.resolve_component_path(logical_path)
            return logical_path, resolved_path

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(data)
            tmp_path = tmp_file.name
        return tmp_path, tmp_path

    async def synthesize(self) -> Message:
        text = self._get_text()
        api_key = self._get_api_key()
        api_base = (self.api_base or DEFAULT_API_BASE).rstrip("/")
        model_name = self.model_name or DEFAULT_TTS_MODEL
        audio_format = self.audio_format or "mp3"
        voice = self.voice or DEFAULT_VOICE

        url = f"{api_base}/audio/speech"
        payload: dict[str, Any] = {
            "model": model_name,
            "input": text,
            "voice": voice,
            "response_format": audio_format,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response else "unknown"
            body = e.response.text if e.response is not None else "no response body"
            msg = f"Text-to-speech request failed: status={status}; response={body[:500]}"
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Text-to-speech request failed: {e}"
            raise RuntimeError(msg) from e

        audio_bytes = response.content
        if not audio_bytes:
            msg = "Text-to-speech succeeded but returned empty audio."
            raise RuntimeError(msg)

        logical_path, resolved_path = await self._persist_bytes(audio_bytes, suffix=f".{audio_format}")

        message = await Message.create(
            text=text,
            files=[logical_path],
        )
        message.properties.icon = "AudioWaveform"
        message.category = "message"

        self.status = f"Generated audio at {resolved_path}"
        return message
