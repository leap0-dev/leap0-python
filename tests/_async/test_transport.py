from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import httpx

from leap0._async._transport import AsyncTransport


def test_async_transport_headers() -> None:
    transport = AsyncTransport(api_key="test-key", base_url="https://api.example.com")
    headers = transport.headers()
    assert headers["authorization"] == "Bearer test-key"
    assert headers["Leap0-Source"] == "sdk-python-async"
    assert headers["Leap0-SDK-Version"]
    assert headers["User-Agent"].startswith("leap0-python-async/")
    asyncio.run(transport.close())


def test_async_transport_request_json(async_mock_transport) -> None:
    async def run() -> None:
        transport = AsyncTransport(api_key="test-key", base_url="https://api.example.com")
        response = MagicMock(spec=httpx.Response)
        response.status_code = 200
        response.json.return_value = {"ok": True}
        transport._client.request = AsyncMock(return_value=response)  # type: ignore[method-assign]
        data = await transport.request_json("GET", "/v1/test")
        assert data == {"ok": True}
        await transport.close()

    asyncio.run(run())
