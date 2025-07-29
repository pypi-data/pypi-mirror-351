#!/usr/bin/env python3
"""
Standalone benchmark script that evaluates formulas of a given annotation+schema within the runtime.
"""

import argparse
import cProfile
import json
import pstats

from txscript.eval import eval_strings
from txscript.fields import Fields
from txscript.flatdata import FieldsFlatData
from txscript.txscript import TxScriptAnnotationContent


def extract_formulas(schema: dict) -> dict:
    formulas = {}
    for schema_id, schema_node in schema.items():
        if "formula" in schema_node:
            formulas[schema_id] = {"code": schema_node["formula"], "type": "formula"}
    return formulas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark code within the runtime.")
    parser.add_argument("annotation_file", nargs="?", help="Path to the annotation content JSON file")
    parser.add_argument("schema_file", nargs="?", help="Path to the schema JSON file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Set up the profiler
    profiler = cProfile.Profile()
    profiler.enable()

    with open(args.annotation_file, "r") as f:
        annotation = json.load(f)
    with open(args.schema_file, "r") as f:
        schema = json.load(f)
    field = Fields(FieldsFlatData.from_tree(schema["content"], annotation["content"]))
    t = TxScriptAnnotationContent(field)

    formulas = extract_formulas(field._data.schema)

    eval_strings(formulas, t, debug=args.debug)

    if args.debug:
        print(t.field._get_operations())
        print(t._messages)
        print(t._automation_blockers)

    # Stop the profiler and print statistics
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats(pstats.SortKey.CUMULATIVE)
    stats.dump_stats("standalone_profile.prof")
    print("\nProfiling data has been written to standalone_profile.prof")
    print("To view the results, you can use a tool like snakeviz or run:")
    print("python -m pstats standalone_profile.prof")
