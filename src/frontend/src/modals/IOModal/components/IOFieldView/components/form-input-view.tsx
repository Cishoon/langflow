import { cloneDeep } from "lodash";
import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import useFlowStore from "@/stores/flowStore";
import type { AllNodeType } from "@/types/flow";

interface FormField {
  label: string;
  name: string;
  type: "text" | "number" | "textarea" | "select";
  placeholder?: string;
  required?: boolean;
  options?: string;
}

interface FormInputViewProps {
  nodeId: string;
  onSubmit?: (values: Record<string, string>) => void;
  isBuilding?: boolean;
}

export default function FormInputView({
  nodeId,
  onSubmit,
  isBuilding = false,
}: FormInputViewProps) {
  const nodes = useFlowStore((state) => state.nodes);
  const setNode = useFlowStore((state) => state.setNode);

  const node: AllNodeType | undefined = nodes.find((n) => n.id === nodeId);
  const [formValues, setFormValues] = useState<Record<string, string>>({});

  // Get form fields from node template
  const formFields: FormField[] =
    node?.data?.node?.template?.form_fields?.value || [];

  // Initialize form values from node template (dynamic fields)
  useEffect(() => {
    const initialValues: Record<string, string> = {};
    formFields.forEach((field) => {
      const fieldKey = `field_${field.name}`;
      const templateField = node?.data?.node?.template?.[fieldKey];
      initialValues[field.name] = templateField?.value?.toString() || "";
    });
    setFormValues(initialValues);
  }, [nodeId, JSON.stringify(formFields)]);

  const handleFieldChange = (fieldName: string, value: string) => {
    setFormValues((prev) => ({ ...prev, [fieldName]: value }));

    // Update node template
    if (node) {
      const newNode = cloneDeep(node);
      const fieldKey = `field_${fieldName}`;
      if (newNode.data.node?.template && newNode.data.node.template[fieldKey]) {
        newNode.data.node.template[fieldKey].value = value;
        setNode(node.id, newNode);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.(formValues);
  };

  const renderField = (field: FormField) => {
    const value = formValues[field.name] || "";

    switch (field.type) {
      case "textarea":
        return (
          <Textarea
            id={`form-field-${field.name}`}
            placeholder={field.placeholder || ""}
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            className="min-h-[80px] resize-y"
            disabled={isBuilding}
          />
        );

      case "number":
        return (
          <Input
            id={`form-field-${field.name}`}
            type="number"
            placeholder={field.placeholder || ""}
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            disabled={isBuilding}
          />
        );

      case "select": {
        const options = (field.options || "")
          .split(",")
          .map((opt) => opt.trim())
          .filter(Boolean);
        return (
          <Select
            value={value}
            onValueChange={(val) => handleFieldChange(field.name, val)}
            disabled={isBuilding}
          >
            <SelectTrigger id={`form-field-${field.name}`}>
              <SelectValue placeholder={field.placeholder || "Select..."} />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
      }

      case "text":
      default:
        return (
          <Input
            id={`form-field-${field.name}`}
            type="text"
            placeholder={field.placeholder || ""}
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            disabled={isBuilding}
          />
        );
    }
  };

  if (formFields.length === 0) {
    return (
      <div className="flex items-center justify-center p-4 text-muted-foreground">
        No form fields defined. Configure the Form Input component to add
        fields.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-4">
      {formFields.map((field) => (
        <div key={field.name} className="flex flex-col gap-2">
          <Label htmlFor={`form-field-${field.name}`} className="text-sm">
            {field.label}
            {field.required && <span className="ml-1 text-destructive">*</span>}
          </Label>
          {renderField(field)}
        </div>
      ))}
    </form>
  );
}
