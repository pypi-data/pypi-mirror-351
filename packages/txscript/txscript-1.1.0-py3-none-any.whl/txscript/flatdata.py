from __future__ import annotations

from typing import List, Optional


def _generate_schema_dict(result: dict, schema_nodes: List[dict], parent: Optional[dict] = None) -> dict:
    for node in schema_nodes:
        schema_id = node["id"]

        # "schema_id": {schema_node...}
        node = {**node}  # shallow copy
        result[schema_id] = node
        if parent:
            # "schema_id": {schema_node..., "parent": schema_id},  // for children of multivalue or tuple fields
            result[schema_id]["parent"] = parent["id"]

        if node["category"] == "multivalue":
            # "schema_id": {schema_node... sans children, "child": schema_id},  // multivalue
            _generate_schema_dict(result, [node["children"]], node)
            node["child"] = node.pop("children")["id"]

        elif "children" in node:
            # "schema_id": {schema_node... sans children, "children": [schema_id...]},  // section, tuple
            _generate_schema_dict(result, node["children"], node)
            node["children"] = [child["id"] for child in node["children"]]

    return result


def _initialize_objects_dict(schema_flat: dict) -> dict:
    result = {}
    for schema_id, schema_node in schema_flat.items():
        result[schema_id] = {"schema_id": schema_id}
        if "parent" in schema_node and schema_flat[schema_node["parent"]]["category"] in ("multivalue", "tuple"):
            result[schema_id]["all_objects"] = []
    return result


def _fill_objects_dict(result: dict, schema_flat: dict, content_nodes: List[dict]) -> dict:
    for node in content_nodes:
        schema_id = node["schema_id"]
        schema_node = schema_flat[schema_id]

        if "all_objects" not in result[schema_id]:
            # not in multivalue: "schema_id": {content_node...}
            result[schema_id].update(node)
            node = result[schema_id]
        else:
            # in multivalue: "schema_id": {"schema_id": schema_id, "all_objects": [content_node, ...]}
            node = {**node}
            if schema_node["category"] == "tuple":
                node["_content_index"] = len(result[schema_id]["all_objects"])
            result[schema_id]["all_objects"].append(node)

        if "children" in node:
            _fill_objects_dict(result, schema_flat, node.pop("children"))

    return result


class FieldsFlatData:
    """
    [INTERNAL] Flat-style Fields input (schema_id-indexed objects and schema dicts).

    Why this "transitional" representation that isn't quite either the API shape
    or Field instances?
      * Most importantly, we believe exactly this representation should be
        the future shape of the Elis API, as it is much easier to work with.
        We have specifically avoided direct Python object references so that
        it is immediately deserializable.
      * It allows us to build Field instances quickly w/o walking the trees.
      * It is faster to build it than if we instantiate Field instances
        (that is lazy, while the flat data covers the whole annotation content).

    TODO: Change the API to use this representation and remove this conversion
    code (and its overhead).
    """

    schema: dict
    objects: dict

    def __init__(self, schema: dict, objects: dict) -> None:
        self.schema = schema
        self.objects = objects

    @staticmethod
    def from_tree(
        schema_tree: List[dict],
        content_tree: List[dict],
    ) -> FieldsFlatData:
        schema_flat = _generate_schema_dict({}, schema_tree)
        objects_flat = _initialize_objects_dict(schema_flat)
        objects_flat = _fill_objects_dict(objects_flat, schema_flat, content_tree)
        return FieldsFlatData(schema_flat, objects_flat)
