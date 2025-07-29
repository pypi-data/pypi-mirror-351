import pathlib
import sys

import pytest


@pytest.fixture(autouse=True)
def _txscript_in_path():
    # This needs to be done in order to simulate the import paths in lambda function
    txscript_path = str(pathlib.Path(__file__).parent.parent)
    already_present = txscript_path in sys.path
    if not already_present:
        sys.path.insert(0, txscript_path)

    yield

    if not already_present:
        sys.path.remove(txscript_path)
