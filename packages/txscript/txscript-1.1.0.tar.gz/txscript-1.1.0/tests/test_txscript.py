import pytest
import requests_mock

from lib.txscript.tests.constants import (
    ENUM_ID,
    ITEM2_NUMBER_ID,
    ITEM2_STR_ID,
    ITEM_NUMBER_ID_1,
    ITEM_NUMBER_ID_3,
    ITEM_STR_ID_1,
    ITEM_STR_ID_2,
    ITEM_STR_ID_3,
    LINE_ITEM_ID_2,
    LINE_ITEMS2_ID,
    LINE_ITEMS_EMPTY_ID,
    LINE_ITEMS_ID,
    MULTISTR_EMPTY_OUTER_ID,
    MULTISTR_INNER_ID_1,
    MULTISTR_INNER_ID_2,
    MULTISTR_OUTER_ID,
    NUMBER2_ID,
    NUMBER_ID,
    STR2_ID,
    STR_ID,
)
from lib.txscript.tests.helpers import mkpayload, override_field_values
from lib.txscript.txscript import *  # noqa: F403
from lib.txscript.txscript.exceptions import PayloadError

field_values = {
    "number": 42,
    "str": "CZ123456",
    "date": "2023-05-22",
}

li_values = {
    "line_items": [
        {"item_str": "Ab-c-d", "item_number": 1},
        {"item_str": "Ef-g-h", "item_number": 2},
        {"item_str": "Ijk", "item_number": 3},
        {"item_str": "Lmn", "item_number": 4},
    ],
}


def test_basic_hook() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, **field_values)

    assert t.annotation.status == "reviewing"
    assert t.annotation.previous_status is None
    assert t.annotation.raw_data["url"] == "https://elis.rossum.ai/api/v1/annotations/48635144"

    assert t.field.number == 42
    assert not is_empty(t.field.number)  # noqa: F405
    assert is_empty(t.field.number2)  # noqa: F405

    with pytest.raises(AttributeError, match=".*not defined.*"):
        t.field.nonexistent_field = 42
    with pytest.raises(AttributeError, match=".*not present.*"):
        t.field.number_nonpresent = 42

    row = t.field.line_items[0]
    row.item_number = 2

    t.field.number2 = t.field.number
    t.field.number.attr.page = t.field.number.attr.position = None
    t.field.number.attr.validation_sources = []
    t.field.str2 = substitute(r"vi", "wy", t.annotation.status)  # noqa: F405
    t.field.str2.attr.hidden = True
    t.show_info("str2 info", field=t.field.str2)
    t.show_warning("global warning")
    t.automation_blocker("str blocker", field=t.field.str)
    t.automation_blocker("global blocker")
    assert t.hook_response() == {
        "actions": [],
        "computed_ids": [],
        "promises": [],
        "automation_blockers": [
            {"content": "str blocker", "id": STR_ID, "source_id": -1},
            {"content": "global blocker", "source_id": -1},
        ],
        "messages": [
            {"type": "info", "content": "str2 info", "id": STR2_ID, "source_id": -1},
            {"type": "warning", "content": "global warning", "source_id": -1},
        ],
        "operations": [
            {"op": "replace", "id": ITEM_NUMBER_ID_1, "value": {"content": {"value": "2"}}},
            {
                "op": "replace",
                "id": NUMBER2_ID,
                "value": {
                    "content": {
                        "value": "42.0",
                    },
                },
            },
            {
                "id": NUMBER_ID,
                "op": "replace",
                "value": {
                    "content": {
                        "page": None,
                        "position": None,
                    },
                    "validation_sources": [],
                },
            },
            {"op": "replace", "id": STR2_ID, "value": {"content": {"value": "rewyewing"}, "hidden": True}},
        ],
    }


