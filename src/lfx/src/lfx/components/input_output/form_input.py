"""Form Input component for structured user inputs in the Playground."""

from typing import Any

from lfx.base.io.chat import ChatComponent
from lfx.helpers.data import data_to_text
from lfx.inputs.inputs import BoolInput, TableInput
from lfx.io import (
    DropdownInput,
    MessageTextInput,
    Output,
)
from lfx.schema.data import Data
from lfx.schema.message import Message
from lfx.utils.constants import (
    MESSAGE_SENDER_NAME_USER,
    MESSAGE_SENDER_USER,
)


class FormInput(ChatComponent):
    """Form Input component that allows developers to create structured form inputs.

    This component enables workflow developers to define multiple labeled input fields
    that users can fill in through the Playground interface, instead of a single text input.
    Outputs a Data object containing all field values that can be accessed by field name.
    """

    display_name = "Form Input"
    description = "Get structured form inputs from the Playground. Outputs a Data object with all field values."
    documentation: str = "https://docs.langflow.org/form-input"
    icon = "ClipboardList"
    name = "FormInput"
    minimized = True

    inputs = [
        TableInput(
            name="form_fields",
            display_name="Form Fields",
            info="Define the form fields. Each row needs 'label' and 'name'. "
            "Optional: 'type' (text/number/textarea/select), 'placeholder', 'required', 'options' (comma-separated for select).",
            value=[
                {
                    "label": "Search Query",
                    "name": "query",
                    "type": "text",
                    "placeholder": "Enter your search query...",
                    "required": True,
                    "options": "",
                },
            ],
            table_schema=[
                {"name": "label", "display_name": "Label", "type": "str"},
                {"name": "name", "display_name": "Field Name", "type": "str"},
                {"name": "type", "display_name": "Type", "type": "str"},
                {"name": "placeholder", "display_name": "Placeholder", "type": "str"},
                {"name": "required", "display_name": "Required", "type": "bool"},
                {"name": "options", "display_name": "Options", "type": "str"},
            ],
            real_time_refresh=True,
        ),
        BoolInput(
            name="should_store_message",
            display_name="Store Messages",
            info="Store the message in the history.",
            value=True,
            advanced=True,
        ),
        DropdownInput(
            name="sender",
            display_name="Sender Type",
            options=["Machine", MESSAGE_SENDER_USER],
            value=MESSAGE_SENDER_USER,
            advanced=True,
        ),
        MessageTextInput(
            name="sender_name",
            display_name="Sender Name",
            value=MESSAGE_SENDER_NAME_USER,
            advanced=True,
        ),
        MessageTextInput(
            name="session_id",
            display_name="Session ID",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Form Data", name="form_data", method="get_form_data"),
        Output(display_name="Message", name="message", method="get_message"),
    ]

    def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Dynamically create input fields based on form_fields configuration."""
        if field_name == "form_fields" and field_value:
            # Remove old dynamic fields
            keys_to_remove = [k for k in build_config if k.startswith("field_")]
            for key in keys_to_remove:
                del build_config[key]

            # Add new dynamic fields
            for field in field_value:
                field_internal_name = field.get("name", "")
                if not field_internal_name:
                    continue

                field_label = field.get("label", field_internal_name)
                field_type = field.get("type", "text")
                field_placeholder = field.get("placeholder", "")
                field_required = field.get("required", False)
                field_options = field.get("options", "")
                field_key = f"field_{field_internal_name}"

                base_config = {
                    "display_name": field_label,
                    "info": field_placeholder,
                    "required": field_required,
                    "show": True,
                    "input_types": ["Message"],
                }

                if field_type == "select" and field_options:
                    options_list = [opt.strip() for opt in field_options.split(",") if opt.strip()]
                    build_config[field_key] = {
                        **base_config,
                        "type": "str",
                        "options": options_list,
                        "value": options_list[0] if options_list else "",
                    }
                elif field_type == "textarea":
                    build_config[field_key] = {**base_config, "type": "str", "multiline": True, "value": ""}
                elif field_type == "number":
                    build_config[field_key] = {**base_config, "type": "int", "value": 0, "input_types": []}
                else:
                    build_config[field_key] = {**base_config, "type": "str", "value": ""}

        return build_config

    def _get_form_values(self) -> dict[str, Any]:
        """Extract all form field values."""
        form_values = {}
        for field in self.form_fields:
            field_name = field.get("name", "")
            field_key = f"field_{field_name}"
            if field_name and hasattr(self, field_key):
                value = getattr(self, field_key, "")
                if hasattr(value, "text"):
                    value = value.text
                elif hasattr(value, "data"):
                    value = data_to_text("{text}", value)
                form_values[field_name] = str(value) if value else ""
        return form_values

    def get_form_data(self) -> Data:
        """Return form data as a Data object with all field values accessible by name."""
        form_values = self._get_form_values()
        data = Data(data=form_values)
        self.status = data
        return data

    async def get_message(self) -> Message:
        """Return form data as a formatted Message for chat display."""
        form_values = self._get_form_values()

        # Format as "Label: Value" lines
        text_parts = []
        for field in self.form_fields:
            label = field.get("label", field.get("name", ""))
            name = field.get("name", "")
            value = form_values.get(name, "")
            text_parts.append(f"{label}: {value}")

        text = "\n".join(text_parts)
        session_id = self.session_id or self.graph.session_id or ""

        message = await Message.create(
            text=text,
            sender=self.sender,
            sender_name=self.sender_name,
            session_id=session_id,
            properties={"form_data": form_values},
        )

        if session_id and self.should_store_message:
            message = await self.send_message(message)

        self.status = message
        return message
