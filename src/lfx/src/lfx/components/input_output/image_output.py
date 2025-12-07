from __future__ import annotations

from typing import Any

from lfx.base.io.image import ImageComponent
from lfx.inputs import HandleInput
from lfx.schema.message import Message
from lfx.template.field.base import Output


class ImageOutput(ImageComponent):
    display_name = "Image Output"
    description = "Display images or image URLs in the Playground."
    icon = "Image"
    name = "ImageOutput"
    minimized = True

    inputs = [
        HandleInput(
            name="input_value",
            display_name="Inputs",
            info="Message containing image files or URLs.",
            input_types=["Message"],
            required=True,
        )
    ]

    outputs = [
        Output(
            display_name="Image Message",
            name="message",
            method="image_response",
        ),
    ]

    @staticmethod
    def _looks_like_image_url(value: str) -> bool:
        lowered = value.lower()
        return lowered.startswith(("http://", "https://")) and any(
            lowered.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]
        )

    async def image_response(self) -> Message:
        value: Any = self.input_value
        message: Message | None = None

        # Normalize into a Message and ensure files array exists
        if isinstance(value, Message):
            message = value
        else:
            msg = f"Unsupported input type for ImageOutput: {type(value).__name__}"
            raise TypeError(msg)

        message.flow_id = self.graph.flow_id if hasattr(self, "graph") else None

        if message.files is None:
            message.files = []

        if message.files and message.text in {"Image input", "Image generated"}:
            message.text = str(message.files[0])

        # Brief status to help debugging wiring
        self.status = f"ImageOutput files={len(message.files)} text={message.text}"
        return message
