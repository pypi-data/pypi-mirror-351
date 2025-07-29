from __future__ import annotations

import abc
import collections
import dataclasses
import datetime
import json
import math
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property, wraps
from typing import TYPE_CHECKING, Any, Generator, Iterable, List, NoReturn, Optional, SupportsIndex, cast, overload

from .builtins import default_to, is_empty
from .fields import FieldContextMixin

if TYPE_CHECKING:
    from .fields import Fields
    from .txscript import TxScriptAnnotationContent


# Patch JSONEncoder to recognize __json__ method


def _wrapped_default(self: json.JSONEncoder, o: Any) -> Any:
    return getattr(o.__class__, "__json__", _wrapped_default.default)(o)  # type: ignore[attr-defined,misc]


_wrapped_default.default = json.JSONEncoder().default  # type: ignore[attr-defined]
json.JSONEncoder.default = _wrapped_default


def needs_updates(func: Any) -> Any:
    @wraps(func)
    def wrapper(self: Field, *args: list, **kwargs: dict) -> Any:
        if not self.field_source._updates:
            raise TypeError("Field formulas must not modify values of other fields")
        return func(self, *args, **kwargs)

    return wrapper


@dataclass
class Field(abc.ABC):
    """
    [INTERNAL] This is an internal strongly typed representation of a field
    object plus its schema and links to other fields.
    """

    schema_id: str
    _attrs: dict  # the dict pointer must never change, that'd break FieldUpdates
    field_source: Fields
    cached_value: Optional[FieldValueBase] = dataclasses.field(default=None, init=False, repr=False)
    waiting: bool = dataclasses.field(default=False, init=False, repr=False)

    def get_value(self) -> FieldValueBase:
        if self.cached_value is None:
            self.cached_value = self._get_value()
        return self.cached_value

    @abc.abstractmethod
    def _get_value(self) -> FieldValueBase:
        pass

    @abc.abstractmethod
    def set_value(self, value: Any) -> None:
        pass

    @cached_property
    def schema(self) -> dict:
        return self.field_source._data.schema[self.schema_id]

    @property
    def attrs(self) -> dict:
        return self._attrs

    @cached_property
    def parent(self) -> Optional[Field]:
        parent_schema = self.field_source._data.schema[self.schema["parent"]]
        if parent_schema["category"] == "section":
            return None
        elif parent_schema["category"] == "tuple":
            cell_index = self.field_source._get_field(self.schema_id).all_fields.index(self)  # type: ignore[attr-defined]
            return self.field_source._get_field(parent_schema["id"]).all_fields[cell_index]  # type: ignore[attr-defined]
        else:
            return self.field_source._get_field(parent_schema["id"])

    @cached_property
    def parent_multivalue(self) -> Optional[Field]:
        parent = self.parent
        if isinstance(parent, RowTupleField):
            parent = parent.parent  # need to recurse one more level up (tuple->multivalue)
        if not isinstance(parent, MultivalueField):
            raise TypeError("Field is not in a multivalue field")
        return parent

    @staticmethod
    def instance(schema_id: str, attrs: dict, field_source: Fields) -> Field:
        if "all_objects" in attrs:
            if field_source._data.schema[schema_id]["category"] == "tuple":
                return MultivalueTupleField(schema_id, attrs, field_source)
            else:
                return MultivalueDatapointField(schema_id, attrs, field_source)

        if field_source._data.schema[schema_id]["category"] == "multivalue":
            return MultivalueField(schema_id, attrs, field_source)

        return DatapointField(schema_id, attrs, field_source)

    @staticmethod
    def from_data(schema_id: str, field_source: Fields) -> Field:
        try:
            attrs = field_source._data.objects[schema_id]
        except KeyError:
            raise AttributeError(f"Field '{schema_id}' is not defined")

        return Field.instance(schema_id, attrs, field_source)


class DatapointField(Field):
    cached_value: Optional[FieldValueBase]

    def _get_value(self) -> FieldValueBase:
        assert self.schema["category"] == "datapoint"

        if "content" not in self.attrs:
            raise AttributeError(f"Field '{self.schema_id}' is not present")

        dp_type = self.schema["type"]
        if dp_type == "enum":
            dp_type = self.schema.get("enum_value_type", "string")

        dp_val = self.attrs["content"]["normalized_value"] or self.attrs["content"]["value"]

        if dp_type == "number":
            try:
                return NumberValue(float(dp_val), self)
            except Exception:  # None, conversion error, ...
                return NumberValue(None, self)
        if dp_type == "boolean":
            return BooleanValue(True if dp_val == "True" else False if dp_val == "False" else None, self)
        elif dp_type == "date":
            try:
                return DateValue(datetime.datetime.strptime(dp_val, "%Y-%m-%d").date(), self)
            except Exception:  # None, conversion error, ...
                return DateValue(None, self)
        else:
            return StringValue(dp_val or "", self)

    @needs_updates
    def set_value(self, value: Any) -> None:
        if "content" not in self.attrs:
            raise AttributeError(f"Field '{self.schema_id}' is not present")

        new_attrs = FieldValueBase._attrs_from_value(value, self)

        replacements = self.field_source._updates.update_dp(self.attrs, new_attrs)
        for replacement in replacements:
            if replacement.startswith("content."):
                replacement = replacement[8:]
                self.attrs["content"][replacement] = new_attrs["content"][replacement]
            else:
                self.attrs[replacement] = new_attrs[replacement]

        if "content.value" in replacements:
            self.attrs["content"]["normalized_value"] = new_attrs["content"]["value"]
            self.cached_value = None