def test_parent_accessors() -> None:
    """Test that parent and parent_multivalue properties work correctly."""
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, **li_values)
    override_field_values(t.field, multistr_inner=["value1", "value2", "value3"])

    # Test parent and parent_multivalue in tuple context (line_items)
    first_row = t.field.line_items[0]
    cell = first_row.item_str
    simple_value = t.field.multistr_inner.all_values[0]

    # Test parent access from table cell (returns the row)
    assert cell.parent == first_row
    assert cell.parent_multivalue == t.field.line_items

    # Test parent access from simple multivalue element (returns multivalue itself)
    assert simple_value.parent == t.field.multistr_outer
    assert simple_value.parent_multivalue == t.field.multistr_outer

    # Test parent access from rows
    assert first_row.parent == t.field.line_items
    assert first_row.parent_multivalue == t.field.line_items

    # Test parent access from columns
    assert t.field.item_str.parent == t.field.line_items
    assert t.field.item_str.parent_multivalue == t.field.line_items
    assert t.field.multistr_inner.parent == t.field.multistr_outer
    assert t.field.multistr_inner.parent_multivalue == t.field.multistr_outer


def test_enum_options_setattr() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    t.field.enum.attr.options[1].label = "ABCD"
    assert t.field.enum.attr.options[1].label == "ABCD"
    assert t.field.enum.attr.options[1].value == "credit_note"
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": ENUM_ID,
            "value": {
                "options": [
                    {"value": "tax_invoice", "label": "Tax Invoice"},
                    {"value": "credit_note", "label": "ABCD"},
                    {"value": "proforma", "label": "Pro Forma Invoice"},
                ]
            },
        }
    ]


def test_enum_options_setitem() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    t.field.enum.attr.options[1] = t.field.enum.attr.options[2]
    t.field.enum.attr.options[2].label = "Change should not propagate"
    assert t.field.enum.attr.options[1].label == "Pro Forma Invoice"
    assert t.field.enum.attr.options[1].value == "proforma"
    assert t.field.enum.attr.options[2].label == "Change should not propagate"
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": ENUM_ID,
            "value": {
                "options": [
                    {"value": "tax_invoice", "label": "Tax Invoice"},
                    {"value": "proforma", "label": "Pro Forma Invoice"},
                    {"value": "proforma", "label": "Change should not propagate"},
                ]
            },
        }
    ]


def test_enum_options_setitem_dict() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    d = {"label": "ABCD", "value": 42}
    t.field.enum_number.attr.options[1] = d
    d["label"] = "Change should not propagate"
    assert t.field.enum_number.attr.options[1].label == "ABCD"
    assert t.field.enum_number.attr.options[1].value == 42
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": 4880323642,
            "value": {
                "options": [
                    {"value": "1", "label": "one"},
                    {"value": "42", "label": "ABCD"},
                    {"value": "3", "label": "three"},
                ]
            },
        }
    ]


def test_enum_options_set() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    t.field.enum.attr.options = t.field.enum.attr.options[0:2]
    assert [o.value for o in t.field.enum.attr.options] == ["tax_invoice", "credit_note"]
    t.field.enum.attr.options = [t.field.enum.attr.options[1], t.field.enum.attr.options[0]]
    assert [o.value for o in t.field.enum.attr.options] == ["credit_note", "tax_invoice"]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "id": ENUM_ID,
            "op": "replace",
            "value": {
                "options": [
                    {"label": "Credit Note", "value": "credit_note"},
                    {"label": "Tax Invoice", "value": "tax_invoice"},
                ]
            },
        }
    ]


def test_enum_options_setdict() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    t.field.enum.attr.options = [{"label": "ABCD", "value": "abcd"}, {"label": "EFGH", "value": "efgh"}]
    assert [o.label for o in t.field.enum.attr.options] == ["ABCD", "EFGH"]
    assert [o.value for o in t.field.enum.attr.options] == ["abcd", "efgh"]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": ENUM_ID,
            "value": {"options": [{"label": "ABCD", "value": "abcd"}, {"label": "EFGH", "value": "efgh"}]},
        },
    ]


def test_enum_options_append() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405

    t.field.enum.attr.options.append({"label": "ABCD", "value": "abcd"})
    t.field.enum.attr.options.append(t.field.enum.attr.options[0])
    assert [o.label for o in t.field.enum.attr.options] == [
        "Tax Invoice",
        "Credit Note",
        "Pro Forma Invoice",
        "ABCD",
        "Tax Invoice",
    ]
    assert [o.value for o in t.field.enum.attr.options] == [
        "tax_invoice",
        "credit_note",
        "proforma",
        "abcd",
        "tax_invoice",
    ]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": ENUM_ID,
            "value": {
                "options": [
                    {"value": "tax_invoice", "label": "Tax Invoice"},
                    {"value": "credit_note", "label": "Credit Note"},
                    {"value": "proforma", "label": "Pro Forma Invoice"},
                    {"label": "ABCD", "value": "abcd"},
                    {"value": "tax_invoice", "label": "Tax Invoice"},
                ]
            },
        }
    ]


