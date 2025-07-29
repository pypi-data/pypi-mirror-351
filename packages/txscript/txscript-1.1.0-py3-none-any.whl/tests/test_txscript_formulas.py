"""
An assortment of real-world inspired examples of formula fields txscript code.
"""

import datetime
from typing import Any

import pytest

from lib.txscript.tests.constants import (
    ITEM_NUMBER_ID_1,
    ITEM_NUMBER_ID_3,
    ITEM_STR2_ID_1,
    ITEM_STR2_ID_2,
    ITEM_STR_ID_2,
    STR_ID,
)
from lib.txscript.tests.helpers import exec_test_formula, exec_test_row_formula


@pytest.mark.parametrize(
    "code",
    (
        """
if field.str == "dDocument_Items":
    f"G{field.date.month:02} {field.str2}"
elif field.str == "dDocument_Service":
    f"S{field.date.month:02} {field.str2}"
else:
    show_error("unknown code", field.str)
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        ({"str": "dDocument_Items", "str2": "CZ123456", "date": "2023-05-22"}, "G05 CZ123456"),
        ({"str": "dDocument_Service", "str2": "CZ123456", "date": "2023-05-22"}, "S05 CZ123456"),
        ({"str": "dDocument_Service", "date": "2023-05-22"}, "S05 "),
        ({"str": "dDocument_Service"}, AttributeError),
        (
            {"str": "nothing", "str2": "CZ123456", "date": "2023-05-22"},
            {"messages": [{"type": "error", "content": "unknown code", "id": STR_ID, "source_id": STR_ID}]},
        ),
        (
            {"str": "", "str2": "CZ123456", "date": "2023-05-22"},
            {"messages": [{"type": "error", "content": "unknown code", "id": STR_ID, "source_id": STR_ID}]},
        ),
    ),
)
def test_calcstring_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
item_total_base = field.item_number.all_values * field.item_number2.all_values
field.number - sum(item_total_base)
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "number": 1000,
                "line_items": [
                    {"item_number": 100, "item_number2": 2},
                    {"item_number": 50, "item_number2": 4},
                    {"item_number": 300, "item_number2": 2},
                ],
            },
            0,
        ),
        (
            {
                "number": 900,
                "line_items": [
                    {"item_number": 100, "item_number2": 2},
                    {"item_number": 50, "item_number2": 4},
                    {"item_number": 300, "item_number2": 2},
                ],
            },
            -100,
        ),
        (
            {
                "number": 1000,
                "line_items": [
                    {"item_number": 100, "item_number2": 1},
                    {"item_number": 50, "item_number2": 4},
                    {"item_number": 300, "item_number2": 2},
                ],
            },
            100,
        ),
        (
            {
                "line_items": [
                    {"item_number": 100, "item_number2": 2},
                    {"item_number": 50, "item_number2": 4},
                    {"item_number": 300, "item_number2": 2},
                ]
            },
            TypeError,
        ),
        (
            {
                "number": 900,
                "line_items": [
                    {"item_number": 100, "item_number2": 2},
                    {"item_number": 50, "item_number2": 4},
                    {"item_number": None, "item_number2": None},
                ],
            },
            TypeError,
        ),
    ),
)
def test_calcrounding_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
now = field.date2  # date.today()
if field.date.month == now.month and field.date.year == now.year:
    if field.str == "L":
        show_error("current month posting period not open yet")
    field.date
else:
    if field.str != "L":
        show_warning(content="posting in previous month")
        field.date
    else:
        show_warning("posting in locked previous month, shifting posting date")
        date(now.year, now.month, 1)
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        ({"date": "2023-05-20", "date2": "2023-05-31", "str": ""}, datetime.date.fromisoformat("2023-05-20")),
        (
            {"date": "2023-05-20", "date2": "2023-05-31", "str": "L"},
            {
                "messages": [{"type": "error", "content": "current month posting period not open yet"}],
                "value": datetime.date.fromisoformat("2023-05-20"),
            },
        ),
        (
            {"date": "2023-05-20", "date2": "2023-06-21", "str": ""},
            {
                "messages": [{"type": "warning", "content": "posting in previous month", "source_id": -1}],
                "value": datetime.date.fromisoformat("2023-05-20"),
            },
        ),
        (
            {"date": "2023-05-20", "date2": "2023-06-21", "str": "L"},
            {
                "messages": [{"type": "warning", "content": "posting in locked previous month, shifting posting date"}],
                "value": datetime.date.fromisoformat("2023-06-01"),
            },
        ),
        ({"date": "", "date2": "2023-05-31", "str": ""}, AttributeError),
        ({"date": "", "date2": "2023-05-31", "str": "L"}, AttributeError),
    ),
)
def test_calcdate_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
date_issue_1stmonth = field.date.replace(day=1)
date_posting = date_issue_1stmonth - timedelta(days=1)
date_posting.strftime("%Y-%m")
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        ({"date": "2023-05-20"}, "2023-04"),
        ({"date": "2023-05-01"}, "2023-04"),
        ({"date": "2023-04-30"}, "2023-03"),
        ({"date": "2023-01-30"}, "2022-12"),
        ({"date": ""}, AttributeError),
    ),
)
def test_calcperiod_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


# "I need the error message I have now on the line items to show up on a header field. One way
# is to copy the value from the line to the header field and set the rule to the header."
@pytest.mark.parametrize(
    "code",
    (
        """
if len(field.item_number.all_values) > 0:
    field.item_number.all_values[0]
else:
    None
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "line_items": [
                    {"item_number": 100},
                ],
            },
            100,
        ),
        (
            {
                "line_items": [
                    {"item_number": 100},
                    {"item_number": 50},
                    {"item_number": 300},
                ],
            },
            100,
        ),
        (
            {},
            None,
        ),
        (
            {
                "line_items": [
                    {"item_number": None},
                    {"item_number": 50},
                    {"item_number": 300},
                ],
            },
            None,
        ),
    ),
)
def test_firstli_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
for item_number in field.item_number.all_values:
    if item_number and item_number >= 100:
        show_warning("Value is too large", item_number)
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "line_items": [
                    {"item_number": 50},
                ],
            },
            {},
        ),
        (
            {
                "line_items": [
                    {"item_number": 100},
                ],
            },
            {"messages": [{"type": "warning", "content": "Value is too large", "id": ITEM_NUMBER_ID_1}]},
        ),
        (
            {
                "line_items": [
                    {"item_number": 100},
                    {"item_number": 50},
                    {"item_number": 300},
                ],
            },
            {
                "messages": [
                    {"type": "warning", "content": "Value is too large", "id": ITEM_NUMBER_ID_1},
                    {"type": "warning", "content": "Value is too large", "id": ITEM_NUMBER_ID_3},
                ]
            },
        ),
        (
            {
                "line_items": [
                    {"item_number": None},
                    {"item_number": 50},
                    {"item_number": 300},
                ],
            },
            {"messages": [{"type": "warning", "content": "Value is too large", "id": ITEM_NUMBER_ID_3}]},
        ),
    ),
)
def test_warning_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
group_total = 0
for row in field.line_items:
    if row.item_str == field.item_str:
        group_total += row.item_number