@dataclass
class MultivalueIterableField(Field):
    @abc.abstractproperty
    def all_fields(self) -> List[Field]:
        pass

    @abc.abstractmethod
    def append(self, value: Any) -> None:
        pass

    @needs_updates
    def remove_slice(self, index: slice) -> None:
        for i in range(*index.indices(len(self.attrs["all_objects"]))):
            self.field_source._updates.remove(self.attrs["all_objects"][i])
        del self.attrs["all_objects"][index]
        if "all_fields" in self.__dict__:
            del self.all_fields[index]

    @abc.abstractmethod
    def index(self, all_fields: List[Field], value: Any) -> int:
        pass


@dataclass
class MultivalueField(MultivalueIterableField):
    @cached_property
    def child_field(self) -> MultivalueIterableField:
        child_schema_id = self.field_source._data.schema[self.schema_id]["child"]
        return cast("MultivalueIterableField", self.field_source._get_field(child_schema_id))

    def _get_value(self) -> Table:
        assert self.schema["category"] == "multivalue"
        return Table(self)

    def set_value(self, value: Any) -> None:
        self.child_field.set_value(value)

    @property
    def all_fields(self) -> List[Field]:
        return self.child_field.all_fields

    def append(self, value: Any) -> None:
        self.child_field.append(value)

    def index(self, all_fields: list[Field], value: Any) -> int:
        return self.child_field.index(all_fields, value)

    @needs_updates
    def remove_slice(self, index: slice) -> None:
        return self.child_field.remove_slice(index)


class MultivalueDatapointField(MultivalueIterableField):
    cached_value: Optional[TableColumnValue]

    in_tuple_size_change_error_message = (
        "Tuple columns cannot change size individually, modify the whole tuple's .all_values instead"
    )

    def _get_value(self) -> TableColumnValue:
        assert self.schema["category"] == "datapoint"
        return TableColumnValue(self)

    def set_value(self, value: Any) -> None:
        raise TypeError("Cannot assign to multivalue field; consider assigning to the .all_values property")

    @property
    def is_in_tuple(self) -> bool:
        parent_schema = self.field_source._data.schema[self.schema["parent"]]
        return parent_schema["category"] == "tuple"

    @property
    def parent(self) -> Optional[Field]:
        # A whole column's parent cannot be a tuple but the multivalue
        parent_schema = self.field_source._data.schema[self.schema["parent"]]
        if parent_schema["category"] == "tuple":
            parent_schema = self.field_source._data.schema[parent_schema["parent"]]
        assert parent_schema["category"] == "multivalue"
        return self.field_source._get_field(parent_schema["id"])

    @property
    def parent_multivalue(self) -> Optional[Field]:
        return self.parent

    @needs_updates
    def append(self, value: Any) -> None:
        if self.is_in_tuple:
            raise TypeError(self.in_tuple_size_change_error_message)

        # field.multistr.append(field.str) must create an independent
        # datapoint w/o "id" to generate an add operation.  (! Making a copy
        # here also means that field.str.hidden = True later will not affect
        # the new datapoint anymore, which may seem unpythonic, but it's
        # preferred in our world where DatapointValue isn't really treated
        # as an independent object in its own right, but just syntax sugar
        # for accessing the annotation.)
        attrs = FieldValueBase._attrs_from_value(value, self)
        dp_field = DatapointField(self.schema_id, attrs, self.field_source)
        self.field_source._updates.add(dp_field.attrs)
        self._append_column_field(dp_field)

    def _append_column_field(self, field: DatapointField) -> None:
        self.attrs["all_objects"].append(field.attrs)
        if "all_fields" in self.__dict__:
            self.all_fields.append(field)

    def remove_slice(self, index: slice) -> None:
        if self.is_in_tuple:
            raise TypeError(self.in_tuple_size_change_error_message)
        super().remove_slice(index)

    def _remove_column_slice(self, index: slice) -> None:
        del self.attrs["all_objects"][index]
        if "all_fields" in self.__dict__:
            del self.all_fields[index]

    def _replace_column_field(self, index: int, attrs_new: dict) -> None:
        attrs_old = self.attrs["all_objects"][index]

        # For the purpose of constructing operations, we need to pretend
        # that we are just modifying the original cells with new values.
        if "id" in attrs_old:
            attrs_new["id"] = attrs_old["id"]
        self.field_source._updates.replace_dp(attrs_old, attrs_new)

        self.attrs["all_objects"][index] = attrs_new
        if "all_fields" in self.__dict__:
            self.all_fields[index] = DatapointField(self.schema_id, attrs_new, self.field_source)

    def index(self, all_fields: List[DatapointField], value: Any) -> int:  # type: ignore[override]
        if isinstance(value, FieldValueBase):
            return all_fields.index(value._field)  # type: ignore[arg-type]
        else:
            return [f.get_value() for f in all_fields].index(value)

    @cached_property
    def all_fields(self) -> List[DatapointField]:  # type: ignore[override]
        return [DatapointField(self.schema_id, attrs, self.field_source) for attrs in self.attrs["all_objects"]]