def test_enum_options_extend() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405

    t.field.line_items_empty.append({})
    new_enum = t.field.item_empty_enum_number.all_values[0]
    new_enum.attr.options += [{"label": "ABCD", "value": 1}, {"label": "EFGH", "value": "efgh"}]
    new_enum.attr.options.extend(new_enum.attr.options[:2])
    new_enum.attr.options[0].label = "Change should not propagate"
    assert [o.label for o in new_enum.attr.options] == [
        "Change should not propagate",
        "EFGH",
        "ABCD",
        "EFGH",
    ]
    assert [o.value for o in new_enum.attr.options] == [
        1,
        None,
        1,
        None,
    ]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "add",
            "id": LINE_ITEMS_EMPTY_ID,
            "value": [
                {"content": {"value": ""}, "schema_id": "item_empty_str"},
                {"content": {"value": ""}, "schema_id": "item_empty_str2"},
                {"content": {"value": ""}, "schema_id": "item_empty_number"},
                {"content": {"value": ""}, "schema_id": "item_empty_number2"},
                {
                    "content": {"value": ""},
                    "options": [
                        {"label": "Change should not propagate", "value": "1"},
                        {"label": "EFGH", "value": "efgh"},
                        {"label": "ABCD", "value": "1"},
                        {"label": "EFGH", "value": "efgh"},
                    ],
                    "schema_id": "item_empty_enum_number",
                },
            ],
        }
    ]


def test_enum_options_insert_remove() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405

    t.field.enum.attr.options.insert(1, {"label": "ABCD", "value": "abcd"})
    t.field.enum.attr.options.insert(0, t.field.enum.attr.options[0])
    t.field.enum.attr.options[0].label = "Change should not propagate"
    assert [o.label for o in t.field.enum.attr.options] == [
        "Change should not propagate",
        "Tax Invoice",
        "ABCD",
        "Credit Note",
        "Pro Forma Invoice",
    ]
    assert [o.value for o in t.field.enum.attr.options] == [
        "tax_invoice",
        "tax_invoice",
        "abcd",
        "credit_note",
        "proforma",
    ]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": ENUM_ID,
            "value": {
                "options": [
                    {"value": "tax_invoice", "label": "Change should not propagate"},
                    {"value": "tax_invoice", "label": "Tax Invoice"},
                    {"label": "ABCD", "value": "abcd"},
                    {"value": "credit_note", "label": "Credit Note"},
                    {"value": "proforma", "label": "Pro Forma Invoice"},
                ]
            },
        }
    ]

    t.field.enum.attr.options.remove(t.field.enum.attr.options[0])
    assert [o.label for o in t.field.enum.attr.options] == [
        "Tax Invoice",
        "ABCD",
        "Credit Note",
        "Pro Forma Invoice",
    ]
    assert [o.value for o in t.field.enum.attr.options] == ["tax_invoice", "abcd", "credit_note", "proforma"]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": ENUM_ID,
            "value": {
                "options": [
                    {"value": "tax_invoice", "label": "Tax Invoice"},
                    {"label": "ABCD", "value": "abcd"},
                    {"value": "credit_note", "label": "Credit Note"},
                    {"value": "proforma", "label": "Pro Forma Invoice"},
                ]
            },
        }
    ]


def test_validation_sources_setitem() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    t.field.number.attr.validation_sources[0] = "man"
    assert t.field.number.attr.validation_sources == ["man", "non_required"]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": NUMBER_ID,
            "value": {"validation_sources": ["man", "non_required"]},
        }
    ]


def test_validation_sources_set() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    with pytest.raises(TypeError):
        t.field.number.attr.validation_sources = t.field.number.attr.validation_sources[0]
    t.field.number.attr.validation_sources = t.field.number.attr.validation_sources[:1]
    assert t.field.number.attr.validation_sources == ["human"]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "id": NUMBER_ID,
            "op": "replace",
            "value": {"validation_sources": ["human"]},
        }
    ]

    t.field.number.attr.validation_sources = []
    assert t.field.number.attr.validation_sources == []
    response = t.hook_response()
    assert response["operations"] == [
        {
            "id": NUMBER_ID,
            "op": "replace",
            "value": {"validation_sources": []},
        }
    ]


