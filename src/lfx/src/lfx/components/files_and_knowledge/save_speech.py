from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, HandleInput, MessageTextInput, Output, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message
from lfx.services.deps import get_storage_service


class SaveSpeechComponent(Component):
    display_name = "Save Speech"
    description = "Save an audio file from a Message, Data, or URL/path into storage or a local directory."
    icon = "AudioWaveform"
    name = "SaveSpeech"

    inputs = [
        HandleInput(
            name="audio_input",
            display_name="Audio Input",
            info="Message/Data/string containing the audio URL or path.",
            input_types=["Message", "Data", "str"],
            required=True,
        ),
        StrInput(
            name="file_name",
            display_name="File Name",
            info="File name to save as (e.g., output.wav).",
            required=True,
        ),
        BoolInput(
            name="overwrite",
            display_name="Overwrite",
            info="Overwrite if the file already exists.",
            value=True,
            advanced=True,
        ),
        StrInput(
            name="local_dir",
            display_name="Local Directory",
            info="Optional directory to save locally (absolute or relative). If empty, uses Langflow storage service.",
            advanced=True,
        ),
        MessageTextInput(
            name="session_id",
            display_name="Session ID",
            info="Optional session id for the output Message.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Saved Audio", name="saved_audio", method="save_speech"),
    ]

    @staticmethod
    def _extract_path_or_url(value: Any) -> str:
        if isinstance(value, Message):
            files = value.files or []
            if files:
                return files[0] if isinstance(files[0], str) else getattr(files[0], "path", "")
            if value.text:
                return str(value.text)
        if isinstance(value, Data):
            data_obj = value.data if hasattr(value, "data") else {}
            audio_path = data_obj.get("audio_url") or data_obj.get("audio_path")
            if audio_path:
                return str(audio_path)
            text_value = value.get_text()
            if text_value:
                return str(text_value)
        if isinstance(value, str):
            return value
        msg = f"Unsupported input type for SaveSpeech: {type(value).__name__}"
        raise TypeError(msg)

    @staticmethod
    def _is_url(path: str) -> bool:
        return path.startswith(("http://", "https://"))

    async def _download_bytes(self, url: str) -> bytes:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
        resp.raise_for_status()
        return resp.content

    def _load_local_bytes(self, path: str) -> bytes:
        file_path = Path(path)
        if not file_path.exists():
            msg = f"Audio file not found: {path}"
            raise FileNotFoundError(msg)
        return file_path.read_bytes()

    async def save_speech(self) -> Message:
        source = self._extract_path_or_url(self.audio_input)
        if not source:
            msg = "No audio path or URL provided."
            raise ValueError(msg)

        data_bytes = await self._download_bytes(source) if self._is_url(source) else self._load_local_bytes(source)

        storage_service = get_storage_service()
        flow_id = str(getattr(self.graph, "flow_id", "") or "default")
        file_name = self.file_name

        logical_path = file_name
        resolved_path = file_name

        if self.local_dir:
            # Normalize common full-width tilde to a real home shortcut
            normalized_dir = self.local_dir.replace("～", "~").strip()
            base_dir = Path(normalized_dir).expanduser().resolve()
            base_dir.mkdir(parents=True, exist_ok=True)
            target_path = base_dir / file_name
            if target_path.exists() and not self.overwrite:
                msg = f"File {target_path} already exists and overwrite is disabled."
                raise FileExistsError(msg)
            target_path.write_bytes(data_bytes)
            logical_path = str(target_path)
            resolved_path = str(target_path)
        elif storage_service:
            if not self.overwrite:
                existing = await storage_service.list_files(flow_id)
                if file_name in existing:
                    msg = f"File {file_name} already exists in flow {flow_id} and overwrite is disabled."
                    raise FileExistsError(msg)

            await storage_service.save_file(flow_id, file_name, data_bytes, append=False)
            logical_path = f"{flow_id}/{file_name}"
            resolved_path = storage_service.resolve_component_path(logical_path)

        message = await Message.create(
            text=logical_path,
            files=[logical_path],
            session_id=self.session_id or getattr(self.graph, "session_id", ""),
        )
        message.properties.icon = "AudioWaveform"
        message.category = "message"
        message.data["audio_path"] = logical_path
        message.data["resolved_path"] = resolved_path
        if self._is_url(source):
            message.data["source_url"] = source

        self.status = f"Saved audio to {resolved_path}"
        return message
