from pathlib import Path
from typing import Any

import pytest

from ..txscript import TxScript
from ..txscript.datapoint import MultivalueDatapointField, MultivalueTupleField, Table, TableColumnValue
from ..txscript.fields import Fields  # noqa: TC002
from ..txscript.formula import Formula


def mkpayload() -> dict:
    import json

    with (Path(__file__).parent / "data" / "schema.json").open() as f:
        schema = json.load(f)
    with (Path(__file__).parent / "data" / "annotation.json").open() as f:
        annotation = json.load(f)

    return {"annotation": annotation, "schemas": [schema], "event": "annotation_content"}


def override_field_values(field: Fields, **overrides):
    assert field._updates.updates_by_field == {}

    for k, v in overrides.items():
        if isinstance(v, list):
            if isinstance(getattr(field, k), TableColumnValue):
                getattr(field, k).all_values = v
            else:
                assert isinstance(getattr(field, k), Table)
                setattr(field, k, v)
        else:
            setattr(field, k, v)

    # Reset history (do not include overrides in hook response operations)
    for dp_updates in field._updates.updates_by_field.values():
        # All pre-existing fields must have attrs["id"] set
        dp = dp_updates.dp
        if "id" not in dp:
            new_field = field._get_field(dp["schema_id"])
            if isinstance(new_field, MultivalueTupleField):
                i = dp["_content_index"]
                for column in new_field.columns:
                    column.all_fields[i].attrs["id"] = f"{column.schema['id']}_{i}"
                dp["id"] = f"{new_field.schema['id']}_{i}"
            elif isinstance(new_field, MultivalueDatapointField):
                i = new_field.attrs["all_objects"].index(dp)
                dp["id"] = f"{new_field.schema['id']}_{i}"
    field._updates.updates_by_field.clear()
    field._field_cache.clear()


def exec_test_formula(code: str, field_values: str, result: Any) -> None:
    t = TxScript.from_payload(mkpayload())
    override_field_values(t.field, **field_values)
    formula = Formula("field", code)
    if isinstance(result, type):
        with t.field._readonly_context():
            with pytest.raises(result):
                formula.evaluate(t)
    else:
        with t.field._readonly_context():
            ret = formula.evaluate(t)
        value = result
        if isinstance(result, dict):
            assert t._messages == [{**m, "source_id": -1} for m in result.get("messages", [])], t._messages
            assert t._automation_blockers == [{**m, "source_id": -1} for m in result.get("automation_blockers", [])], (
                t._automation_blockers
            )
            if "value" in result:
                value = result["value"]
            else:
                return
        assert ret == value


def exec_test_row_formula(code: str, field_values: str, result: dict) -> None:
    t = TxScript.from_payload(mkpayload())
    override_field_values(t.field, **field_values)
    formula = Formula("field", code)
    for value, row in zip(result["values"], t.field.line_items):
        with t.field._readonly_context():
            with row._row_formula_context(t) as row_r:
                if isinstance(value, type):
                    with pytest.raises(value):
                        formula.evaluate(row_r)
                else:
                    ret = formula.evaluate(row_r)
                    assert ret == value
    assert t._messages == result.get("messages", []), t._messages
    assert t._automation_blockers == result.get("automation_blockers", []), t._automation_blockers
