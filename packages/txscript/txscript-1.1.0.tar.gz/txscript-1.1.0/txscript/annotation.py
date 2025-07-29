# !!! This code path is currently untested !!!

from typing import Any, Optional

from .exceptions import PayloadError


class Annotation:
    def __init__(self, raw_data: dict, token: Optional[str]) -> None:
        self.raw_data = raw_data
        self._token = token
        self.status = raw_data["status"]
        self.previous_status = raw_data.get("previous_status")
        self.url = raw_data["url"]

    def action(self, verb: str, **args: Any) -> None:
        """Execute a given API verb on the annotation (use in return ... clause to stop processing at this point)."""
        import requests

        if self._token is None:
            raise PayloadError("Passing authorization token must be enabled!")

        r = requests.post(f"{self.url}/{verb}", headers={"Authorization": f"Bearer {self._token}"}, json=args)
        if r.status_code >= 300:
            raise Exception(r)
