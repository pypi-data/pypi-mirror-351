from lib.txscript.txscript.reasoning import Reasoning


def test_dependencies_and_targets() -> None:
    reasoning = Reasoning(
        "reasoning",
        ["field.abc", "field.xyz", "abc", "xyz", "queue", "label", "description", ""],
    )

    assert sorted(reasoning.dependencies) == ["abc", "xyz"]
    assert sorted(reasoning.targets) == []
