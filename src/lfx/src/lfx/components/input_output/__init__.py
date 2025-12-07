from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lfx.components._importing import import_mod

if TYPE_CHECKING:
    from lfx.components.input_output.audio import AudioInput
    from lfx.components.input_output.chat import ChatInput
    from lfx.components.input_output.chat_output import ChatOutput
    from lfx.components.input_output.image_input import ImageInput
    from lfx.components.input_output.image_output import ImageOutput
    from lfx.components.input_output.text import TextInputComponent
    from lfx.components.input_output.text_output import TextOutputComponent
    from lfx.components.input_output.webhook import WebhookComponent

_dynamic_imports = {
    "AudioInput": "audio",
    "ChatInput": "chat",
    "ChatOutput": "chat_output",
    "ImageInput": "image_input",
    "ImageOutput": "image_output",
    "TextInputComponent": "text",
    "TextOutputComponent": "text_output",
    "WebhookComponent": "webhook",
}

__all__ = [
    "AudioInput",
    "ChatInput",
    "ChatOutput",
    "ImageInput",
    "ImageOutput",
    "TextInputComponent",
    "TextOutputComponent",
    "WebhookComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import input/output components on attribute access."""
    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)
    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
