import datetime
from typing import Any

import pytest

from lib.txscript.tests.constants import STR2_ID
from lib.txscript.tests.helpers import mkpayload, override_field_values
from lib.txscript.txscript import TxScript
from lib.txscript.txscript.formula import Formula

field_values = {
    "number": 42,
    "enum": "tax_invoice",
    "enum_number": 2,
    "str": "CZ123456",
    "date": "2023-05-22",
    "multistr_inner": ["foo", "bar"],
    "line_items": [
        {"item_str": "Ab-c-d", "item_str2": "a", "item_number": 0, "item_number2": 10},
        {"item_str": "Ef-g-h", "item_str2": "", "item_number": 1, "item_number2": 20},
        {"item_str": "Ij-k-l", "item_str2": "c", "item_number": 2, "item_number2": 30},
    ],
    "line_items2": [],
}


@pytest.mark.parametrize(
    ("expression", "result"),
    (
        # Basic math
        ("1 + 1", 2),
        ("field.number + 1", 43),
        ("sum(field.item_number.all_values) + 1", 4),
        ("0.1 + 0.2 == 0.3", False),
        ("round(0.1 + 0.2, 2) == round(0.3, 2)", True),
        ("1 + 1.1", 2.1),
        ("round(field.number + 0.123)", 42),
        ("round(field.number + 0.123, 2)", 42.12),
        ("pow(field.number, 2)", 1764),
        ("divmod(50, field.number)", (1, 8)),
        ("field.enum_number * 2", 4),
        # Date manipulations
        ("date.today()", datetime.datetime.now(datetime.UTC).date()),
        ("field.date + timedelta(days=1)", datetime.date(2023, 5, 23)),
        ("field.date + timedelta(hours=3*24)", datetime.date(2023, 5, 25)),
        ("field.date + timedelta(days=int(field.number))", datetime.date(2023, 7, 3)),
        ("field.date.strftime('%Y%m%d')", "20230522"),
        ("(field.date - default_to(field.date2, date(2023, 5, 1))).days", 21),
        # Basic strings
        ("field.enum", "tax_invoice"),
        ("f'{field.number:.2f}'", "42.00"),
        ("f'{field.str} {field.date.strftime(\"%Y\")}'", "CZ123456 2023"),
        ("substitute(r'^[A-Z][A-Z]', r'', field.str)", "123456"),
        ("substitute(r'^[A-Z][a-z]', r'', field.str)", "CZ123456"),
        ("substitute(r'-', r'', field.item_str.all_values[0])", "Abcd"),
        ("substitute(r'-', r'', field.item_str[0])", TypeError),
        # Basic comparisons
        ("10 < 20 < 30", True),
        ("field.number < 3", False),
        ("field.number > 3", True),
        ("field.number == 42", True),
        # all/any logic
        ("all(field.item_number.all_values > 0)", False),
        ("any(field.item_number.all_values > 0)", True),
        # conditional logic
        ("if any(field.item_number.all_values > 0): 10", 10),
        ("if all(field.item_number.all_values > 0): 10", None),
        ("if field.item_number.all_values > 0: 10", ValueError),
        # Operations on the line items
        ("'bar' in field.multistr_inner.all_values", True),
        ("'baz' in field.multistr_inner.all_values", False),
        ("all(field.item_number == field.item_number2)", TypeError),
        ("all(field.item_number.all_values == field.item_number2.all_values)", False),
        ("all(field.item_number.all_values * 10 == field.item_number2.all_values)", False),
        ("all((field.item_number.all_values + 2) * 10 == field.item_number2.all_values)", False),
        ("all((field.item_number.all_values + 1) * 10 == field.item_number2.all_values)", True),
        ("sum(field.item_number.all_values * field.item_number2.all_values)", 80),
        ("min(field.item_number.all_values)", 0),
        ("max(field.item_number.all_values)", 2),
        ("len(field.multistr_inner.all_values)", 2),
        ("len(field.multistr_outer.all_values)", 2),
        ("sum(round(field.item_number.all_values))", sum([0, 1, 2])),
        ("sum(pow(0.5, field.item_number.all_values))", sum([1, 0.5, 0.25])),
        ("divmod(field.item_number.all_values, 2)[1]", (0, 1)),
        ("sum(field.item2_number.all_values)", 0),
        ("sum(field.item_empty_number.all_values)", 0),
        ("''.join(field.multistr_empty_inner.all_values)", ""),
        ("''.join(field.multistr_empty_outer.all_values)", ""),
        # None, empty string behavior
        ("field.str2 == ''", True),
        ("field.str2 == None", False),
        ("field.str2 != None", True),
        ("field.str2 != ''", False),
        ("field.number2 == 42", False),
        ("field.number2 == None", True),
        pytest.param(
            "field.number2 is None",
            TypeError,
            marks=pytest.mark.xfail(
                reason="'is None' must not be used due to *Value proxies, we should prohibit it at AST level as it's too standard in Python"
            ),
        ),
        ("field.date2 == None", True),
        ("field.date2 != None", False),
        ("substitute(r'^[A-Z][A-Z]', r'', field.str2)", ""),
        ("field.number2 + 5", TypeError),
        ("field.date2 - field.date", TypeError),
        ("field.number_nonpresent", AttributeError),
        # Getting default value
        ("None", None),
        ("field.str2", ""),
        ("field.number2", None),
        ("default_to(field.str, 'x')", "CZ123456"),
        ("default_to(field.str2, 'x')", "x"),
        ("default_to(field.number, 5)", 42),
        ("default_to(field.number2, 5)", 5),
        ("default_to(field.number2, field.number)", 42),
        ("default_to(field.date, date(2023, 5, 1))", datetime.date(2023, 5, 22)),
        ("default_to(field.date2, date(2023, 5, 1))", datetime.date(2023, 5, 1)),
        ("10 if not is_empty(field.str2) else 20", 20),
        ("10 if is_empty(field.str2) else 20", 10),
        ("10 if not is_empty(field.number2) else 20", 20),
        ("10 if is_empty(field.number2) else 20", 10),
        ("fallback(field.number2, 5)", 5),  # temporary compatibility
        ("10 if is_set(field.str2) else 20", 20),  # temporary compatibility
        ("''.join(default_to(field.item_str2.all_values, '_'))", "a_c"),
        # Attribute access
        ("field.str2.attr.id", STR2_ID),
        ("field.str2.attr.value", ""),
        ("field.str2.attr.rir_confidence", None),
        ("field.str2.attr.hidden", False),
        ("field.str2.attr.unknown", AttributeError),
        ("field.date.attr.value", "2023-05-22"),
        ("field.number.attr.page", 1),
        ("field.number.attr.constraints['required']", False),
        ("field.date2.attr.value", ""),
        ("field.enum.attr.options[0].label", "Tax Invoice"),
        ("field.enum.attr.options[0].value", "tax_invoice"),
        ("field.enum_number.attr.options[0].value", 1),
        # Attribute access (compatibility whitelist, deprecated as of 2024-09).
        ("field.str2.id", STR2_ID),
        ("field.str2.value", ""),
        ("field.str2.rir_confidence", None),
        ("field.str2.hidden", AttributeError),
        ("field.str2.unknown", AttributeError),
        ("field.date.value", "2023-05-22"),
        ("field.number.page", AttributeError),
        ("field.number.constraints['required']", AttributeError),
        ("field.date2.value", ""),
        ("field.enum.options[0].value", "tax_invoice"),
        # Rules-only boolean
        ("field.bool", None),
        ("field.bool_true", True),
        ("field.bool_false", False),
    ),
)
def test_execute(
    expression: str,
    result: Any,
) -> None:
    t = TxScript.from_payload(mkpayload())
    override_field_values(t.field, **field_values)
    formula = Formula("field", expression)
    if isinstance(result, type):
        with pytest.raises(result):
            formula.evaluate(t)
    else:
        assert formula.evaluate(t) == result
