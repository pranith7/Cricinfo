from __future__ import annotations

import pytest


@pytest.fixture
def base_url() -> str:
    return "https://example.test"