class MultivalueTupleField(MultivalueIterableField):
    cached_value: Optional[TableRows]

    def _get_value(self) -> TableRows:
        assert self.schema["category"] == "tuple"
        assert "all_objects" in self.attrs
        return TableRows(self)

    def set_value(self, value: collections.abc.Collection[TableRow | dict]) -> None:
        if value == self.get_value():
            return
        if not hasattr(value, "__iter__"):
            raise TypeError("Multivalue tuple must be assigned a list or other iterable (of rows)")
        self._get_value()._replace(value)

    @needs_updates
    def append(self, value: TableRow | dict) -> None:
        # New Field() instance
        tuple_attrs = {"schema_id": self.schema_id, "_content_index": len(self.attrs["all_objects"])}
        row = RowTupleField(self.schema_id, tuple_attrs, self.field_source)

        # Append Field to all the right places
        self.field_source._updates.add(row.attrs)
        self.attrs["all_objects"].append(row.attrs)
        if "all_fields" in self.__dict__:
            self.all_fields.append(row)

        # Extend all_fields of the individual columns
        new_columns_attrs = RowTupleField.columns_attrs(value, row)
        for column_id, column_attrs in new_columns_attrs.items():
            column = self.field_source._get_field(column_id)
            column._append_column_field(DatapointField(column.schema_id, column_attrs, self.field_source))  # type: ignore[attr-defined]

    def remove_slice(self, index: slice) -> None:
        range_start = index.start or 0
        range_stop = index.stop if index.stop is not None else len(self.attrs["all_objects"])
        range_len = range_stop - range_start

        for column in self.columns:
            column._remove_column_slice(index)
        for row in self.all_fields[range_stop:]:
            row.attrs["_content_index"] -= range_len

        super().remove_slice(index)

    def index(self, all_fields: List[RowTupleField], value: TableRow) -> int:  # type:ignore[override]
        for idx, row in enumerate(all_fields):
            if row.cached_value is value:
                return idx
        raise ValueError("value not found")

    @cached_property
    def columns(self) -> List[MultivalueDatapointField]:
        return [self.field_source._get_field(column_id) for column_id in self.schema["children"]]  # type: ignore[misc]

    @cached_property
    def all_fields(self) -> List[RowTupleField]:  # type:ignore[override]
        return [RowTupleField(self.schema_id, attrs, self.field_source) for attrs in self.attrs["all_objects"]]


@dataclass
class RowTupleField(Field):
    cached_value: Optional[TableRow] = dataclasses.field(default=None, init=False, repr=False)
    field_cache: dict[str, Field] = dataclasses.field(default_factory=dict, init=False, repr=False)

    def get_field(self, attrname: str) -> Field:
        if attrname not in self.schema["children"]:
            raise AttributeError
        if attrname not in self.field_cache:
            column = self.field_source._get_field(attrname)
            self.field_cache[attrname] = column.all_fields[self.attrs["_content_index"]]  # type: ignore[attr-defined]
        return self.field_cache[attrname]

    def _get_value(self) -> TableRow:
        assert self.schema["category"] == "tuple"
        assert "all_objects" not in self.attrs
        return TableRow(self)

    @needs_updates
    def set_value(self, value: TableRow | dict) -> None:
        # We cannot overwrite the contents of the original RowTupleField e.g.
        # because of x[:2] = [x[1], x[0]] - we'd overwrite the x[0] source
        # with x[1].  Therefore, we replace the cell attrs, but are careful
        # not to disrupt the source TableRow, which we decouple from current
        # fields.

        if self.cached_value and isinstance(value, TableRow):
            if value == self.get_value():
                return
            # Replace us with a detached field snapshot
            self.cached_value._field = RowTupleField(self.schema_id, {**self.attrs}, self.field_source)
            for cell in self.cached_value._field.cells:  # fill cache
                self.cached_value._field.get_field(cell.schema_id)
            self.cached_value._field.attrs["_content_index"] = None  # force decouple
            self.cached_value._field.field_source = None  # type: ignore[assignment]
            self.cached_value = None

        new_columns_attrs = RowTupleField.columns_attrs(value, self)
        for column_id, attrs_new in new_columns_attrs.items():
            column: MultivalueDatapointField = self.field_source._get_field(column_id)  # type: ignore[assignment]
            column._replace_column_field(self.attrs["_content_index"], attrs_new)

        self.field_cache.clear()

    @cached_property
    def columns(self) -> List[MultivalueDatapointField]:
        return [self.field_source._get_field(column_id) for column_id in self.schema["children"]]  # type: ignore[misc]

    @cached_property
    def cells(self) -> List[DatapointField]:
        return [column.all_fields[self.attrs["_content_index"]] for column in self.columns]

    @staticmethod
    def columns_attrs(value: TableRow | dict, field: RowTupleField) -> dict:
        if not isinstance(value, TableRow):
            return TableRow._columns_attrs_from_value(value, field)
        else:
            if value._field.schema["children"] != field.schema["children"]:
                raise ValueError(
                    f"Attempt to set columns {value._field.schema['children']} to a tuple expecting {field.schema['children']}"
                )
            return {
                cell.schema_id: FieldValueBase._attrs_from_value(cell.get_value(), cell) for cell in value._field.cells
            }


