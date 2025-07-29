import ast
from textwrap import dedent
from unittest import mock

import pytest

from lib.txscript.txscript.formula import Formula


@pytest.mark.parametrize(
    ("formula_code", "expected_dependencies", "expected_targets", "expected_all_value_dependencies"),
    (
        ("show_info('info', field=field.info)", [], ["info"], []),
        ("show_warning('warning', field.warning)", [], ["warning"], []),
        ("show_error('error', field.error)", [], ["error"], []),
        ("show_error('error')", [], [], []),
        ("automation_blocker('blocker', field.blocker)", [], ["blocker"], []),
        ("automation_blocker('blocker')", [], [], []),
        ("field.xyz", ["xyz"], [], []),
        ("field.item_rst.all_values", ["item_rst"], [], ["item_rst"]),
        ("field.abc", ["abc"], [], []),
        ('getattr(field, "fgh")', ["fgh"], [], []),
        ('getattr(not_field, "xxx")', [], [], []),
        ("getattr(field, schema_id)", [], [], []),
        ("getattr(field, function())", [], [], []),
        ('getattr(field, f"{schema_id}")', [], [], []),
        ('getattr(field, "item_rst2").all_values', ["item_rst2"], [], ["item_rst2"]),
        ('getattr(field.datapoint, "attr")', ["datapoint"], [], []),
        ("field.line_items[0].item_description", ["line_items", "item_description"], [], []),
    ),
)
def test_dependencies_and_targets(
    formula_code: str,
    expected_dependencies: list[str],
    expected_targets: list[str],
    expected_all_value_dependencies: list[str],
) -> None:
    formula = Formula("field", formula_code)

    assert sorted(formula.dependencies) == sorted(expected_dependencies)
    assert sorted(formula.targets) == sorted(expected_targets)
    assert sorted(formula.all_value_dependencies) == sorted(expected_all_value_dependencies)


def test_dependencies_for_multivalue_index() -> None:
    formula = Formula("field", "field._index", "multivalue")

    assert sorted(formula.dependencies) == ["multivalue"]
    assert sorted(formula.targets) == []


def test_dependencies_for_multivalue_index_getattr() -> None:
    formula = Formula("field", "getattr(field, '_index')", "multivalue")

    assert sorted(formula.dependencies) == ["multivalue"]
    assert sorted(formula.targets) == []


def test_dependencies_and_targets_for_cycle() -> None:
    formula = Formula(
        "field",
        dedent(
            """
                for line in field.line_items:
                    line.ccc
                """
        ),
    )

    assert sorted(formula.dependencies) == ["ccc", "line_items"]
    assert sorted(formula.targets) == []


@pytest.mark.parametrize(
    ("formula_code", "expected_dependencies", "expected_targets"),
    (
        ("[line.item_str for line in field.line_items]", ["line_items", "item_str"], []),
        ("{l.item_str for l in field.line_items}", ["line_items", "item_str"], []),
        ('{key.item_str: "value" for key in field.line_items}', ["line_items", "item_str"], []),
        ('[line.item_str for line in getattr(field, "line_items")]', ["line_items", "item_str"], []),
        ('[getattr(line, "item_str") for line in field.line_items]', ["line_items", "item_str"], []),
    ),
)
def test_dependencies_and_targets_comprehensions(
    formula_code: str, expected_dependencies: list[str], expected_targets: list[str]
) -> None:
    formula = Formula("field", formula_code)

    assert sorted(formula.dependencies) == sorted(expected_dependencies)
    assert sorted(formula.targets) == sorted(expected_targets)


def test_evaluate_parses_ast_just_once() -> None:
    class TxScriptX:
        def _formula_methods(self):
            return {}

        def _action(self):
            return {}

    with mock.patch("ast.parse", wraps=ast.parse) as ast_parse:
        formula = Formula("field", "0")
        formula.evaluate(TxScriptX())
        formula.evaluate(TxScriptX())

    ast_parse.assert_called_once()
