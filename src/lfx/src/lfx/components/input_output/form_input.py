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
from lfx.schema.message import Message
from lfx.utils.constants import (
    MESSAGE_SENDER_NAME_USER,
    MESSAGE_SENDER_USER,
)


class FormInput(ChatComponent):
    """Form Input component that allows developers to create structured form inputs.

    This component enables workflow developers to define multiple labeled input fields
    that users can fill in through the Playground interface, instead of a single text input.
    Each form field generates its own output that can be connected independently.
    """

    display_name = "Form Input"
    description = "Get structured form inputs from the Playground with multiple labeled fields. Each field has its own output."
    documentation: str = "https://docs.langflow.org/form-input"
    icon = "ClipboardList"
    name = "FormInput"
    minimized = True

    inputs = [
        TableInput(
            name="form_fields",
            display_name="Form Fields",
            info="Define the form fields. Each row should have 'label' (field name shown to user), "
            "'name' (internal field identifier), 'type' (text/number/textarea/select), "
            "and optionally 'placeholder', 'required', 'options' (for select type, comma-separated).",
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
                {"name": "label", "display_name": "Label", "type": "str", "description": "Field label shown to user"},
                {"name": "name", "display_name": "Field Name", "type": "str", "description": "Internal field identifier"},
                {
                    "name": "type",
                    "display_name": "Type",
                    "type": "str",
                    "description": "Field type: text, number, textarea, select",
                },
                {"name": "placeholder", "display_name": "Placeholder", "type": "str", "description": "Placeholder text"},
                {"name": "required", "display_name": "Required", "type": "bool", "description": "Is field required"},
                {
                    "name": "options",
                    "display_name": "Options",
                    "type": "str",
                    "description": "For select type: comma-separated options",
                },
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
            info="Type of sender.",
            advanced=True,
        ),
        MessageTextInput(
            name="sender_name",
            display_name="Sender Name",
            info="Name of the sender.",
            value=MESSAGE_SENDER_NAME_USER,
            advanced=True,
        ),
        MessageTextInput(
            name="session_id",
            display_name="Session ID",
            info="The session ID of the chat. If empty, the current session ID parameter will be used.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="All Fields", name="all_fields", method="all_fields_response"),
    ]

    def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Dynamically update build config when form_fields changes."""
        if field_name == "form_fields" and field_value:
            # Remove old dynamic fields (those starting with "field_")
            keys_to_remove = [k for k in build_config if k.startswith("field_")]
            for key in keys_to_remove:
                del build_config[key]

            # Add new dynamic fields based on form_fields configuration
            for idx, field in enumerate(field_value):
                field_internal_name = field.get("name", f"field_{idx}")
                field_label = field.get("label", field_internal_name)
                field_type = field.get("type", "text")
                field_placeholder = field.get("placeholder", "")
                field_required = field.get("required", False)
                field_options = field.get("options", "")

                # Create the appropriate input type based on field type
                field_key = f"field_{field_internal_name}"

                if field_type == "select" and field_options:
                    options_list = [opt.strip() for opt in field_options.split(",") if opt.strip()]
                    build_config[field_key] = {
                        "display_name": field_label,
                        "info": f"{'Required. ' if field_required else ''}{field_placeholder}",
                        "type": "str",
                        "options": options_list,
                        "value": options_list[0] if options_list else "",
                        "required": field_required,
                        "show": True,
                        "input_types": ["Message"],
                    }
                elif field_type == "textarea":
                    build_config[field_key] = {
                        "display_name": field_label,
                        "info": f"{'Required. ' if field_required else ''}{field_placeholder}",
                        "type": "str",
                        "multiline": True,
                        "value": "",
                        "required": field_required,
                        "show": True,
                        "input_types": ["Message"],
                    }
                else:  # text or number
                    build_config[field_key] = {
                        "display_name": field_label,
                        "info": f"{'Required. ' if field_required else ''}{field_placeholder}",
                        "type": "str" if field_type != "number" else "int",
                        "value": "" if field_type != "number" else 0,
                        "required": field_required,
                        "show": True,
                        "input_types": ["Message"] if field_type != "number" else [],
                    }

        return build_config

    def update_outputs(self, frontend_node: dict, field_name: str, field_value: Any) -> dict:
        """Dynamically update outputs when form_fields changes."""
        if field_name == "form_fields" and field_value:
            # Start with the base output
            new_outputs = [
                Output(display_name="All Fields", name="all_fields", method="all_fields_response"),
            ]

            # Add an output for each form field
            for field in field_value:
                field_internal_name = field.get("name", "")
                field_label = field.get("label", field_internal_name)
                if field_internal_name:
                    output_name = f"output_{field_internal_name}"
                    new_outputs.append(
                        Output(
                            display_name=field_label,
                            name=output_name,
                            method="get_field_value",
                        )
                    )

            frontend_node["outputs"] = new_outputs

        return frontend_node

    def _get_form_values(self) -> dict[str, str]:
        """Extract form field values from the component's dynamic attributes."""
        form_values = {}
        for field in self.form_fields:
            field_name = field.get("name", "")
            field_key = f"field_{field_name}"
            if field_name and hasattr(self, field_key):
                value = getattr(self, field_key, "")
                # Handle Message type inputs
                if hasattr(value, "text"):
                    value = value.text
                elif hasattr(value, "data"):
                    value = data_to_text("{text}", value)
                form_values[field_name] = str(value) if value else ""
        return form_values

    def _get_single_field_value(self, field_name: str) -> str:
        """Get the value of a single form field."""
        field_key = f"field_{field_name}"
        if hasattr(self, field_key):
            value = getattr(self, field_key, "")
            if hasattr(value, "text"):
                value = value.text
            elif hasattr(value, "data"):
                value = data_to_text("{text}", value)
            return str(value) if value else ""
        return ""

    async def get_field_value(self) -> Message:
        """Return the value of a specific form field based on the output being called."""
        # Get the output name that was called
        output_name = self.selected_output or ""

        # Extract field name from output name (output_fieldname -> fieldname)
        field_name = output_name.replace("output_", "", 1) if output_name.startswith("output_") else ""

        # Get the field value
        value = self._get_single_field_value(field_name)

        # Find the field label
        field_label = field_name
        for field in self.form_fields:
            if field.get("name") == field_name:
                field_label = field.get("label", field_name)
                break

        session_id = self.session_id or self.graph.session_id or ""
        message = await Message.create(
            text=value,
            sender=self.sender,
            sender_name=self.sender_name,
            session_id=session_id,
            properties={"field_name": field_name, "field_label": field_label},
        )

        self.status = message
        return message

    async def all_fields_response(self) -> Message:
        """Return all form data as a structured message."""
        form_values = self._get_form_values()

        # Build a formatted text representation
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
            properties={"form_data": form_values, "form_fields": self.form_fields},
        )

        if session_id and isinstance(message, Message) and self.should_store_message:
            stored_message = await self.send_message(message)
            self.all_fields.value = stored_message
            message = stored_message

        self.status = message
        return message
