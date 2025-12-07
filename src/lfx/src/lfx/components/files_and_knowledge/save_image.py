from pathlib import Path
from typing import Any

import requests

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, HandleInput, MessageTextInput, Output, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message
from lfx.services.deps import get_storage_service


class SaveImageComponent(Component):
    display_name = "Save Image"
    description = "Save an image from a Message, Data, or URL/path into the configured storage or a local directory."
    icon = "Image"
    name = "SaveImage"

    inputs = [
        HandleInput(
            name="image_input",
            display_name="Image Input",
            info="Message/Data/string containing the image path or URL.",
            input_types=["Message", "Data", "str"],
            required=True,
        ),
        StrInput(
            name="file_name",
            display_name="File Name",
            info="File name to save as (including extension, e.g., output.png).",
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
        Output(display_name="Saved Image", name="saved_image", method="save_image"),
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
            # Try data dict
            file_path = value.data.get("image_path") if hasattr(value, "data") else None
            if file_path:
                return str(file_path)
            if value.get_text():
                return str(value.get_text())
        if isinstance(value, str):
            return value
        msg = f"Unsupported input type for SaveImage: {type(value).__name__}"
        raise TypeError(msg)

    @staticmethod
    def _is_url(path: str) -> bool:
        return path.startswith(("http://", "https://"))

    def _load_bytes(self, path_or_url: str) -> bytes:
        if self._is_url(path_or_url):
            resp = requests.get(path_or_url, timeout=30)
            resp.raise_for_status()
            return resp.content

        file_path = Path(path_or_url)
        if not file_path.exists():
            msg = f"Image file not found: {path_or_url}"
            raise FileNotFoundError(msg)
        return file_path.read_bytes()

    async def save_image(self) -> Message:
        source = self._extract_path_or_url(self.image_input)
        if not source:
            msg = "No image path or URL provided."
            raise ValueError(msg)

        data_bytes = self._load_bytes(source)
        storage_service = get_storage_service()
        flow_id = str(getattr(self.graph, "flow_id", "") or "default")
        file_name = self.file_name

        logical_path = file_name
        resolved_path = file_name

        if self.local_dir:
            base_dir = Path(self.local_dir).expanduser().resolve()
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
        message.properties.icon = "Image"
        message.category = "message"
        message.data["image_path"] = logical_path
        message.data["resolved_path"] = resolved_path
        if self._is_url(source):
            message.data["source_url"] = source

        self.status = f"Saved image to {logical_path}"
        return message