class FieldValueBase:
    """
    Transparent container for field values that decorates them with dp attributes.

    Any field value is wrapped in the container that makes it behave
    as the value itself (e.g. print(field.strfield) will print the string value
    of the field, field.date_due - field.date_issue will produce a timedelta
    object, etc.).

    However, you can also access datapoint attributes for the fields, such as
    `field.date_due.attr.rir_confidence`.
    Moreover, this works even if date_due value is not valid and `field.date_due`
    poses as a None.

    USAGE NOTE: Any operations on this container will *lose* the datapoint metadata.
    Therefore, you SHOULD always reference the datapoint attributes only when
    directly accessing the `field` object.
      * `field.amount.attr.id` will work.
      * `x = field.amount; x.attr.id` will work, but is not recommended as confusing.
      * `x = field.amount; x += 1; x.attr.id` will not work (x is now plain float).

    IMPLEMENTATION NOTE: This is an abc that has to support both extending an
    object (in case of string) and proxying the data (in case of date).
    """

    _field: Field
    id: int  # noqa: A003

    def _attach_field(self, field: Field) -> None:
        self.__dict__["_field"] = field

    @property
    def attr(self) -> DotAttrProxy:
        return DotAttrProxy(self)

    @property
    def parent(self) -> Optional[FieldValueBase]:
        parent = self._field.parent
        return parent.get_value() if parent is not None else None

    @property
    def parent_multivalue(self) -> Optional[FieldValueBase]:
        multivalue_parent_field = self._field.parent_multivalue
        return multivalue_parent_field.get_value() if multivalue_parent_field is not None else None

    def __getattr__(self, attrname: str) -> Any:
        # Compatibility whitelist, deprecated as of 2024-09.
        if attrname in ("id", "value", "rir_confidence", "options"):
            return getattr(self.attr, attrname)
        elif getattr(self.attr, attrname, None) is not None:
            raise AttributeError(f"Consider accessing .{attrname} as .attr.{attrname}")
        else:
            raise AttributeError(attrname)

    def __setattr__(self, attrname: str, value: Any) -> Any:
        if attrname == "all_values" or attrname.startswith("_"):
            super().__setattr__(attrname, value)
        elif getattr(self.attr, attrname, None) is not None:
            raise AttributeError(f"Consider accessing .{attrname} as .attr.{attrname}")
        else:
            raise AttributeError(attrname)

    @staticmethod
    def _attrs_from_value(value: FieldValueBase | datetime.date | float | str | None, field: Field) -> dict:
        normalized_value = str(value) if not is_empty(value) else ""
        return {
            "schema_id": field.schema_id,
            "content": {"normalized_value": normalized_value, "value": normalized_value},
        }


class DotAttrProxy:
    _value: FieldValueBase
    _field: Field

    def __init__(self, value: FieldValueBase) -> None:
        self.__dict__["_value"] = value
        self.__dict__["_field"] = value._field

    def __getattr__(self, attrname: str) -> Any:
        if attrname == "options":
            if "options" not in self._field.attrs:
                self._field.attrs["options"] = [{**op} for op in self._field.schema.get("options", [])]
            return EnumOptionList(self._field.attrs["options"], self._value)
        elif attrname == "validation_sources":
            return ValidationSourceList(self._field.attrs.get("validation_sources", []), self._value)
        elif attrname in self._field.attrs["content"]:
            return self._field.attrs["content"][attrname]
        elif attrname in self._field.attrs:
            return self._field.attrs[attrname]
        elif attrname in self._field.schema:
            return self._field.schema[attrname]
        elif attrname == "hidden":
            return False
        else:
            raise AttributeError(attrname)

    def __setattr__(self, attrname: str, value: Any) -> None:
        if not self._field.field_source._updates:
            raise TypeError("Field formulas must not modify values of other fields")

        if attrname == "options":
            value = [EnumOption._dict_copy(option) for option in value]
        elif attrname == "validation_sources":
            if not isinstance(value, list) and not isinstance(value, ValidationSourceList):
                raise TypeError(f"validation_sources must be a list, not {type(value)}")

        if attrname in ("validation_sources", "hidden", "options"):
            self._field.attrs[attrname] = value
            self._field.field_source._updates.replace_attrs(self._field.attrs, {attrname})
        elif attrname in ("value", "position", "page"):
            self._field.attrs["content"][attrname] = value
            self._field.field_source._updates.replace_attrs(self._field.attrs, {"content." + attrname})
        else:
            raise AttributeError(f"{attrname} is read-only or unknown")


class EnumOption:
    _option_dict: dict
    _value: FieldValueBase

    def __init__(self, option_dict: dict, value: Optional[FieldValueBase] = None) -> None:
        self.__dict__["_option_dict"] = option_dict  # {"label": ..., "value": ...}
        self.__dict__["_value"] = value

    def __getattr__(self, attrname: str) -> Any:
        if attrname == "label":
            return self._option_dict["label"]
        elif attrname == "value":
            val = self._option_dict["value"]
            try:
                dp_type = self._value.attr.enum_value_type
            except AttributeError:
                dp_type = "string"
            if dp_type == "number":
                try:
                    return float(val)
                except Exception:  # None, conversion error, ...
                    return None
            elif dp_type == "date":
                try:
                    return datetime.datetime.strptime(val, "%Y-%m-%d").date()
                except Exception:  # None, conversion error, ...
                    return None
            else:
                return val or ""
        else:
            raise AttributeError(attrname)

    def __setattr__(self, attrname: str, value: Any) -> Any:
        if attrname not in self._option_dict:
            raise AttributeError(attrname)
        if attrname == "value":
            value = str(value)
        self._option_dict[attrname] = value
        if self._value is not None:
            if not self._value._field.field_source._updates:
                raise TypeError("Field formulas must not modify values of other fields")
            self._value._field.field_source._updates.replace_attrs(self._value._field.attrs, {"options"})

    def __repr__(self) -> str:
        return f"<EnumOption {self._option_dict['value']}>"

    @staticmethod
    def _dict_copy(opt: EnumOption | dict) -> dict:
        if isinstance(opt, EnumOption):
            return {**opt._option_dict}
        else:
            return {"label": opt["label"], "value": str(opt["value"])}


