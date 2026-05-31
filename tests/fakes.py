from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass
class FakeResponse:
    text: str
    status_code: int = 200

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


class FakeSession:
    def __init__(self, responses: dict[str, FakeResponse]) -> None:
        self.responses = responses
        self.headers: dict[str, str] = {}
        self.calls: list[tuple[str, int]] = []

    def get(self, url: str, timeout: int) -> FakeResponse:
        self.calls.append((url, timeout))
        return self.responses[url]