def test_validation_sources_append_extend() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405

    t.field.number.attr.validation_sources += ["data_matching"]
    t.field.line_items_empty.append({})
    new_num = t.field.item_empty_number.all_values[0]
    new_num.attr.validation_sources.append("connector")
    new_num.attr.validation_sources.extend(t.field.number.attr.validation_sources)
    assert t.field.number.attr.validation_sources == ["human", "non_required", "data_matching"]
    assert new_num.attr.validation_sources == ["connector", "human", "non_required", "data_matching"]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "replace",
            "id": NUMBER_ID,
            "value": {"validation_sources": ["human", "non_required", "data_matching"]},
        },
        {
            "op": "add",
            "id": LINE_ITEMS_EMPTY_ID,
            "value": [
                {"content": {"value": ""}, "schema_id": "item_empty_str"},
                {"content": {"value": ""}, "schema_id": "item_empty_str2"},
                {
                    "content": {"value": ""},
                    "validation_sources": ["connector", "human", "non_required", "data_matching"],
                    "schema_id": "item_empty_number",
                },
                {"content": {"value": ""}, "schema_id": "item_empty_number2"},
                {"content": {"value": ""}, "schema_id": "item_empty_enum_number"},
            ],
        },
    ]


def test_validation_sources_insert_remove() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405

    t.field.number.attr.validation_sources.remove("non_required")
    t.field.number.attr.validation_sources.insert(0, "data_matching")
    assert t.field.number.attr.validation_sources == ["data_matching", "human"]
    with pytest.raises(ValueError, match="not in list"):
        t.field.number2.attr.validation_sources.remove("human")
    assert t.field.number2.attr.validation_sources == []
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": NUMBER_ID, "value": {"validation_sources": ["data_matching", "human"]}}
    ]


def test_simple_multivalue_assignment() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, multistr_inner=["initial", "values"])

    # Test assigning literals to a non-tuple multivalue
    assert all(t.field.multistr_inner.all_values == ["initial", "values"])
    t.field.multistr_inner.all_values = ["new", "assigned", "values"]
    assert all(t.field.multistr_inner.all_values == ["new", "assigned", "values"])

    # Verify that the operations are recorded
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": MULTISTR_INNER_ID_1, "value": {"content": {"value": "new"}}},
        {"op": "replace", "id": MULTISTR_INNER_ID_2, "value": {"content": {"value": "assigned"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "values"}}},
    ]

    # Verify that a change inside multivalue is processed correctly
    t.field.multistr_inner.all_values[2] = "changed"
    assert all(t.field.multistr_inner.all_values == ["new", "assigned", "changed"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": MULTISTR_INNER_ID_1, "value": {"content": {"value": "new"}}},
        {"op": "replace", "id": MULTISTR_INNER_ID_2, "value": {"content": {"value": "assigned"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "changed"}}},
    ]

    # Verify that non-pristine all_values cannot be modified
    all_values_bracketed = "<" + t.field.multistr_inner.all_values + ">"
    all_values_bracketed[0] = "abc"
    del all_values_bracketed[1]
    all_values_bracketed.append("x")
    all_values_bracketed.remove("<changed>")
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": MULTISTR_INNER_ID_1, "value": {"content": {"value": "new"}}},
        {"op": "replace", "id": MULTISTR_INNER_ID_2, "value": {"content": {"value": "assigned"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "changed"}}},
    ]


def test_simple_multivalue_assignment_outer() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, multistr_inner=["initial", "values"])

    # Test assigning literals to a non-tuple multivalue's outer dp
    assert all(t.field.multistr_outer.all_values == ["initial", "values"])
    t.field.multistr_outer.all_values = ["new", "assigned", "values"]
    assert all(t.field.multistr_outer.all_values == ["new", "assigned", "values"])

    # Verify that the operations are recorded
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": MULTISTR_INNER_ID_1, "value": {"content": {"value": "new"}}},
        {"op": "replace", "id": MULTISTR_INNER_ID_2, "value": {"content": {"value": "assigned"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "values"}}},
    ]


