from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from leap0._async.desktop import AsyncDesktopClient
from leap0.models.errors import Leap0Error


class TestAsyncDesktopClient:
    def test_validates_request_payloads(self, async_mock_transport):
        async def run() -> None:
            client = AsyncDesktopClient(async_mock_transport, sandbox_domain="sandbox.example.com")

            with pytest.raises(Leap0Error, match="width must be between 320 and 7680"):
                await client.resize_screen("sbx-1", width=100, height=720)
            with pytest.raises(Leap0Error, match="width and height must be provided together"):
                await client.screenshot("sbx-1", width=100)
            with pytest.raises(Leap0Error, match="format must be one of: png, jpg, jpeg"):
                await client.screenshot("sbx-1", image_format="webp")
            with pytest.raises(Leap0Error, match="quality must be between 1 and 100"):
                await client.screenshot("sbx-1", quality=101)
            with pytest.raises(Leap0Error, match="height must be >= 1"):
                await client.screenshot_region("sbx-1", x=0, y=0, width=10, height=0)
            with pytest.raises(Leap0Error, match="x and y must be provided together"):
                await client.click("sbx-1", x=10)

            assert async_mock_transport.request.call_count == 0
            assert async_mock_transport.request_target_json.call_count == 0

        asyncio.run(run())

    def test_screenshot_allows_zero_sized_paired_region_query(self, async_mock_transport):
        async def run() -> None:
            response = MagicMock()
            response.content = b"image"
            async_mock_transport.request_target.return_value = response

            result = await AsyncDesktopClient(async_mock_transport, sandbox_domain="sandbox.example.com").screenshot(
                "sbx-1",
                width=0,
                height=0,
            )

            assert result == b"image"
            assert async_mock_transport.request_target.call_args.kwargs["params"] == {"width": 0, "height": 0}

        asyncio.run(run())

    def test_requires_boolean_ok_response(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_target_json.return_value = {"ok": "false"}

            with pytest.raises(Leap0Error, match="missing boolean 'ok'"):
                await AsyncDesktopClient(async_mock_transport, sandbox_domain="sandbox.example.com").type_text("sbx-1", text="hello")

        asyncio.run(run())

    def test_status_stream_raises_on_non_dict_event(self, async_mock_transport):
        async def run() -> None:
            response = MagicMock()

            async def aiter_lines():
                yield "data: malformed"
                yield ""

            response.aiter_lines = aiter_lines
            response.aclose = AsyncMock()
            async_mock_transport.stream.return_value = response

            with pytest.raises(Leap0Error, match="Malformed desktop status stream event"):
                async for _ in AsyncDesktopClient(async_mock_transport, sandbox_domain="sandbox.example.com").status_stream("sbx-1"):
                    pass

        asyncio.run(run())

    def test_wait_until_ready_accepts_count_only_running_updates(self, async_mock_transport):
        async def run() -> None:
            response = MagicMock()

            async def aiter_lines():
                yield 'data: {"status": "degraded", "items": [{"name": "xvfb", "running": true, "stdout_log": "/tmp/xvfb.stdout.log", "stderr_log": "/tmp/xvfb.stderr.log"}], "running": 4, "total": 4}'
                yield ""

            response.aiter_lines = aiter_lines
            response.aclose = AsyncMock()
            async_mock_transport.stream.return_value = response

            await AsyncDesktopClient(async_mock_transport, sandbox_domain="sandbox.example.com").wait_until_ready("sbx-1", timeout=1)

        asyncio.run(run())

    def test_status_stream_raises_on_plain_text_error_event(self, async_mock_transport):
        async def run() -> None:
            response = MagicMock()

            async def aiter_lines():
                yield "event: error"
                yield "data: Desktop request failed"
                yield ""

            response.aiter_lines = aiter_lines
            response.aclose = AsyncMock()
            async_mock_transport.stream.return_value = response

            with pytest.raises(Leap0Error, match="Desktop status stream error"):
                async for _ in AsyncDesktopClient(async_mock_transport, sandbox_domain="sandbox.example.com").status_stream("sbx-1"):
                    pass

        asyncio.run(run())

    def test_process_status_requires_documented_fields(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_target_json.return_value = {"items": [], "running": 0, "total": 0}

            with pytest.raises(Leap0Error, match="missing string 'status'"):
                await AsyncDesktopClient(async_mock_transport, sandbox_domain="sandbox.example.com").process_status("sbx-1")

        asyncio.run(run())
