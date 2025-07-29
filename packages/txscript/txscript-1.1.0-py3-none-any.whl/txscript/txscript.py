from __future__ import annotations

import abc
from html import escape
from typing import Any, List, Optional

from .annotation import Annotation
from .datapoint import FieldValueBase, TableColumnValue  # noqa: TC002
from .exceptions import PayloadError
from .fields import Fields
from .flatdata import FieldsFlatData


class TxScriptBase(abc.ABC):
    pass


class Queue:
    def __init__(self, url: str, name: str) -> None:
        self.url = url
        self.name = name


class Workspace:
    def __init__(self, url: str, name: str) -> None:
        self.url = url
        self.name = name


class TxScriptAnnotationContent(TxScriptBase):
    """
    This class encapsulates the annotation_content event Rossum TxScript execution context.

    Its attributes (including methods) are available as globals in formula code.
    """

    field: Fields
    annotation: Optional[Annotation]
    updated_datapoint_ids: list[int]
    recompute_all: bool

    _computed_ids: set[int]
    _exceptions: List[dict]
    _messages: List[dict]
    _automation_blockers: List[dict]
    _actions: List[dict]
    _promises: List[dict]

    def __init__(
        self,
        field: Fields,
        annotation: Optional[Annotation] = None,
        updated_dp_ids: Optional[list[int]] = None,
        force_update_datapoint_ids: Optional[list[int]] = None,
        queue: Optional[Queue] = None,
        workspace: Optional[Workspace] = None,
    ) -> None:
        self.field = field
        self.annotation = annotation
        self.updated_datapoint_ids = updated_dp_ids if updated_dp_ids else []
        self.force_update_datapoint_ids = force_update_datapoint_ids if force_update_datapoint_ids else []
        self.recompute_all = not bool(updated_dp_ids)
        self.queue = queue
        self.workspace = workspace

        self._computed_ids = set()
        self._exceptions = []
        self._messages = []
        self._automation_blockers = []
        self._actions = []
        self._promises = []

    @staticmethod
    def from_payload(payload: dict) -> TxScriptAnnotationContent:
        try:
            schema_content = payload["schemas"][0]["content"]
        except KeyError:
            raise PayloadError("Schema sideloading must be enabled!") from None

        field = Fields(FieldsFlatData.from_tree(schema_content, payload["annotation"]["content"]))

        annotation = (
            Annotation(payload["annotation"], payload.get("rossum_authorization_token", None))
            if "status" in payload["annotation"]
            else None
        )
        queue = Queue(payload.get("queue"), payload.get("queue_name")) if payload.get("queue_name") else None  # type:ignore[arg-type]
        workspace = (
            Workspace(payload.get("workspace"), payload.get("workspace_name"))  # type:ignore[arg-type]
            if payload.get("workspace_name")
            else None
        )

        updated_datapoint_ids = payload.get("updated_datapoint_ids")
        force_update_datapoint_ids = payload.get("force_update_datapoint_ids")
        return TxScriptAnnotationContent(
            field, annotation, updated_datapoint_ids, force_update_datapoint_ids, queue, workspace
        )

    def _with_field(self, field: Fields) -> TxScriptAnnotationContent:
        t = TxScriptAnnotationContent(
            field,
            self.annotation,
            self.updated_datapoint_ids,
            self.force_update_datapoint_ids,
            self.queue,
            self.workspace,
        )
        t._computed_ids = self._computed_ids
        t._exceptions = self._exceptions
        t._messages = self._messages
        t._automation_blockers = self._automation_blockers
        t._actions = self._actions
        t._promises = self._promises
        return t

    @staticmethod
    def _create_exception_message(exc: dict) -> dict:
        tb = []
        for frame in exc["traceback"]:
            tb.append(f"  at line {frame['lineno']}{f', in {frame["loc"]}' if 'loc' in frame else ''}:")
            tb.append(f"    {frame['code']}")
        content = f"{exc['content']}\n\n{'\n'.join(['Traceback (most recent call last):', *tb])}"
        return {
            "id": exc["id"],
            "type": "error",
            "content": escape(content).replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;"),
            "detail": {"is_exception": True, "traceback_line_number": exc["lineno"]},
        }

    def hook_response(self, separate_exceptions: bool = False) -> dict:
        res = {
            "automation_blockers": self._automation_blockers,
            "messages": self._messages,
            "operations": self.field._get_operations(),
            "exceptions": self._exceptions,
            "actions": self._actions,
            "computed_ids": list(self._computed_ids),
            "promises": self._promises,
        }
        if not separate_exceptions:
            exception_messages = [self._create_exception_message(e) for e in self._exceptions]
            res["messages"] = self._messages + exception_messages
            del res["exceptions"]
        return res

    def _formula_methods(self) -> dict:
        return {
            "show_error": self.show_error,
            "show_warning": self.show_warning,
            "show_info": self.show_info,
            "automation_blocker": self.automation_blocker,
        }

    def show_error(self, content: str, field: Optional[FieldValueBase] = None, **json: Any) -> None:
        if field is not None and not isinstance(field, TableColumnValue):
            # column is not represented with a single datapoint that would have id
            json = dict(**json, id=field.id)
        self._message(type="error", content=content, **json)

    def show_warning(self, content: str, field: Optional[FieldValueBase] = None, **json: Any) -> None:
        if field is not None and not isinstance(field, TableColumnValue):
            # column is not represented with a single datapoint that would have id
            json = dict(**json, id=field.id)
        self._message(type="warning", content=content, **json)

    def show_info(self, content: str, field: Optional[FieldValueBase] = None, **json: Any) -> None:
        if field is not None and not isinstance(field, TableColumnValue):
            # column is not represented with a single datapoint that would have id
            json = dict(**json, id=field.id)
        self._message(type="info", content=content, **json)

    def automation_blocker(self, content: str, field: Optional[FieldValueBase] = None, **json: Any) -> None:
        if field is not None and not isinstance(field, TableColumnValue):
            # column is not represented with a single datapoint that would have id
            json = dict(**json, id=field.id)
        self._automation_blocker(content=content, **json)

    def _message(self, **json: Any) -> None:
        json["source_id"] = self.field.__dict__["_field_id"]
        schema_id = json.pop("schema_id", None)
        if schema_id:
            json["id"] = self.field.__getattr__(schema_id).attr.id
        self._messages.append(json)

    def _exception(self, content: str, lineno: int, traceback: list[dict], **json: Any) -> None:
        json["source_id"] = self.field.__dict__["_field_id"]
        schema_id = json.pop("schema_id", None)
        if schema_id:
            json["id"] = self.field.__getattr__(schema_id).attr.id
        self._exceptions.append(
            {
                "content": content,
                "traceback": traceback,
                "lineno": lineno,
                **json,
            }
        )

    def _automation_blocker(self, **json: Any) -> None:
        json["source_id"] = self.field.__dict__["_field_id"]
        schema_id = json.pop("schema_id", None)
        if schema_id:
            json["id"] = self.field.__getattr__(schema_id).attr.id
        self._automation_blockers.append(json)

    def _action(self, action_type: str, detail: dict, **json: Any) -> None:
        schema_id = json.pop("schema_id", None)
        if schema_id:
            json["id"] = self.field.__getattr__(schema_id).attr.id
        self._actions.append({"type": action_type, "payload": json, "detail": detail})

    def _promise(self, schema_id: str, **json: Any) -> None:
        json["id"] = self.field.__getattr__(schema_id).attr.id
        json["schema_id"] = schema_id
        self._promises.append(json)


class TxScript:
    @staticmethod
    def from_payload(payload: dict) -> TxScriptBase:
        if payload["event"] == "annotation_content":
            return TxScriptAnnotationContent.from_payload(payload)
        else:
            raise ValueError(f"Event not supported by TxScript: {payload['event']}")
