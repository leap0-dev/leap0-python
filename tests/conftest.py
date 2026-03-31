from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0._transport import Transport


@pytest.fixture
def transport():
    return Transport(api_key="test-key", base_url="https://api.example.com")


@pytest.fixture
def mock_transport():
    t = MagicMock(spec=Transport)
    t.auth_header = "authorization"
    t.auth_value = "Bearer test-key"
    return t