group_total
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "line_items": [
                    {"item_str": "1", "item_number": 1},
                    {"item_str": "1", "item_number": 2},
                    {"item_str": "A5", "item_number": 4},
                ],
            },
            {"values": [3, 3, 4]},
        ),
    ),
)
def test_liiter_in_row_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_row_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
summary = ""
for tax_code in sorted(set(field.item_str.all_values)):
    amounts = [fallback(row.item_number, 0) for row in field.line_items if row.item_str == tax_code]
    amount_sum = round(sum(amounts))
    summary += f"{tax_code}: {amount_sum}\\n"
summary
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "line_items": [
                    {"item_str": "1", "item_number": 1},
                    {"item_str": "1", "item_number": 2},
                    {"item_str": "A5", "item_number": 4},
                ],
            },
            {"values": [3, 3, 4]},
        ),
    ),
)
def test_liiter_in_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
substitute(r"[^\\w\\d]", r"", field.str)
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        ({"str": ""}, ""),
        ({"str": "CZ1234"}, "CZ1234"),
        ({"str": " _Hi: 1-2"}, "_Hi12"),
        ({"str": "%"}, ""),
    ),
)
def test_substitute_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
if field.str != "":
    order_id = substitute("^PO", "", field.str)
    order_id = substitute("^P0", "", order_id)
    order_id
