from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generator, Optional, Set

if TYPE_CHECKING:
    from .datapoint import Field, FieldValueBase
    from .flatdata import FieldsFlatData


def datapoint_diff(dp: dict, dp_new: dict) -> set[str]:
    """
    Return a set of changed attributes that can be signalled in replacement
    operations.
    """
    replacements = set()

    old_value = dp["content"].get("normalized_value")
    if old_value is None:
        old_value = dp["content"].get("value")
    if "value" in dp_new["content"] and dp_new["content"]["value"] != old_value:
        replacements.add("content.value")

    for content_key in ("position", "page"):
        if content_key in dp_new["content"] and dp["content"].get(content_key) != dp_new["content"].get(content_key):
            replacements.add("content." + content_key)

    for key in ("validation_sources", "hidden", "options"):
        if key in dp_new and dp.get(key) != dp_new.get(key):
            replacements.add(key)

    return replacements


@dataclass
class FieldUpdate:
    dp: dict
    remove: bool = False
    replace: set = field(default_factory=set)


class FieldUpdates:
    """
    [INTERNAL] Tracker of field changes that is used for the construction of
    operations to return in hook response.
    """

    updates_by_field: dict

    def __init__(self) -> None:
        self.updates_by_field = {}

    def _get_update_by_dp(self, dp: dict) -> FieldUpdate:
        dp_id = dp.get("id", id(dp))
        if dp_id not in self.updates_by_field:
            self.updates_by_field[dp_id] = FieldUpdate(dp)
        return self.updates_by_field[dp_id]

    def update_dp(self, dp: dict, new_attrs: dict) -> Set[str]:
        replacements = datapoint_diff(dp, new_attrs)
        if replacements:
            self.replace_attrs(dp, replacements)
        return replacements

    def replace_attrs(self, dp: dict, attrnames: Set[str]) -> None:
        self._get_update_by_dp(dp).replace |= attrnames

    def add(self, dp: dict) -> None:
        self._get_update_by_dp(dp)

    def remove(self, dp: dict) -> None:
        if "id" in dp:
            self._get_update_by_dp(dp).remove = True
        else:
            dp_id = dp.get("id", id(dp))
            del self.updates_by_field[dp_id]

    def replace_dp(self, dp_old: dict, dp_new: dict) -> None:
        replacements = datapoint_diff(dp_old, dp_new)

        dp_old_id = dp_old.get("id", id(dp_old))
        if dp_old_id in self.updates_by_field:
            assert not self.updates_by_field[dp_old_id].remove
            replacements |= self.updates_by_field[dp_old_id].replace
            del self.updates_by_field[dp_old_id]

        if replacements:
            self._get_update_by_dp(dp_new).replace = replacements

    def get_operations(self, data: FieldsFlatData) -> Generator[dict, None, None]:
        def _dp_op_value(dp: dict, key_filter: Optional[Callable[[str], bool]] = None) -> dict:
            if key_filter is None:
                key_filter = lambda k: True  # noqa: E731
            return {
                "content": {
                    k: v
                    for k, v in dp["content"].items()
                    if k in ("value", "position", "page") and key_filter("content." + k)
                }
            } | {k: v for k, v in dp.items() if k in ("validation_sources", "hidden", "options") and key_filter(k)}

        for _, dp_updates in self.updates_by_field.items():
            dp = dp_updates.dp

            if "id" not in dp:
                schema_node = data.schema[dp["schema_id"]]
                if data.schema[schema_node["parent"]]["category"] == "multivalue":
                    dp_multivalue = data.objects[schema_node["parent"]]
                    if schema_node["category"] == "tuple":
                        yield {
                            "op": "add",
                            "id": dp_multivalue["id"],
                            "value": [
                                _dp_op_value(data.objects[column]["all_objects"][dp["_content_index"]])
                                | {"schema_id": column}
                                for column in schema_node["children"]
                                if data.schema[column].get("ui_configuration", {}).get("type") != "formula"
                            ],
                        }
                    else:
                        yield {
                            "op": "add",
                            "id": dp_multivalue["id"],
                            "value": _dp_op_value(dp),
                        }
                else:
                    assert data.schema[schema_node["parent"]]["category"] == "tuple"
            elif dp_updates.remove:
                yield {"op": "remove", "id": dp["id"]}
            else:
                op_value = _dp_op_value(dp, lambda k: k in dp_updates.replace)  # noqa: B023
                if not op_value["content"]:
                    # (only attribute changes such as .hidden)
                    del op_value["content"]
                yield {"op": "replace", "id": dp["id"], "value": op_value}


class FieldContextMixin:
    def __init__(self) -> None:
        self._field_id: int
        self.__dict__["_field_id"] = -1

    @contextmanager
    def _field_context(self, field: Field) -> Generator[None, None, None]:
        """Used for message/automation_blocker field source_id reference tracking."""
        self.__dict__["_field_id"] = field.attrs["id"]
        try:
            yield
        finally:
            self.__dict__["_field_id"] = -1


class Fields(FieldContextMixin):
    """
    [USER FACING] The `field` object implementation.

    It is backed by the FieldsFlatData data store, triggers lazy instantiation
    of DatapointValue*, and keeps track of changes in FieldUpdates.
    """

    def __init__(
        self,
        data: FieldsFlatData,
    ) -> None:
        super().__init__()
        self._data: FieldsFlatData
        self._field_cache: dict[str, Field]
        self._updates: FieldUpdates
        self.__dict__["_data"] = data
        self.__dict__["_field_cache"] = {}
        self.__dict__["_updates"] = FieldUpdates()

    @contextmanager
    def _readonly_context(self) -> Generator[None, None, None]:
        """Evaluate within this context with updates restricted."""
        _updates = self._updates
        self.__dict__["_updates"] = None
        try:
            yield
        finally:
            self.__dict__["_updates"] = _updates

    def _get_field(self, attrname: str) -> Field:
        from .datapoint import Field

        if attrname not in self._field_cache:
            self._field_cache[attrname] = Field.from_data(attrname, self)

        return self._field_cache[attrname]

    def __getattr__(self, attrname: str) -> FieldValueBase:
        return self._get_field(attrname).get_value()

    def __setattr__(self, attrname: str, value: Any) -> None:
        if not self._updates:
            raise TypeError("Field formulas must not modify values of other fields")
        self._get_field(attrname).set_value(value)

    def _get_operations(self) -> list[dict]:
        return list(self._updates.get_operations(self._data))