def test_simple_multivalue_assignment_to_empty() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405

    assert len(t.field.multistr_empty_inner.all_values) == 0
    t.field.multistr_empty_inner.all_values = ["new", "assigned", "values"]
    assert all(t.field.multistr_empty_inner.all_values == ["new", "assigned", "values"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "add", "id": MULTISTR_EMPTY_OUTER_ID, "value": {"content": {"value": "new"}}},
        {"op": "add", "id": MULTISTR_EMPTY_OUTER_ID, "value": {"content": {"value": "assigned"}}},
        {"op": "add", "id": MULTISTR_EMPTY_OUTER_ID, "value": {"content": {"value": "values"}}},
    ]


def test_simple_multivalue_incremental() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, multistr_inner=["a", "b", "c", "d", "e", "f"])

    # Verify that a small change in the list results in incremental ops sequence
    t.field.multistr_inner.all_values = [x for x in t.field.multistr_inner.all_values if x not in ("b", "d")]
    assert all(t.field.multistr_inner.all_values == ["a", "c", "e", "f"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "remove", "id": MULTISTR_INNER_ID_2},
        {"op": "remove", "id": "multistr_inner_3"},
    ]

    t.field.multistr_inner.all_values[1] = "cc"
    with pytest.raises(ValueError, match="Binary operation on unevenly long columns.*"):
        t.field.multistr_inner.all_values += ["g"]
    t.field.multistr_inner.all_values.append("g")
    assert all(t.field.multistr_inner.all_values == ["a", "cc", "e", "f", "g"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "remove", "id": MULTISTR_INNER_ID_2},
        {"op": "remove", "id": "multistr_inner_3"},
        {"op": "replace", "id": "multistr_inner_2", "value": {"content": {"value": "cc"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "g"}}},
    ]

    t.field.multistr_inner.all_values.remove("f")
    t.field.multistr_inner.all_values[0] = "f"
    assert all(t.field.multistr_inner.all_values == ["f", "cc", "e", "g"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "remove", "id": MULTISTR_INNER_ID_2},
        {"op": "remove", "id": "multistr_inner_3"},
        {"op": "replace", "id": "multistr_inner_2", "value": {"content": {"value": "cc"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "g"}}},
        {"op": "remove", "id": "multistr_inner_5"},
        {"op": "replace", "id": MULTISTR_INNER_ID_1, "value": {"content": {"value": "f"}}},
    ]


def test_simple_multivalue_incremental_greedy() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, multistr_inner=["a", "b", "c", "d", "e", "f"])

    # XXX: The edit is going to be suboptimal in case we do the modification
    # immediately, due to the greedy algorithm in TableColumnValue.all_values.
    t.field.multistr_inner.all_values = ["f", "b", "c", "d", "e"]
    assert all(t.field.multistr_inner.all_values == ["f", "b", "c", "d", "e"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "remove", "id": MULTISTR_INNER_ID_1},
        {"op": "remove", "id": MULTISTR_INNER_ID_2},
        {"op": "remove", "id": "multistr_inner_2"},
        {"op": "remove", "id": "multistr_inner_3"},
        {"op": "remove", "id": "multistr_inner_4"},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "b"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "c"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "d"}}},
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "e"}}},
    ]


def test_simple_multivalue_appenditicis() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, multistr_inner=["a", "b", "c", "d", "e", "f"], **field_values)

    t.field.multistr_inner.all_values.append("g")
    assert all(t.field.multistr_inner.all_values == ["a", "b", "c", "d", "e", "f", "g"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "g"}}},
    ]

    t.field.multistr_inner.all_values.append(t.field.str)
    assert all(t.field.multistr_inner.all_values == ["a", "b", "c", "d", "e", "f", "g", "CZ123456"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "g"}}},
        {
            "op": "add",
            "id": MULTISTR_OUTER_ID,
            "value": {
                "content": {"value": "CZ123456"},
            },
        },
    ]

    # Modifying the field.str shouldn't affect the multistr_inner

    t.field.str.attr.hidden = True
    assert all(t.field.multistr_inner.all_values == ["a", "b", "c", "d", "e", "f", "g", "CZ123456"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "g"}}},
        {
            "op": "add",
            "id": MULTISTR_OUTER_ID,
            "value": {
                "content": {"value": "CZ123456"},
            },
        },
        {"op": "replace", "id": STR_ID, "value": {"hidden": True}},
    ]

    t.field.str = "abc"
    assert all(t.field.multistr_inner.all_values == ["a", "b", "c", "d", "e", "f", "g", "CZ123456"])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "add", "id": MULTISTR_OUTER_ID, "value": {"content": {"value": "g"}}},
        {
            "op": "add",
            "id": MULTISTR_OUTER_ID,
            "value": {
                "content": {"value": "CZ123456"},
            },
        },
        {"op": "replace", "id": STR_ID, "value": {"content": {"value": "abc"}, "hidden": True}},
    ]


