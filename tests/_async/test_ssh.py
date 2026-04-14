from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from leap0._async.ssh import AsyncSshClient


class TestAsyncSshClient:
    def test_create_access(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {
                "id": "ssh-1", "password": "pw", "ssh_command": "ssh u@h", "sandbox_id": "sbx-1",
            }
            result = await AsyncSshClient(async_mock_transport).create_access("sbx-1")
            assert result.id == "ssh-1"

        asyncio.run(run())

    def test_delete_access(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request.return_value = MagicMock(status_code=204)
            await AsyncSshClient(async_mock_transport).delete_access("sbx-1", id="ssh-1")
            assert async_mock_transport.request.call_args[0][:2] == ("DELETE", "/v1/sandbox/sbx-1/ssh/ssh-1")

        asyncio.run(run())