class EnumOptionList(collections.UserList):
    data: list[dict]
    _value: Optional[FieldValueBase]

    def __init__(self, data: list[dict], value: Optional[FieldValueBase] = None) -> None:
        super().__init__(data)
        self._value = value

    @overload  # type: ignore[override]
    def __getitem__(self, index: SupportsIndex) -> EnumOption: ...

    @overload
    def __getitem__(self, index: slice) -> List[EnumOption]: ...

    def __getitem__(self, index: SupportsIndex | slice) -> EnumOption | List[EnumOption]:
        if isinstance(index, slice):
            return [EnumOption(self.data[i], self._value) for i in range(*index.indices(len(self)))]
        else:
            return EnumOption(self.data[index], self._value)

    def _notify_update(self) -> None:
        if self._value is not None:
            self._value.attr.options = self.data

    def __setitem__(self, index: SupportsIndex | slice, opt: Any) -> None:
        if isinstance(index, slice):
            self.data[index] = [EnumOption._dict_copy(option) for option in opt]
        else:
            self.data[index] = EnumOption._dict_copy(opt)
        self._notify_update()

    def append(self, opt: EnumOption | dict) -> None:
        self.data.append(EnumOption._dict_copy(opt))
        self._notify_update()

    def extend(self, opt: Iterable[EnumOption | dict]) -> None:
        self.data.extend([EnumOption._dict_copy(option) for option in opt])
        self._notify_update()

    def __iadd__(self, opt: Iterable[EnumOption | dict]) -> EnumOptionList:  # type: ignore[misc]
        self.data += [EnumOption._dict_copy(option) for option in opt]
        self._notify_update()
        return self

    def insert(self, index: int, opt: EnumOption | dict) -> None:
        self.data.insert(index, EnumOption._dict_copy(opt))
        self._notify_update()

    def remove(self, opt: EnumOption | dict) -> None:
        data_values = [option["value"] for option in self.data]
        i = data_values.index(opt.value if isinstance(opt, EnumOption) else opt["value"])
        del self[i]

    def __delitem__(self, index: SupportsIndex | slice) -> None:
        del self.data[index]
        self._notify_update()


class ValidationSourceList(collections.UserList):
    data: list[str]
    _value: Optional[FieldValueBase]

    def __init__(self, data: list[dict], value: Optional[FieldValueBase] = None) -> None:
        super().__init__(data)
        self._value = value

    @overload  # type: ignore[override]
    def __getitem__(self, index: SupportsIndex) -> str: ...

    @overload
    def __getitem__(self, index: slice) -> List[str]: ...

    def __getitem__(self, index: SupportsIndex | slice) -> str | List[str]:
        return self.data[index]

    def _notify_update(self) -> None:
        if self._value is not None:
            self._value.attr.validation_sources = self.data

    def __setitem__(self, index: SupportsIndex | slice, src: Any) -> None:
        self.data[index] = src
        self._notify_update()

    def append(self, src: str) -> None:
        self.data.append(src)
        self._notify_update()

    def extend(self, srcs: Iterable[str]) -> None:
        self.data.extend(srcs)
        self._notify_update()

    def __iadd__(self, srcs: Iterable[str]) -> ValidationSourceList:  # type: ignore[misc]
        self.data += srcs
        self._notify_update()
        return self

    def insert(self, index: int, src: str) -> None:
        self.data.insert(index, src)
        self._notify_update()

    def remove(self, src: str) -> None:
        self.data.remove(src)
        self._notify_update()

    def __delitem__(self, index: SupportsIndex | slice) -> None:
        del self.data[index]
        self._notify_update()


class StringValue(FieldValueBase, str):
    def __new__(cls, data: str, field: Field) -> StringValue:
        self = str.__new__(cls, data)
        self._attach_field(field)
        return self


class DatapointValueProxyBase(FieldValueBase):
    def __init__(self, data: Any, field: Field) -> None:
        self.__dict__["data"] = data
        self._attach_field(field)

    def __getattr__(self, attrname: str) -> Any:
        try:
            return FieldValueBase.__getattr__(self, attrname)
        except AttributeError:
            return getattr(self.data, attrname)

    def __setattr__(self, attrname: str, value: Any) -> Any:
        try:
            return FieldValueBase.__setattr__(self, attrname, value)
        except AttributeError:
            return setattr(self.data, attrname, value)

    @staticmethod
    def _demote(x: Any) -> Any:
        try:
            return x.data  # proxy
        except Exception:
            return x  # extending

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return repr(self.data)

    def __format__(self, specifier: str) -> str:
        return self.data.__format__(specifier)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __neg__(self) -> bool:
        return -self.data

    def __pos__(self) -> Any:
        return +self.data

    def __abs__(self) -> int:
        return abs(self.data)

    def __round__(self, ndigits: int | None = None) -> int:
        return round(self.data, ndigits)

    def __trunc__(self) -> int:
        return math.trunc(self.data)

    def __floor__(self) -> int:
        return math.floor(self.data)

    def __ceil__(self) -> int:
        return math.ceil(self.data)

    def __int__(self) -> int:
        return int(self.data)

    def __float__(self) -> float:
        return float(self.data)

    def __add__(self, other: Any) -> Any:
        return self.data + self._demote(other)

    __radd__ = __add__

    def __mul__(self, other: Any) -> Any:
        return self.data * self._demote(other)

    __rmul__ = __mul__

    def __sub__(self, other: Any) -> Any:
        return self.data - self._demote(other)

    def __rsub__(self, other: Any) -> Any:
        return self._demote(other) - self._demote(self)

    def __truediv__(self, other: Any) -> Any:
        return self._demote(self) / self._demote(other)

    def __rtruediv__(self, other: Any) -> Any:
        return self._demote(other) / self._demote(self)

    def __floordiv__(self, other: Any) -> Any:
        return self._demote(self) // self._demote(other)

    def __rfloordiv__(self, other: Any) -> Any:
        return self._demote(other) // self._demote(self)

    def __mod__(self, other: Any) -> Any:
        return self._demote(self) % self._demote(other)

    def __rmod__(self, other: Any) -> Any:
        return self._demote(other) % self._demote(self)

    def __divmod__(self, other: Any) -> Any:
        return divmod(self._demote(self), self._demote(other))

    def __rdivmod__(self, other: Any) -> Any:
        return divmod(self._demote(other), self._demote(self))

    def __pow__(self, other: Any, mod: Any = None) -> Any:
        return pow(self._demote(self), self._demote(other), mod)

    def __rpow__(self, other: Any, mod: Any = None) -> Any:
        return pow(self._demote(other), self._demote(self), mod)

    def __lt__(self, other: Any) -> bool:
        return self._demote(self) < self._demote(other)

    def __le__(self, other: Any) -> bool:
        return self._demote(self) <= self._demote(other)

    def __eq__(self, other: Any) -> bool:
        return self._demote(self) == self._demote(other)

    def __ne__(self, other: Any) -> bool:
        return self._demote(self) != self._demote(other)

    def __ge__(self, other: Any) -> bool:
        return self._demote(self) >= self._demote(other)

    def __gt__(self, other: Any) -> bool:
        return self._demote(self) > self._demote(other)

    def __json__(self) -> Any:
        return self.data


