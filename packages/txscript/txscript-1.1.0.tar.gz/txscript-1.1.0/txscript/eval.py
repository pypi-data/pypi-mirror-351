from __future__ import annotations

import dataclasses
import time
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from .computed import Promise
from .datapoint import Field, FieldValueBase, MultivalueDatapointField, TableColumnValue
from .formula import Formula
from .reasoning import Reasoning
from .txscript import TxScriptAnnotationContent

if TYPE_CHECKING:
    from .computed import Computed


def toposort(computed: List[Computed]) -> List[Computed]:
    computed_by_schema_id = {f.schema_id: f for f in computed}

    sorted_computed = []

    while computed:
        independent_computed = [
            c for c in computed if all(dep not in computed_by_schema_id or dep == c.schema_id for dep in c.dependencies)
        ]
        if not independent_computed:
            raise RuntimeError(f"Cyclical dependencies: {', '.join(c.schema_id for c in computed)}")
        for c in independent_computed:
            del computed_by_schema_id[c.schema_id]
            sorted_computed.append(c)
            computed.remove(c)

    return sorted_computed


def parse_formula_exception(formula_code: str, e: Exception) -> Tuple[str, int, list[dict]]:
    lines = [""] + formula_code.split("\n")

    traceback = []
    tb = e.__traceback__
    tb_lineno = getattr(e, "lineno", 1)
    while tb:
        if tb.tb_frame.f_code.co_filename.startswith("<"):  # filter only formula source code tb_frames
            tb_lineno = tb.tb_lineno
            co_name = tb.tb_frame.f_code.co_name
            co_name = co_name if co_name != "<module>" else tb.tb_frame.f_code.co_filename
            traceback.append({"lineno": tb_lineno, "loc": co_name, "code": lines[tb_lineno].strip()})
        tb = tb.tb_next

    if not traceback and tb_lineno:
        traceback.append({"lineno": tb_lineno, "code": lines[tb_lineno].strip()})

    return f"{e.__class__.__name__}: {getattr(e, 'msg', e)}", tb_lineno, traceback


def check_deps(
    t: TxScriptAnnotationContent,
    computed: Computed,
    dp_id: int,
    updated_datapoint_ids: set[int],
) -> tuple[bool, list[FieldValueBase]]:
    deps = []
    for dep_schema_id in computed.dependencies:
        try:
            deps.append(t.field.__getattr__(dep_schema_id))
        except AttributeError:
            # get proper Traceback by evaluating the formula
            # note: we create a new TxScriptAnnotationContent to avoid side effects
            #       like adding messages or automation blockers which would normally be put inside the `t` instance
            computed.evaluate(TxScriptAnnotationContent(t.field, t.annotation))

    # the force_update_datapoint_ids is necessary when a formula field's `no_recalculation` is changed
    # or for /validate call after content/{multivalue_id}/add_empty which receives the just added columns ids
    evaluate = t.recompute_all or dp_id in t.force_update_datapoint_ids
    if not evaluate:
        dep_ids = set()
        for dep in deps:
            if isinstance(dep, TableColumnValue):
                dep_ids |= {f.attr.id for f in dep.all_values}  # add all column cell ids
                assert dep.parent_multivalue is not None
                dep_ids.add(dep.parent_multivalue.attr.id)  # add the associated multivalue id
            else:
                dep_ids.add(dep.attr.id)
        evaluate = not dep_ids.isdisjoint(updated_datapoint_ids)

    return evaluate, deps


def eval_field(
    t: TxScriptAnnotationContent,
    _readonly_context: Any,
    computed: Computed,
    field: Field,
    updated_datapoint_ids: set[int],
    debug: bool = False,
) -> None:
    dp_id = field.attrs["id"]
    try:
        if field.attrs.get("no_recalculation", False):
            if debug:
                print(f"{computed.schema_id}: (no recalculation)")
            return

        evaluate, deps = check_deps(t, computed, dp_id, updated_datapoint_ids)
        if not evaluate:
            return

        if any(dep._field.waiting for dep in deps):
            t.field.__getattr__(computed.schema_id)._field.waiting = True
            return

        with _readonly_context():
            t._computed_ids.add(dp_id)
            new_val = computed.evaluate(t)

        if isinstance(new_val, Promise):
            t._promise(computed.schema_id, **dataclasses.asdict(new_val))
            t.field.__getattr__(computed.schema_id)._field.waiting = True
            return

        t.field.__setattr__(computed.schema_id, new_val)
        updated_datapoint_ids.add(dp_id)

        if debug:
            print(f"{computed.schema_id}: {new_val}")
    except Exception as e:
        t._computed_ids.add(dp_id)
        formula_code = getattr(computed, "string", "")  # FIXME: check stacktraces for non-formulas here
        content, lineno, traceback = parse_formula_exception(formula_code, e)
        print(f"{computed.schema_id} [exc]: {content}\n{traceback}")
        t._exception(content, lineno, traceback, schema_id=computed.schema_id)


def eval_strings(fields: Dict[str, dict], t: TxScriptAnnotationContent, debug: bool = False) -> None:
    computed_fields: list[Computed] = []
    for schema_id, computeddict in fields.items():
        if computeddict["type"] == "formula":
            formula_field = t.field._get_field(schema_id)
            multivalue_of_tuple = formula_field.parent if isinstance(formula_field, MultivalueDatapointField) else None
            multivalue_schema_id = multivalue_of_tuple.schema_id if multivalue_of_tuple is not None else None
            try:
                formula = Formula(schema_id, computeddict["code"], multivalue_schema_id)
                computed_fields.append(formula)
            except SyntaxError as e:
                content, lineno, traceback = parse_formula_exception(computeddict["code"], e)
                if not multivalue_of_tuple:
                    with t.field._field_context(formula_field):
                        t._exception(content, lineno, traceback, schema_id=schema_id)
                else:
                    for row in multivalue_of_tuple.get_value():  # type: ignore[attr-defined]
                        with row._row_formula_context(t) as row_r:
                            field = row._get_field(schema_id)
                            with row._field_context(field):
                                row_r._exception(content, lineno, traceback, schema_id=schema_id)

        elif computeddict["type"] == "reasoning":
            computed_fields.append(Reasoning(schema_id, computeddict["context"]))

    # bail out if there were syntax errors
    if t._messages:
        return

    updated_datapoint_ids = set(t.updated_datapoint_ids)
    for computed in toposort(computed_fields):
        start_time = time.monotonic()
        field = t.field._get_field(computed.schema_id)
        multivalue_of_tuple = field.parent if isinstance(field, MultivalueDatapointField) else None

        if not multivalue_of_tuple:
            with t.field._field_context(field):
                eval_field(t, t.field._readonly_context, computed, field, updated_datapoint_ids, debug)
        else:
            for row in multivalue_of_tuple.get_value():  # type: ignore[attr-defined]
                with row._row_formula_context(t) as row_r:
                    field = row._get_field(computed.schema_id)
                    with row._field_context(field):
                        eval_field(row_r, t.field._readonly_context, computed, field, updated_datapoint_ids, debug)
        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"Computed {computed.schema_id} ({duration * 1000:.3f}ms)")
