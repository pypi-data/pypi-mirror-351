from typing import Any

from .computed import Computed, Promise
from .datapoint import TableColumnValue  # noqa: TC002
from .txscript import TxScriptAnnotationContent  # noqa: TC002


class Reasoning(Computed):
    context: list

    def __init__(self, schema_id: str, context: list) -> None:
        self.schema_id = schema_id
        self.context = context

        self._context_fields = [
            context_item.split(".")[-1] for context_item in context if context_item.split(".")[0] == "field"
        ]
        self.dependencies = set(self._context_fields)
        self.targets = set()

    def _resolve_context_dependencies(self, t: TxScriptAnnotationContent) -> list[str]:
        result = []
        for dep in self._context_fields:
            field = t.field.__getattr__(dep)
            if isinstance(field, TableColumnValue):
                result.append(f"field {dep}: {t.field.__getattr__(dep).all_values}")
            else:
                result.append(f"field {dep}: {t.field.__getattr__(dep)}")

        return result

    def evaluate(self, t: TxScriptAnnotationContent) -> Any | Promise:
        field = t.field.__getattr__(self.schema_id)

        return Promise(
            type="reasoning",
            context={
                "field_schema_id": self.schema_id,
                "field_output_type": field.attr.type,
                "description": getattr(field.attr, "prompt", ""),
                "relevant_fields": self._resolve_context_dependencies(t),
                "field_details": {
                    **({"Queue Name": t.queue.name if t.queue else None} if "queue.name" in self.context else {}),
                    **(
                        {"Workspace Name": t.workspace.name if t.workspace else None}
                        if "workspace.name" in self.context
                        else {}
                    ),
                    **({"Field label": getattr(field.attr, "label", "")} if "self.attr.label" in self.context else {}),
                    **(
                        {"Field description": getattr(field.attr, "description", "")}
                        if "self.attr.description" in self.context
                        else {}
                    ),
                },
                **({"enum_options": str(options)} if (options := getattr(field.attr, "options", "")) else {}),
            },
            id=field.attr.id,
        )