class NumberValue(DatapointValueProxyBase):
    def __init__(self, data: Optional[float], field: Field) -> None:
        super().__init__(data, field)


class DateValue(DatapointValueProxyBase):
    def __init__(self, data: Optional[datetime.date], field: Field) -> None:
        super().__init__(data, field)

    def __json__(self) -> Optional[str]:
        return self.data.isoformat() if self.data else None


class BooleanValue(DatapointValueProxyBase):
    def __init__(self, data: Optional[bool], field: Field) -> None:
        super().__init__(data, field)


class ColumnMixin(collections.abc.MutableSequence):
    def _promote(self, x: Any) -> Any:
        if not isinstance(x, str):
            try:
                if len(x) != len(self):
                    raise ValueError(f"Binary operation on unevenly long columns ({len(self)}, {len(x)})")
                return x
            except TypeError:
                pass
        return [x] * len(self)

    def default_to(self, default: Any) -> ColumnMixin:
        return ValuesColumn([default_to(x, y) for x, y in zip(self, self._promote(default))])

    def is_empty(self) -> ColumnMixin:
        return ValuesColumn([is_empty(x) for x in self])

    def __neg__(self) -> ColumnMixin:
        return ValuesColumn([-x for x in self])

    def __pos__(self) -> ColumnMixin:
        return ValuesColumn([+x for x in self])

    def __abs__(self) -> ColumnMixin:
        return ValuesColumn([abs(x) for x in self])

    def __round__(self, ndigits: int | None = None) -> ColumnMixin:
        return ValuesColumn([round(x, ndigits) for x in self])

    def __trunc__(self) -> ColumnMixin:
        return ValuesColumn([math.trunc(x) for x in self])

    def __floor__(self) -> ColumnMixin:
        return ValuesColumn([math.floor(x) for x in self])

    def __ceil__(self) -> ColumnMixin:
        return ValuesColumn([math.ceil(x) for x in self])

    def __int__(self) -> ColumnMixin:
        return ValuesColumn([int(x) for x in self])

    def __float__(self) -> ColumnMixin:
        return ValuesColumn([float(x) for x in self])

    def __bool__(self) -> NoReturn:
        raise ValueError(
            "Table column does not have a bool value - wrap it in all(), any() or aggregation such as sum()"
        )

    def __add__(self, other: Any) -> ColumnMixin:
        a = ValuesColumn([x + y for x, y in zip(self, self._promote(other))])
        return a

    __iadd__ = __add__

    def __radd__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([y + x for x, y in zip(self, self._promote(other))])

    def __mul__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x * y for x, y in zip(self, self._promote(other))])

    __imul__ = __mul__

    def __rmul__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([y * x for x, y in zip(self, self._promote(other))])

    def __sub__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x - y for x, y in zip(self, self._promote(other))])

    __isub__ = __sub__

    def __rsub__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([y - x for x, y in zip(self, self._promote(other))])

    def __truediv__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x / y for x, y in zip(self, self._promote(other))])

    __itruediv__ = __truediv__

    def __rtruediv__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([y / x for x, y in zip(self, self._promote(other))])

    def __floordiv__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x // y for x, y in zip(self, self._promote(other))])

    __ifloordiv__ = __floordiv__

    def __rfloordiv__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([y // x for x, y in zip(self, self._promote(other))])

    def __mod__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x % y for x, y in zip(self, self._promote(other))])

    __imod__ = __mod__

    def __rmod__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([y % x for x, y in zip(self, self._promote(other))])

    def __divmod__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([divmod(x, y) for x, y in zip(self, self._promote(other))])

    def __rdivmod__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([divmod(y, x) for x, y in zip(self, self._promote(other))])

    def __pow__(self, other: Any, mod: Any = None) -> ColumnMixin:
        return ValuesColumn([pow(x, y, mod) for x, y in zip(self, self._promote(other))])

    __ipow__ = __pow__

    def __rpow__(self, other: Any, mod: Any = None) -> ColumnMixin:
        return ValuesColumn([pow(y, x, mod) for x, y in zip(self, self._promote(other))])

    def __lt__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x < y for x, y in zip(self, self._promote(other))])

    def __le__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x <= y for x, y in zip(self, self._promote(other))])

    def __eq__(self, other: Any) -> ColumnMixin:  # type: ignore[override]
        return ValuesColumn([x == y for x, y in zip(self, self._promote(other))])

    def __ne__(self, other: Any) -> ColumnMixin:  # type: ignore[override]
        return ValuesColumn([x != y for x, y in zip(self, self._promote(other))])

    def __ge__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x >= y for x, y in zip(self, self._promote(other))])

    def __gt__(self, other: Any) -> ColumnMixin:
        return ValuesColumn([x > y for x, y in zip(self, self._promote(other))])


