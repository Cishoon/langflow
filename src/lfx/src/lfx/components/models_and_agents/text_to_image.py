from __future__ import annotations

import base64
from typing import Any

import httpx
from pydantic.v1 import SecretStr

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DropdownInput, IntInput, MessageInput, MessageTextInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message

DEFAULT_IMAGE_MODEL = "qwen-image-plus"
DEFAULT_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
DEFAULT_SEED = 1


class TextToImageComponent(Component):
    display_name = "Text to Image"
    description = "Generate an image from text using OpenAI-compatible image APIs."
    icon = "Image"
    name = "TextToImage"

    inputs = [
        MessageTextInput(
            name="prompt",
            display_name="Prompt",
            info="Text prompt to generate the image.",
            required=True,
        ),
        MessageInput(
            name="prompt_message",
            display_name="Prompt Message",
            info="Optional upstream message or data containing the prompt.",
            input_types=["Message", "Data"],
            advanced=True,
            required=False,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="OpenAI or OpenAI-compatible API key.",
            required=True,
        ),
        StrInput(
            name="endpoint",
            display_name="Generation Endpoint URL",
            info="Full endpoint for image generation. Example (DashScope): "
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            value=DEFAULT_ENDPOINT,
            required=True,
        ),
        StrInput(
            name="model_name",
            display_name="Model",
            info="Image generation model to use.",
            value=DEFAULT_IMAGE_MODEL,
            required=True,
        ),
        DropdownInput(
            name="size",
            display_name="Size",
            info="Allowed resolutions (DashScope examples): 1024*1024, 1024*1792, 1792*1024, "
            "1664*928, 928*1664, 1472*1104, 1104*1472, 1328*1328.",
            options=[
                "1024*1024",
                "1024*1792",
                "1792*1024",
                "1664*928",
                "928*1664",
                "1472*1104",
                "1104*1472",
                "1328*1328",
            ],
            value="1024*1024",
            required=True,
        ),
        StrInput(
            name="style",
            display_name="Style",
            info="Style hint (e.g., vivid/natural for OpenAI, or leave blank).",
            advanced=True,
        ),
        MessageTextInput(
            name="negative_prompt",
            display_name="Negative Prompt",
            info="Undesired content description (DashScope parameters.negative_prompt).",
            advanced=True,
        ),
        BoolInput(
            name="prompt_extend",
            display_name="Prompt Extend",
            info="Enable prompt optimization (DashScope parameters.prompt_extend).",
            value=True,
            advanced=True,
        ),
        BoolInput(
            name="watermark",
            display_name="Watermark",
            info="Enable watermark (DashScope parameters.watermark).",
            value=False,
            advanced=True,
        ),
        IntInput(
            name="seed",
            display_name="Seed",
            info="Optional seed for deterministic generations.",
            value=DEFAULT_SEED,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Generated Image", name="image_output", method="generate_image"),
    ]

    def _get_api_key(self) -> str:
        if not self.api_key:
            msg = "API key is required for Text to Image."
            raise ValueError(msg)
        if isinstance(self.api_key, SecretStr):
            return self.api_key.get_secret_value()
        return str(self.api_key)

    def _get_endpoint(self) -> str:
        if self.endpoint:
            return str(self.endpoint)
        return DEFAULT_ENDPOINT

    def _get_model_name(self) -> str:
        if getattr(self, "model_name", None):
            return str(self.model_name)
        return DEFAULT_IMAGE_MODEL

    def _get_prompt(self) -> str:
        if getattr(self, "prompt", None):
            return str(self.prompt)

        if getattr(self, "prompt_message", None):
            prompt_message = self.prompt_message
            if isinstance(prompt_message, Message) and prompt_message.text:
                return str(prompt_message.text)
            if isinstance(prompt_message, Data):
                text_value = prompt_message.get_text()
                if text_value:
                    return str(text_value)
            if isinstance(prompt_message, dict):
                text_value = prompt_message.get("text") or prompt_message.get("prompt")
                if text_value:
                    return str(text_value)
            if isinstance(prompt_message, str):
                return prompt_message

        msg = "Prompt is required. Please provide a prompt or connect a Prompt Message."
        raise ValueError(msg)

    async def generate_image(self) -> Message:
        prompt = self._get_prompt()
        api_key = self._get_api_key()
        endpoint = self._get_endpoint()
        model_name = self._get_model_name()
        request_preview = {
            "endpoint": endpoint,
            "model": model_name,
            "size": getattr(self, "size", None),
            "style": getattr(self, "style", None),
            "seed": getattr(self, "seed", None),
            "prompt_extend": getattr(self, "prompt_extend", None),
            "watermark": getattr(self, "watermark", None),
        }

        payload: dict[str, Any] = {
            "model": model_name,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}],
                    }
                ]
            },
            "parameters": {},
        }

        parameters: dict[str, Any] = {}
        if self.size:
            parameters["size"] = self.size
        if self.style:
            parameters["style"] = self.style
        if self.seed is not None:
            parameters["seed"] = self.seed
        if self.negative_prompt:
            parameters["negative_prompt"] = self.negative_prompt
        if self.prompt_extend is not None:
            parameters["prompt_extend"] = self.prompt_extend
        if self.watermark is not None:
            parameters["watermark"] = self.watermark

        if parameters:
            payload["parameters"] = parameters
        else:
            payload.pop("parameters", None)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response else "unknown"
            body = e.response.text if e.response is not None else "no response body"
            msg = (
                f"Image generation request failed: status={status}; "
                f"endpoint={request_preview['endpoint']}; "
                f"model={request_preview['model']}; "
                f"response={body[:500]}"
            )
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Image generation request failed: {e} | request={request_preview}"
            raise RuntimeError(msg) from e

        result = response.json()
        data_list = result.get("data") or []
        image_entry: dict[str, Any] = {}

        image_bytes: bytes | None = None
        image_url: str | None = None

        output = result.get("output") or {}
        choices = output.get("choices") or []
        if choices:
            content_blocks = choices[0].get("message", {}).get("content", []) or []
            for block in content_blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("url"):
                    image_url = block["url"]
                    break
                if "image" in block and isinstance(block["image"], dict) and block["image"].get("url"):
                    image_url = block["image"]["url"]
                    break
                if block.get("image") and isinstance(block["image"], str):
                    # Some providers return direct URL under "image"
                    image_url = block["image"]
                    break
                if block.get("b64_json"):
                    image_bytes = base64.b64decode(block["b64_json"])

        # Fallback to OpenAI-style data list
        if image_bytes is None and image_url is None and data_list:
            image_entry = data_list[0] or {}
            if image_entry.get("b64_json"):
                image_bytes = base64.b64decode(image_entry["b64_json"])
            elif image_entry.get("url"):
                image_url = image_entry["url"]

        # Prefer remote URL directly; fallback to data URI built from base64
        files: list[str] = []
        display_text: str | None = None

        if image_url:
            # Fix URL encoding issue: '+' in query params (e.g., Signature) must be encoded as %2B
            # Otherwise browsers interpret '+' as space, causing signature mismatch errors
            if "?" in image_url:
                base, query = image_url.split("?", 1)
                # Encode '+' in query string to prevent it being interpreted as space
                query = query.replace("+", "%2B")
                image_url = f"{base}?{query}"
            files.append(image_url)
            display_text = image_url

        if not files and image_bytes:
            data_uri = f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            files.append(data_uri)
            display_text = data_uri

        if not files:
            msg = "Image generation returned empty image content."
            raise RuntimeError(msg)

        message = await Message.create(
            text=display_text or files[0],
            files=files,
        )
        message.properties.icon = "Image"
        message.category = "message"
        message.data["image_path"] = files[0]
        if image_url:
            message.data["remote_url"] = image_url

        self.status = f"Generated image url={image_url or 'data-uri'}"
        return message
