"""
Builtins available as globals in TxScript code.

Each new builtin:
    * is automatically available as a global in formulas
    * must be added to __init__.__all__ to be available in
      serverless functions that have `from txscript import *`
"""

import datetime  # noqa: F401
import re  # noqa: ELI503
from datetime import date, timedelta  # noqa: F401
from typing import Any


def default_to(value: Any, default: Any) -> Any:
    try:
        return value.default_to(default)
    except AttributeError:
        return default if is_empty(value) else value


fallback = default_to  # temporary compatibility


def is_empty(value: Any) -> bool:
    try:
        return value.is_empty()
    except AttributeError:
        return value == None or value == ""  # noqa: E711


def is_set(value: Any) -> bool:
    # temporary compatibility
    return not is_empty(value)


substitute = re.sub
