from __future__ import annotations

from typing import Any

import httpx
from pydantic.v1 import SecretStr

from lfx.custom.custom_component.component import Component
from lfx.io import DropdownInput, MessageInput, MessageTextInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message

DEFAULT_TTS_MODEL = "qwen3-tts-flash"
DEFAULT_VOICE = "Cherry"
DEFAULT_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
DEFAULT_LANGUAGE = "Chinese"


class TextToSpeechComponent(Component):
    display_name = "Text to Speech"
    description = "Convert text to spoken audio using DashScope/Qwen TTS."
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
            info="DashScope API key.",
            required=True,
        ),
        StrInput(
            name="endpoint",
            display_name="Endpoint",
            info="Full endpoint for DashScope TTS.",
            value=DEFAULT_ENDPOINT,
        ),
        StrInput(
            name="model_name",
            display_name="Model",
            info="TTS model to use.",
            value=DEFAULT_TTS_MODEL,
        ),
        DropdownInput(
            name="voice",
            display_name="Voice",
            options=["Cherry", "Bob", "Tony", "Lily", "Jack"],
            value=DEFAULT_VOICE,
            info="Voice to use for synthesis.",
        ),
        StrInput(
            name="language_type",
            display_name="Language",
            info="Language type, e.g., Chinese / English.",
            value=DEFAULT_LANGUAGE,
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

    async def synthesize(self) -> Message:
        text = self._get_text()
        api_key = self._get_api_key()
        model_name = self.model_name or DEFAULT_TTS_MODEL
        voice = self.voice or DEFAULT_VOICE
        language = self.language_type or DEFAULT_LANGUAGE
        endpoint = self.endpoint or DEFAULT_ENDPOINT

        payload: dict[str, Any] = {
            "model": model_name,
            "input": {
                "text": text,
                "voice": voice,
                "language_type": language,
            },
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response else "unknown"
            body = e.response.text if e.response is not None else "no response body"
            msg = f"Text-to-speech request failed: status={status}; response={body[:500]}"
            raise RuntimeError(msg) from e
        except Exception as e:  # noqa: BLE001
            msg = f"Text-to-speech request failed: {e}"
            raise RuntimeError(msg) from e

        result = response.json()
        audio_url = (
            result.get("output", {}).get("audio", {}).get("url")
            if isinstance(result, dict)
            else None
        )
        audio_data_b64 = (
            result.get("output", {}).get("audio", {}).get("data")
            if isinstance(result, dict)
            else None
        )

        files: list[str] = []
        display_text: str | None = None

        if audio_url:
            files.append(audio_url)
            display_text = audio_url
        elif audio_data_b64:
            data_uri = f"data:audio/wav;base64,{audio_data_b64}"
            files.append(data_uri)
            display_text = data_uri
        else:
            msg = "Text-to-speech succeeded but returned no audio URL or data."
            raise RuntimeError(msg)

        message = await Message.create(
            text=display_text or text,
            files=files,
        )
        message.properties.icon = "AudioWaveform"
        message.category = "message"
        message.data["audio_url"] = files[0]

        self.status = f"Generated audio {files[0]}"
        return message