class ValuesColumn(ColumnMixin, collections.UserList):  # type: ignore[misc]
    """
    Operations on TableColumn produce a ValueColumn which is a list of
    instantiated field values that is detached from Fields but still applies
    ops element-wise.
    """

    pass


class FieldMutableSequence(collections.abc.MutableSequence):
    _field: MultivalueIterableField

    def __len__(self) -> int:
        return len(self._field.all_fields)

    @overload
    def __getitem__(self, index: SupportsIndex) -> FieldValueBase: ...

    @overload
    def __getitem__(self, index: slice) -> List[FieldValueBase]: ...

    def __getitem__(self, index: SupportsIndex | slice) -> FieldValueBase | List[FieldValueBase]:
        if isinstance(index, slice):
            return [
                self._field.all_fields[idx].get_value() for idx in range(*index.indices(len(self._field.all_fields)))
            ]
        else:
            return self._field.all_fields[index].get_value()

    def __setitem__(self, index: SupportsIndex | slice, value: Any) -> None:
        if not isinstance(index, slice):
            index = slice(index, index + 1, 1)  # type: ignore[operator]
            value = [value]

        for val, idx in zip(
            value, range(index.start or 0, index.stop if index.stop is not None else len(self), index.step or 1)
        ):
            self._field.all_fields[idx].set_value(val)

    def __delitem__(self, index: SupportsIndex | slice) -> None:
        if not isinstance(index, slice):
            index = slice(index, index + 1, 1)  # type: ignore[operator]

        self._field.remove_slice(index)

    def insert(self, index: int, value: Any) -> None:
        if index == len(self):
            self._field.append(value)
        else:
            last_index = len(self) - 1
            self._field.append(self[last_index])
            for i in range(last_index, index, -1):
                self[i] = self[i - 1]
            self[index] = value

    def index(self, value: Any, start: int = 0, stop: Optional[int] = None) -> int:
        if start < 0:
            start = max(len(self) + start, 0)
        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop += len(self)
        all_fields = self._field.all_fields[start:stop]
        return start + self._field.index(all_fields, value)

    def copy(self) -> collections.abc.MutableSequence:
        return [x.get_value() for x in self._field.all_fields]

    def __str__(self) -> str:
        return str(self.copy())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.copy()}>"

    def _replace(self, new_values: collections.abc.Collection[Any]) -> None:
        """
        Generate a diff between current and new list of values and execute
        the operations in this diff (by doing updates, appends or removals).
        """
        # XXX: Greedy algorithm. We could use dynamic programming to generate
        # an optimally minimal edit script.

        for i, new_value in enumerate(new_values):
            if i >= len(self):
                self.append(new_value)
                continue

            for j, old_value in enumerate(self[i:], i):
                if old_value == new_value:
                    if j > i:
                        del self[i:j]
                    self[i] = new_value
                    break
            else:
                # No subsequence to remove, replace current value
                self[i] = new_value

        if len(new_values) < len(self):
            del self[len(new_values) : len(self)]


class TableColumn(ColumnMixin, FieldMutableSequence):
    _field: MultivalueDatapointField

    def __init__(self, field: MultivalueDatapointField) -> None:
        self._field = field

    def __json__(self) -> Any:
        return [item.__json__() for item in self]


class TableRows(FieldValueBase, FieldMutableSequence):
    _field: MultivalueTupleField

    def __init__(self, field: MultivalueTupleField) -> None:
        field.attrs["content"] = field.attrs.get("content", {})
        self._attach_field(field)

    def __json__(self) -> Any:
        return [row.__json__() for row in self]


class Table(FieldValueBase, FieldMutableSequence):
    _field: MultivalueField

    def __init__(self, field: MultivalueField) -> None:
        field.attrs["content"] = field.attrs.get("content", {})
        self._attach_field(field)

    @property
    def all_values(self) -> TableColumn:
        # Compatibility shim, as we used to require .all_values access even to
        # outer multivalue containers of simple datapoints.
        if isinstance(self._field.child_field, MultivalueDatapointField):
            return self._field.child_field.get_value().all_values
        else:
            raise AttributeError("all_values")

    @all_values.setter
    def all_values(self, new_values: collections.abc.Collection[Any]) -> None:
        if isinstance(self._field.child_field, MultivalueDatapointField):
            self._replace(new_values)
        else:
            raise AttributeError("all_values")

    def __json__(self) -> Any:
        return self._field.child_field.get_value().__json__()


