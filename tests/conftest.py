from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from leap0._sync._transport import Transport
from leap0._async._transport import AsyncTransport


@pytest.fixture
def transport():
    return Transport(api_key="test-key", base_url="https://api.example.com")


@pytest.fixture
def mock_transport():
    t = MagicMock(spec=Transport)
    t.auth_header = "authorization"
    t.auth_value = "Bearer test-key"
    return t


@pytest.fixture
def async_mock_transport():
    t = MagicMock(spec=AsyncTransport)
    t.auth_header = "authorization"
    t.auth_value = "Bearer test-key"
    t.request = AsyncMock()
    t.request_json = AsyncMock()
    t.request_target = AsyncMock()
    t.request_target_json = AsyncMock()
    t.stream = AsyncMock()
    t.close = AsyncMock()
    return t