def test_tuple_column_assignment() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, **li_values)

    t.field.item_str.all_values = ["a", "b", "c", "d"]
    assert all(t.field.item_str.all_values == ["a", "b", "c", "d"])
    assert t.field.line_items[0].item_str == "a"
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": ITEM_STR_ID_1, "value": {"content": {"value": "a"}}},
        {"op": "replace", "id": ITEM_STR_ID_2, "value": {"content": {"value": "b"}}},
        {"op": "replace", "id": ITEM_STR_ID_3, "value": {"content": {"value": "c"}}},
        {"op": "replace", "id": "item_str_3", "value": {"content": {"value": "d"}}},
    ]

    with pytest.raises(TypeError, match=".*change size.*"):
        t.field.item_str.all_values = ["a", "b", "c", "d", "e"]
    with pytest.raises(TypeError, match=".*change size.*"):
        t.field.item_str.all_values.append("e")
    with pytest.raises(TypeError, match=".*change size.*"):
        t.field.item_str.all_values.remove("a")


def test_multivalue_tuple_assignment_to_empty() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, **field_values)
    override_field_values(t.field, **li_values)

    # Test appending line item to initially empty line_items_empty
    t.field.line_items_empty.append({"item_empty_str": t.field.str, "item_empty_number": t.field.number})
    assert all(t.field.item_empty_str.all_values == ["CZ123456"])
    assert all(t.field.item_empty_number.all_values == [42])
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "add",
            "id": LINE_ITEMS_EMPTY_ID,
            "value": [
                {
                    "schema_id": "item_empty_str",
                    "content": {"value": "CZ123456"},
                },
                {"schema_id": "item_empty_str2", "content": {"value": ""}},
                {
                    "schema_id": "item_empty_number",
                    "content": {"value": "42.0"},
                },
                {"schema_id": "item_empty_number2", "content": {"value": ""}},
                {"schema_id": "item_empty_enum_number", "content": {"value": ""}},
            ],
        }
    ]


