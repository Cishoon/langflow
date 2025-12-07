from lfx.base.io.image import ImageComponent
from lfx.io import MessageTextInput, Output
from lfx.schema.message import Message


class ImageInput(ImageComponent):
    display_name = "Image Input"
    description = "Upload an image (or URL) and pass it into the flow."
    icon = "Image"
    name = "ImageInput"
    minimized = True

    inputs = [
        MessageTextInput(
            name="image_url",
            display_name="Image URL",
            info="Optional URL instead of uploading a file.",
            required=True,
            advanced=True,
        ),
        MessageTextInput(
            name="session_id",
            display_name="Session ID",
            info="Optional session id. If empty, the current session id will be used.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Image Message", name="image_message", method="image_response"),
    ]

    async def image_response(self) -> Message:
        img_path = None
        if self.image_url:
            img_path = self.image_url

        if not img_path:
            msg = "Provide an image file or image URL"
            raise ValueError(msg)

        session_id = self.session_id or self.graph.session_id if hasattr(self, "graph") else ""

        message = await Message.create(
            text="Image input",
            files=[img_path],
            session_id=session_id,
        )

        self.status = f"ImageInput files=1 path={img_path}"
        return message