else:
    field.str2
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        ({"str": "", "str2": ""}, ""),
        ({"str": "", "str2": "POPO"}, "POPO"),
        ({"str": "1234", "str2": "POPO"}, "1234"),
        ({"str": "PO1234", "str2": "POPO"}, "1234"),
        ({"str": "P01234", "str2": "POPO"}, "1234"),
    ),
)
def test_posubstitute_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
for row in field.line_items:
    if re.search(r"\\s", row.item_str):
        show_error("Item number is wrong", row.item_str)
    if row.item_str2 == "":
        show_warning("Item status does not exist", row.item_str2)
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "line_items": [
                    {"item_str": "x11", "item_str2": "exists"},
                    {"item_str": "x11", "item_str2": "exists"},
                    {"item_str": "x11", "item_str2": "exists"},
                ],
            },
            {},
        ),
        (
            {
                "line_items": [
                    {"item_str": "", "item_str2": ""},
                    {"item_str": "x11", "item_str2": "exists"},
                    {"item_str": "x11", "item_str2": "exists"},
                ],
            },
            {"messages": [{"type": "warning", "content": "Item status does not exist", "id": ITEM_STR2_ID_1}]},
        ),
        (
            {
                "line_items": [
                    {"item_str": "x11", "item_str2": "exists"},
                    {"item_str": "x 12", "item_str2": ""},
                    {"item_str": "x11", "item_str2": "exists"},
                ],
            },
            {
                "messages": [
                    {"type": "error", "content": "Item number is wrong", "id": ITEM_STR_ID_2},
                    {"type": "warning", "content": "Item status does not exist", "id": ITEM_STR2_ID_2},
                ]
            },
        ),
    ),
)
def test_liwarning_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
if field.str == "credit_note":
    show_error("Credit note.")
    automation_blocker("Credit note")
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        ({"str": "debit_note"}, {}),
        (
            {"str": "credit_note"},
            {
                "messages": [{"type": "error", "content": "Credit note."}],
                "automation_blockers": [{"content": "Credit note"}],
            },
        ),
    ),
)
def test_strblock_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
import json
data = {
    "string": field.str,
    "number": field.number,
    "date": field.date,
    "boolean": field.bool_true,
    "array": [field.number, field.str],
    "line_items": field.line_items
}
json.dumps(data, sort_keys=True) # Last expression is the result
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "str": "test string",
                "number": 42.5,
                "date": "2023-05-22",
                "bool_true": True,
                "line_items": [{"item_number": 123, "item_str": "item1"}, {"item_number": 456, "item_str": "item2"}],
            },
            '{"array": [42.5, "test string"], "boolean": true, "date": "2023-05-22", "line_items": [{"item_formula_str": "", "item_number": 123.0, "item_number2": null, "item_str": "item1", "item_str2": ""}, {"item_formula_str": "", "item_number": 456.0, "item_number2": null, "item_str": "item2", "item_str2": ""}], "number": 42.5, "string": "test string"}',
        ),
    ),
)
def test_json_serializable(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
if not is_empty(field.item_number):
    field.item_number + field.number
elif not is_empty(field.item_number2) and not is_empty(field.item_str2):
    # (total - tax) / quantity
    (field.item_number2 - default_to(float(field.item_str), 0)) / float(field.item_str2)
elif not is_empty(field.item_str) and not is_empty(field.item_str2):
    # base / quantity)
    # N.B. string fields are used just due to shortage of columns
    float(field.item_str) / float(field.item_str2)
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "line_items": [
                    {},
                    {"item_str": "100"},
                    {"item_str2": "5"},
                ],
            },
            {"values": [None, None, None]},
        ),
        (
            {
                "line_items": [
                    {"item_str": "100", "item_str2": "5", "item_number": 50},
                    {"item_str": "100", "item_str2": "5", "item_number2": 1100},
                    {"item_str": "100", "item_str2": "5"},
                ],
                "number": 1,
            },
            {"values": [51, 200, 20]},
        ),
    ),
)
def test_liamount_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_row_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
if field.item_number >= 30000:
    field._index
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "line_items": [{}, {"item_number": 50}, {"item_number": 500000}],
            },
            {"values": [TypeError, None, 2]},
        ),
    ),
)
def test_licond_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_row_formula(code, field_values, result)


@pytest.mark.parametrize(
    "code",
    (
        """
if field.str == 'C10829' and field.item_str == "35":
    field.item_number * field.item_number2
""",
    ),
)
@pytest.mark.parametrize(
    ("field_values", "result"),
    (
        (
            {
                "str": "C10829",
                "line_items": [
                    {"item_str": "36"},
                    {"item_str": "35", "item_number": None, "item_number2": 2},
                    {"item_str": "35", "item_number": 50, "item_number2": 2},
                ],
            },
            {"values": [None, TypeError, 100]},
        ),
        (
            {
                "str": "D10829",
                "line_items": [
                    {"item_str": "36"},
                    {"item_str": "35", "item_number": 50},
                    {"item_str": "35", "item_number": 50, "item_number2": 2},
                ],
            },
            {"values": [None, None, None]},
        ),
    ),
)
def test_liamountcond_formula(
    code: str,
    field_values: str,
    result: Any,
) -> None:
    exec_test_row_formula(code, field_values, result)