def test_multivalue_tuple_assignment() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, **li_values)

    # Test assigning line_items to line_items2
    with pytest.raises(ValueError, match="Attempt to set columns.*to a tuple expecting.*"):
        t.field.line_items2 = t.field.line_items
    with pytest.raises(ValueError, match=".* not a member of the tuple"):
        t.field.line_items2 = [{"item_str": row.item_str, "item_number": row.item_number} for row in t.field.line_items]
    t.field.line_items2 = [{"item2_str": row.item_str, "item2_number": row.item_number} for row in t.field.line_items]
    assert all(t.field.item2_str.all_values == ["Ab-c-d", "Ef-g-h", "Ijk", "Lmn"])
    assert [row.item2_str for row in t.field.line_items2] == ["Ab-c-d", "Ef-g-h", "Ijk", "Lmn"]
    assert [row.item2_number for row in t.field.line_items2] == [1, 2, 3, 4]
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": ITEM2_STR_ID, "value": {"content": {"value": "Ab-c-d"}}},
        {"op": "replace", "id": ITEM2_NUMBER_ID, "value": {"content": {"value": "1.0"}}},
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Ef-g-h"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "2.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Ijk"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "3.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Lmn"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "4.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
    ]
    assert [row._index == i for i, row in enumerate(t.field.line_items2)]

    # Test assigning some synthetic data to an item
    t.field.line_items2[2] = {"item2_str": "Xyz", "item2_number": 39}
    assert [row.item2_str for row in t.field.line_items2] == ["Ab-c-d", "Ef-g-h", "Xyz", "Lmn"]
    assert [row.item2_number for row in t.field.line_items2] == [1, 2, 39, 4]
    assert t.field.line_items[2].item_str == "Ijk"
    assert t.field.line_items[2].item_number == 3
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": ITEM2_STR_ID, "value": {"content": {"value": "Ab-c-d"}}},
        {"op": "replace", "id": ITEM2_NUMBER_ID, "value": {"content": {"value": "1.0"}}},
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Ef-g-h"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "2.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Xyz"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "39"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Lmn"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "4.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
    ]
    assert [row._index == i for i, row in enumerate(t.field.line_items2)]

    # Test assigning a longer list
    t.field.line_items2 += [{"item2_str": "Xyz", "item2_number": 39}]
    assert len(t.field.line_items2) == 5
    assert [row.item2_str for row in t.field.line_items2] == ["Ab-c-d", "Ef-g-h", "Xyz", "Lmn", "Xyz"]
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": ITEM2_STR_ID, "value": {"content": {"value": "Ab-c-d"}}},
        {"op": "replace", "id": ITEM2_NUMBER_ID, "value": {"content": {"value": "1.0"}}},
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Ef-g-h"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "2.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Xyz"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "39"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Lmn"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "4.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "id": LINE_ITEMS2_ID,
            "op": "add",
            "value": [
                {
                    "schema_id": "item2_str",
                    "content": {
                        "value": "Xyz",
                    },
                },
                {
                    "schema_id": "item2_str2",
                    "content": {
                        "value": "",
                    },
                },
                {
                    "schema_id": "item2_number",
                    "content": {
                        "value": "39",
                    },
                },
                {
                    "schema_id": "item2_number2",
                    "content": {
                        "value": "",
                    },
                },
            ],
        },
    ]
    assert [row._index == i for i, row in enumerate(t.field.line_items2)]

    # Test assigning a shorter list
    t.field.line_items2 = t.field.line_items2[:-2]
    assert len(t.field.line_items2) == 3
    assert [row.item2_str for row in t.field.line_items2] == ["Ab-c-d", "Ef-g-h", "Xyz"]
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "replace", "id": ITEM2_STR_ID, "value": {"content": {"value": "Ab-c-d"}}},
        {"op": "replace", "id": ITEM2_NUMBER_ID, "value": {"content": {"value": "1.0"}}},
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Ef-g-h"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "2.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Xyz"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "39"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
    ]
    assert [row._index == i for i, row in enumerate(t.field.line_items2)]

    # Test swapping rows
    t.field.line_items2[0], t.field.line_items2[1] = t.field.line_items2[1], t.field.line_items2[0]
    assert [row.item2_str for row in t.field.line_items2] == ["Ef-g-h", "Ab-c-d", "Xyz"]
    assert [row.item2_number for row in t.field.line_items2] == [2, 1, 39]
    response = t.hook_response()
    assert response["operations"] == [
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Ab-c-d"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "1.0"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {
            "op": "add",
            "id": LINE_ITEMS2_ID,
            "value": [
                {"schema_id": "item2_str", "content": {"value": "Xyz"}},
                {"schema_id": "item2_str2", "content": {"value": ""}},
                {"schema_id": "item2_number", "content": {"value": "39"}},
                {"schema_id": "item2_number2", "content": {"value": ""}},
            ],
        },
        {"op": "replace", "id": ITEM2_STR_ID, "value": {"content": {"value": "Ef-g-h"}}},
        {"op": "replace", "id": ITEM2_NUMBER_ID, "value": {"content": {"value": "2.0"}}},
    ]
    assert [row._index == i for i, row in enumerate(t.field.line_items2)]

    # The column accessor should still work fine
    assert all(t.field.item2_str.all_values == ["Ef-g-h", "Ab-c-d", "Xyz"])

    # Of course nothing should affect the source line_items
    assert [row.item_str for row in t.field.line_items] == ["Ab-c-d", "Ef-g-h", "Ijk", "Lmn"]
    assert [row._index == i for i, row in enumerate(t.field.line_items)]


