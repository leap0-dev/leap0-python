from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from leap0._async.templates import AsyncTemplatesClient


class TestAsyncTemplatesClient:
    def test_create(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {
                "id": "tpl-1", "name": "my-tpl", "digest": "sha256:abc",
                "image_config": None, "is_system": False, "created_at": "",
            }
            result = await AsyncTemplatesClient(async_mock_transport).create(name="my-tpl", uri="docker.io/library/python:3.12")
            args, _kwargs = async_mock_transport.request_json.call_args
            assert args[1] == "/v1/template"
            assert result.name == "my-tpl"

        asyncio.run(run())

    def test_delete(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request.return_value = MagicMock(status_code=204)
            await AsyncTemplatesClient(async_mock_transport).delete("tpl-1")
            assert async_mock_transport.request.call_args[1]["expected_status"] == 204

        asyncio.run(run())