class TableRow(FieldContextMixin, FieldValueBase):
    _field: RowTupleField
    _fallback_to_global: bool = False

    def __init__(self, field: RowTupleField) -> None:
        super().__init__()
        field.attrs["content"] = field.attrs.get("content", {})
        self._attach_field(field)

    @contextmanager
    def _row_formula_context(self, t: TxScriptAnnotationContent) -> Generator[TxScriptAnnotationContent, None, None]:
        """In this context, row behaves like `field` within a row formula,
        allowing access to global fields as well."""
        self._fallback_to_global = True
        try:
            yield t._with_field(cast("Fields", self))  # the TableRow behaves like a Fields instance
        finally:
            self._fallback_to_global = False

    def _get_field(self, attrname: str) -> Field:
        try:
            return self._field.get_field(attrname)
        except AttributeError:
            if not self._fallback_to_global:
                raise
            return self._field.field_source._get_field(attrname)

    def __getattr__(self, attrname: str) -> Any:
        try:
            return self._get_field(attrname).get_value()
        except AttributeError:
            try:
                return FieldValueBase.__getattr__(self, attrname)
            except AttributeError:
                raise AttributeError(f"Field '{attrname}' is not defined in tuple '{self._field.schema_id}'")

    def __setattr__(self, attrname: str, value: Any) -> Any:
        try:
            return self._get_field(attrname).set_value(value)
        except AttributeError:
            try:
                return FieldValueBase.__setattr__(self, attrname, value)
            except AttributeError:
                raise AttributeError(f"Field '{attrname}' is not defined in tuple '{self._field.schema_id}'")

    def __str__(self) -> str:
        return (
            "TableRow("
            + ", ".join(
                schema_id + "=" + repr(self._field.get_field(schema_id).get_value())
                for schema_id in self._field.schema["children"]
            )
            + ")"
        )

    def __repr__(self) -> str:
        return str(self)

    @property
    def _index(self) -> int:
        return self._field.attrs["_content_index"]

    @staticmethod
    def _columns_attrs_from_value(value: dict, field: RowTupleField) -> dict:
        attrs = {}
        for column in field.columns:
            v = value.get(column.schema_id, None)
            attrs[column.schema_id] = FieldValueBase._attrs_from_value(v, column)

        for k in value.keys():
            if k not in attrs:
                raise ValueError(f"Attempted to set column {k} that is not a member of the tuple")

        return attrs

    def __json__(self) -> Any:
        return {cell_field.schema_id: cell_field.get_value() for cell_field in self._field.cells}


class TableColumnValue(FieldValueBase, collections.abc.MutableSequence):
    _field: MultivalueDatapointField
    _cached_all_values: Optional[TableColumn] = None

    def __init__(self, field: Field) -> None:
        if "content" not in field.attrs:
            field.attrs["content"] = {}
        self._attach_field(field)

    @property
    def all_values(self) -> TableColumn:
        if self._cached_all_values is None:
            self._cached_all_values = TableColumn(self._field)
        return self._cached_all_values

    @all_values.setter
    def all_values(self, new_values: collections.abc.Collection[Any]) -> None:
        if not hasattr(new_values, "__iter__"):
            raise TypeError(".all_values must be assigned a list or other iterable")
        self.all_values._replace(new_values)

    error_message_list = (
        "The multivalue field value is not a list by itself, use the .all_values property to access the list"
    )

    def __len__(self) -> Any:
        raise TypeError(self.__class__.error_message_list)

    def __getitem__(self, index: int) -> Any:  # type: ignore[override]
        raise TypeError(self.__class__.error_message_list)

    def __setitem__(self, index: int, value: Any) -> Any:  # type: ignore[override]
        raise TypeError(self.__class__.error_message_list)

    def __delitem__(self, index: int) -> Any:  # type: ignore[override]
        raise TypeError(self.__class__.error_message_list)

    def insert(self, index: int, value: Any) -> Any:
        raise TypeError(self.__class__.error_message_list)

    def index(self, value: Any, start: Optional[int] = 0, stop: Optional[int] = None) -> Any:
        raise TypeError(self.__class__.error_message_list)

    error_message = "Ambiguous operation on multivalue field, use the .all_values property to access the whole column"

    def __str__(self) -> str:
        raise TypeError(self.__class__.error_message)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.all_values}>"

    def __format__(self, specifier: str) -> str:
        raise TypeError(self.__class__.error_message)

    def __bool__(self) -> bool:
        raise TypeError(self.__class__.error_message)

    def __neg__(self) -> bool:
        raise TypeError(self.__class__.error_message)

    def __pos__(self) -> Any:
        raise TypeError(self.__class__.error_message)

    def __abs__(self) -> int:
        raise TypeError(self.__class__.error_message)

    def __round__(self, ndigits: int | None = None) -> int:
        raise TypeError(self.__class__.error_message)

    def __trunc__(self) -> int:
        raise TypeError(self.__class__.error_message)

    def __floor__(self) -> int:
        raise TypeError(self.__class__.error_message)

    def __ceil__(self) -> int:
        raise TypeError(self.__class__.error_message)

    def __int__(self) -> int:
        raise TypeError(self.__class__.error_message)

    def __float__(self) -> float:
        raise TypeError(self.__class__.error_message)

    def __add__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    __radd__ = __add__

    def __mul__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    __rmul__ = __mul__

    def __sub__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __rsub__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __truediv__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __rtruediv__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __floordiv__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __rfloordiv__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __mod__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __rmod__(self, other: Any) -> Any:
        raise TypeError(self.__class__.error_message)

    def __divmod__(self, other: Any) -> TableColumn:
        raise TypeError(self.__class__.error_message)

    def __rdivmod__(self, other: Any) -> TableColumn:
        raise TypeError(self.__class__.error_message)

    def __pow__(self, other: Any, mod: Any = None) -> TableColumn:
        raise TypeError(self.__class__.error_message)

    def __rpow__(self, other: Any, mod: Any = None) -> TableColumn:
        raise TypeError(self.__class__.error_message)

    def __lt__(self, other: Any) -> bool:
        raise TypeError(self.__class__.error_message)

    def __le__(self, other: Any) -> bool:
        raise TypeError(self.__class__.error_message)

    def __eq__(self, other: Any) -> bool:
        raise TypeError(self.__class__.error_message)

    def __ne__(self, other: Any) -> bool:
        raise TypeError(self.__class__.error_message)

    def __ge__(self, other: Any) -> bool:
        raise TypeError(self.__class__.error_message)

    def __gt__(self, other: Any) -> bool:
        raise TypeError(self.__class__.error_message)

    def __json__(self) -> Any:
        return self.all_values.__json__()
