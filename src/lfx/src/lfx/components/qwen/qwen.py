import requests
from pydantic.v1 import SecretStr
from typing_extensions import override

from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import BoolInput, DictInput, DropdownInput, IntInput, SecretStrInput, SliderInput, StrInput

# Qwen model list - https://help.aliyun.com/zh/model-studio/getting-started/models
QWEN_MODELS = ["qwen-plus", "qwen3-max", "qwen-flash"]

# Default API base for Qwen (DashScope OpenAI-compatible endpoint)
QWEN_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class QwenModelComponent(LCModelComponent):
    display_name = "Qwen"
    description = "Generate text using Alibaba Qwen (通义千问) LLMs via DashScope API."
    icon = "Qwen"
    name = "QwenModel"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            info="Maximum number of tokens to generate. Set to 0 for unlimited.",
            range_spec=RangeSpec(min=0, max=128000),
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
            info="Additional keyword arguments to pass to the model.",
        ),
        BoolInput(
            name="json_mode",
            display_name="JSON Mode",
            advanced=True,
            info="If True, it will output JSON regardless of passing a schema.",
        ),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            info="Qwen model to use. See https://help.aliyun.com/zh/model-studio/getting-started/models",
            options=QWEN_MODELS,
            value="qwen-plus",
            refresh_button=True,
            combobox=True,
        ),
        StrInput(
            name="api_base",
            display_name="Qwen API Base",
            advanced=True,
            info="Base URL for API requests. Defaults to DashScope OpenAI-compatible endpoint.",
            value=QWEN_API_BASE,
        ),
        SecretStrInput(
            name="api_key",
            display_name="Qwen API Key",
            info="The DashScope API Key for Qwen. Get it from https://dashscope.console.aliyun.com/",
            advanced=False,
            required=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            info="Controls randomness in responses. Higher values make output more random.",
            value=0.7,
            range_spec=RangeSpec(min=0, max=2, step=0.01),
            advanced=True,
        ),
        SliderInput(
            name="top_p",
            display_name="Top P",
            info="Nucleus sampling parameter. Controls diversity of output.",
            value=0.8,
            range_spec=RangeSpec(min=0, max=1, step=0.01),
            advanced=True,
        ),
        IntInput(
            name="seed",
            display_name="Seed",
            info="The seed controls the reproducibility of the job.",
            advanced=True,
            value=1,
        ),
    ]

    def get_models(self) -> list[str]:
        """Fetch available models from DashScope API."""
        if not self.api_key:
            return QWEN_MODELS

        url = f"{self.api_base}/models"
        api_key_value = (
            SecretStr(self.api_key).get_secret_value() if isinstance(self.api_key, SecretStr) else str(self.api_key)
        )
        headers = {"Authorization": f"Bearer {api_key_value}", "Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            model_list = response.json()
            models = [model["id"] for model in model_list.get("data", [])]
            # Filter to only include qwen models and return default list if empty
            qwen_models = [m for m in models if "qwen" in m.lower()]
            if not qwen_models:
                return QWEN_MODELS
        except requests.RequestException as e:
            self.status = f"Error fetching models: {e}"
            return QWEN_MODELS
        else:
            return qwen_models

    @override
    def update_build_config(self, build_config: dict, field_value: str, field_name: str | None = None):
        if field_name in {"api_key", "api_base", "model_name"}:
            models = self.get_models()
            build_config["model_name"]["options"] = models
        return build_config

    def build_model(self) -> LanguageModel:
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            msg = "langchain-openai not installed. Please install with `pip install langchain-openai`"
            raise ImportError(msg) from e

        api_key_value = None
        if self.api_key:
            if isinstance(self.api_key, SecretStr):
                api_key_value = self.api_key.get_secret_value()
            else:
                api_key_value = str(self.api_key)

        model_kwargs = self.model_kwargs or {}
        # Add top_p to model_kwargs if set
        if hasattr(self, "top_p") and self.top_p is not None:
            model_kwargs["top_p"] = self.top_p

        output = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature if self.temperature is not None else 0.7,
            max_tokens=self.max_tokens or None,
            model_kwargs=model_kwargs,
            base_url=self.api_base or QWEN_API_BASE,
            api_key=api_key_value,
            streaming=self.stream if hasattr(self, "stream") else False,
            seed=self.seed,
        )

        if self.json_mode:
            output = output.bind(response_format={"type": "json_object"})

        return output

    def _get_exception_message(self, e: Exception):
        """Get message from Qwen API exception."""
        try:
            from openai import BadRequestError

            if isinstance(e, BadRequestError):
                message = e.body.get("message")
                if message:
                    return message
        except ImportError:
            pass
        return None