def test_multivalue_tuple_listops() -> None:
    t = TxScript.from_payload(mkpayload())  # noqa: F405
    override_field_values(t.field, **li_values)

    assert [row.item_str for row in t.field.line_items] == ["Ab-c-d", "Ef-g-h", "Ijk", "Lmn"]
    del t.field.line_items[1]
    assert [row.item_str for row in t.field.line_items] == ["Ab-c-d", "Ijk", "Lmn"]
    assert all(t.field.item_str.all_values == ["Ab-c-d", "Ijk", "Lmn"])
    response = t.hook_response()
    assert response["operations"] == [{"op": "remove", "id": LINE_ITEM_ID_2}]
    assert [row._index == i for i, row in enumerate(t.field.line_items)]

    t.field.line_items.append(t.field.line_items[0])
    assert [row.item_str for row in t.field.line_items] == ["Ab-c-d", "Ijk", "Lmn", "Ab-c-d"]
    assert all(t.field.item_str.all_values == ["Ab-c-d", "Ijk", "Lmn", "Ab-c-d"])
    t.field.line_items[0].item_str = "Abc"
    assert [row.item_str for row in t.field.line_items] == ["Abc", "Ijk", "Lmn", "Ab-c-d"]
    assert all(t.field.item_str.all_values == ["Abc", "Ijk", "Lmn", "Ab-c-d"])
    assert is_empty(t.field.line_items[-1].item_formula_str)  # noqa: F405
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "remove", "id": LINE_ITEM_ID_2},
        {
            "op": "add",
            "id": LINE_ITEMS_ID,
            "value": [
                {"schema_id": "item_str", "content": {"value": "Ab-c-d"}},
                {"schema_id": "item_str2", "content": {"value": ""}},
                {"schema_id": "item_number", "content": {"value": "1.0"}},
                {"schema_id": "item_number2", "content": {"value": ""}},
            ],
        },
        {"op": "replace", "id": ITEM_STR_ID_1, "value": {"content": {"value": "Abc"}}},
    ]
    assert [row._index == i for i, row in enumerate(t.field.line_items)]

    t.field.line_items.insert(1, {"item_str": "Xyz", "item_number": 39})
    t.field.line_items[1].item_number = 42
    assert [row.item_str for row in t.field.line_items] == ["Abc", "Xyz", "Ijk", "Lmn", "Ab-c-d"]
    assert all(t.field.item_str.all_values == ["Abc", "Xyz", "Ijk", "Lmn", "Ab-c-d"])
    assert all(t.field.item_number.all_values == [1, 42, 3, 4, 1])
    response = t.hook_response()
    assert response["operations"] == [
        {"op": "remove", "id": LINE_ITEM_ID_2},
        {
            "op": "add",
            "id": LINE_ITEMS_ID,
            "value": [
                {"schema_id": "item_str", "content": {"value": "Lmn"}},
                {"schema_id": "item_str2", "content": {"value": ""}},
                {"schema_id": "item_number", "content": {"value": "4.0"}},
                {"schema_id": "item_number2", "content": {"value": ""}},
            ],
        },
        {"op": "replace", "id": ITEM_STR_ID_1, "value": {"content": {"value": "Abc"}}},
        {
            "op": "add",
            "id": LINE_ITEMS_ID,
            "value": [
                {"schema_id": "item_str", "content": {"value": "Ab-c-d"}},
                {"schema_id": "item_str2", "content": {"value": ""}},
                {"schema_id": "item_number", "content": {"value": "1.0"}},
                {"schema_id": "item_number2", "content": {"value": ""}},
            ],
        },
        {"op": "replace", "id": "item_str_3", "value": {"content": {"value": "Ijk"}}},
        {"op": "replace", "id": "item_number_3", "value": {"content": {"value": "3.0"}}},
        {"op": "replace", "id": ITEM_STR_ID_3, "value": {"content": {"value": "Xyz"}}},
        {"op": "replace", "id": ITEM_NUMBER_ID_3, "value": {"content": {"value": "42"}}},
    ]
    assert [row._index == i for i, row in enumerate(t.field.line_items)]


def test_hook_action() -> None:
    payload = mkpayload()

    with requests_mock.Mocker() as m:
        m.post("https://elis.rossum.ai/api/v1/annotations/48635144/postpone", json={})

        t = TxScript.from_payload(payload)  # noqa: F405
        override_field_values(t.field, **field_values)
        with pytest.raises(PayloadError):
            t.annotation.action("postpone")
        assert len(m.request_history) == 0

        payload["rossum_authorization_token"] = "token"
        t = TxScript.from_payload(payload)  # noqa: F405
        override_field_values(t.field, **field_values)
        t.annotation.action("postpone")
        assert len(m.request_history) == 1
