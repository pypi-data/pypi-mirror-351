import dataclasses
from typing import Any

from .txscript import TxScriptAnnotationContent  # noqa: TC002


@dataclasses.dataclass
class Promise:
    type: str  # noqa: A003
    id: int  # noqa: A003
    context: dict


class Computed:
    dependencies: set
    targets: set
    schema_id: str

    def evaluate(self, t: TxScriptAnnotationContent) -> Any | Promise:
        raise NotImplementedError
