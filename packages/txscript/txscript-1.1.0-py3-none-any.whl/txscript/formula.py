from __future__ import annotations

import ast
import importlib
from typing import TYPE_CHECKING, Any, Optional, Set

from .computed import Computed
from .txscript import TxScriptAnnotationContent  # noqa: TC002

if TYPE_CHECKING:
    from types import CodeType

    from .computed import Promise


# get __dict__ with builtins of builtins.py in this directory
builtins = importlib.import_module(".builtins", __package__)


class FieldReferenceVisitor(ast.NodeVisitor):
    TARGET_METHOD_NAMES = {"show_info", "show_warning", "show_error", "automation_blocker"}
    LINE_ITEM_ATTRIBUTES = {"all_values"}

    def __init__(self) -> None:
        super().__init__()
        self.schema_ids: Set[str] = set()
        self.schema_all_values: Set[str] = set()
        self.target_schema_ids: Set[str] = set()

        # the additional keywords are collected and not removed after leaving the loop context
        self.field_keywords: Set[str] = {"field", "row"}
        self.additional_keywords: Set[str] = set()

    def get_schema_id(self, node: ast.expr) -> str | None:
        next_node = None
        schema_id = None

        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "getattr":
            next_node = node.args[0]
            schema_id = getattr(node.args[1], "value", None)

        if isinstance(node, ast.Attribute):
            next_node = node.value
            schema_id = node.attr

        if next_node and schema_id and self.is_field_expression(next_node):
            return schema_id

        return None

    def is_field_expression(self, node: ast.expr) -> bool:
        """Can be either
        - keyword: 'field' or 'row'
        - field-like expression: 'field.line_items[0]'
        """
        if isinstance(node, ast.Name):
            return getattr(node, "id", "") in self.field_keywords | self.additional_keywords
        elif isinstance(node, ast.Subscript):
            return self.get_schema_id(node.value) is not None

        return False

    def _check_for_field_access(self, node: ast.Call | ast.Attribute) -> None:
        if schema_id := self.get_schema_id(node):
            is_target = getattr(node, "__is_target", False)

            if is_target:
                self.target_schema_ids.add(schema_id)
            else:
                self.schema_ids.add(schema_id)

    def _register_additional_keyword(self, expr: ast.For | ast.comprehension) -> None:
        if self.get_schema_id(expr.iter):
            target = getattr(expr.target, "id", "")
            self.additional_keywords.add(target)

    def visit_For(self, node: ast.For) -> None:
        self._register_additional_keyword(node)
        super().generic_visit(node)

    def _resolve_comp_visit(self, node: ast.ListComp | ast.SetComp | ast.DictComp) -> None:
        comprehension = node.generators[0]
        self._register_additional_keyword(comprehension)
        super().generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._resolve_comp_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._resolve_comp_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._resolve_comp_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self._check_for_field_access(node)

        if getattr(node.func, "id", "") in self.TARGET_METHOD_NAMES:
            if len(node.args) > 1:
                field_attr = node.args[1]
            elif field_keyword := next((k for k in node.keywords if k.arg == "field"), None):
                field_attr = field_keyword.value
            else:
                field_attr = None

            if field_attr:
                setattr(field_attr, "__is_target", True)

        super().generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in self.LINE_ITEM_ATTRIBUTES:
            if isinstance(node.value, ast.Call) or isinstance(node.value, ast.Attribute):
                if schema_id := self.get_schema_id(node.value):
                    self.schema_all_values.add(schema_id)

        self._check_for_field_access(node)
        super().generic_visit(node)


class ExpressionGatheringTransformer(ast.NodeTransformer):
    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        call = ast.Call(func=ast.Name(id="_eg", ctx=ast.Load()), args=[node.value], keywords=[])
        expr = ast.Expr(value=call, lineno=0, col_offset=0)
        return expr


class ExpressionGatherer:
    def __init__(self) -> None:
        self.last_expression_result: Any = None

    def __call__(self, x: Any) -> None:
        self.last_expression_result = x


class Formula(Computed):
    def __init__(self, schema_id: str, string: str, parent_multivalue_schema_id: str | None = None) -> None:
        self.schema_id = schema_id
        self.string = string
        self.code: Optional[CodeType] = None

        # Return value of formula is either `return` statement value or value of
        # the last executed expression.
        self.tree = ast.parse(self.string, self.schema_id, "exec")

        visitor = FieldReferenceVisitor()
        visitor.visit(self.tree)
        self.dependencies = visitor.schema_ids
        self.all_value_dependencies = visitor.schema_all_values
        self.targets = visitor.target_schema_ids

        if parent_multivalue_schema_id:
            if "_index" in self.dependencies:
                self.dependencies.remove("_index")
                self.dependencies.add(parent_multivalue_schema_id)

            if "_index" in self.targets:
                self.targets.remove("_index")
                self.targets.add(parent_multivalue_schema_id)

    def evaluate(self, t: TxScriptAnnotationContent) -> Any | Promise:
        _eg = ExpressionGatherer()

        globals_ = dict(
            **t.__dict__,
            **t._formula_methods(),
            **builtins.__dict__,
            _action=t._action,
            _eg=_eg,
        )

        if not self.code:
            transformer = ExpressionGatheringTransformer()
            transformer.visit(self.tree)
            ast.fix_missing_locations(self.tree)

            filename = f"<formula:{self.schema_id}>"
            self.code = compile(self.tree, filename, "exec")

        exec(self.code, globals_)
        return _eg.last_expression_result
