from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from leap0._async.code_interpreter import AsyncCodeInterpreterClient
from leap0.models.errors import Leap0Error


class TestAsyncCodeInterpreterClient:
    def test_selected_methods_forward_http_timeout(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_target_json.return_value = {"status": "ok", "items": []}

            client = AsyncCodeInterpreterClient(async_mock_transport, sandbox_domain="sandbox.example.com")
            await client.health("sbx-1", http_timeout=1.5)
            await client.list_contexts("sbx-1", http_timeout=2.5)
            await client.delete_context("sbx-1", "ctx-1", http_timeout=3.5)

            assert async_mock_transport.request_target_json.call_args_list[0].kwargs["timeout"] == 1.5
            assert async_mock_transport.request_target_json.call_args_list[1].kwargs["timeout"] == 2.5
            assert async_mock_transport.request_target.call_args.kwargs["timeout"] == 3.5

        asyncio.run(run())

    def test_execute_stream_skips_non_dict_frames(self, async_mock_transport):
        async def lines():
            yield "data: heartbeat"
            yield ""
            yield 'data: {"type": "stdout", "data": "ok"}'
            yield ""

        async def run() -> None:
            response = MagicMock()
            response.aiter_lines = lambda: lines()
            response.aclose = AsyncMock()
            async_mock_transport.stream.return_value = response

            events = [
                event
                async for event in AsyncCodeInterpreterClient(
                    async_mock_transport,
                    sandbox_domain="sandbox.example.com",
                ).execute_stream("sbx-1", code="print('ok')")
            ]

            assert [event.data for event in events] == ["ok"]

        asyncio.run(run())

    def test_execute_stream_raises_on_error_envelope(self, async_mock_transport):
        async def lines():
            yield 'data: {"envelope": "error", "message": "boom"}'
            yield ""

        async def run() -> None:
            response = MagicMock()
            response.aiter_lines = lambda: lines()
            response.aclose = AsyncMock()
            async_mock_transport.stream.return_value = response

            with pytest.raises(Leap0Error, match="boom"):
                async for _ in AsyncCodeInterpreterClient(
                    async_mock_transport,
                    sandbox_domain="sandbox.example.com",
                ).execute_stream("sbx-1", code="print('ok')"):
                    pass

        asyncio.run(run())
