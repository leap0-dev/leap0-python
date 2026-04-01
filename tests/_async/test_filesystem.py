from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from leap0._async.filesystem import AsyncFilesystemClient
from leap0.models.filesystem import FileEdit


class TestAsyncFilesystemClient:
    def test_ls(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"items": []}
            await AsyncFilesystemClient(async_mock_transport).ls("sbx-1", path="/workspace")
            assert "/filesystem/ls" in async_mock_transport.request_json.call_args[0][1]

        asyncio.run(run())

    def test_mkdir(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request.return_value = MagicMock(status_code=204)
            await AsyncFilesystemClient(async_mock_transport).mkdir("sbx-1", path="/workspace/src", recursive=True)
            assert async_mock_transport.request.call_args[1]["json"]["recursive"] is True

        asyncio.run(run())

    def test_edit_file(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"diff": "...", "replacements": 1}
            await AsyncFilesystemClient(async_mock_transport).edit_file("sbx-1", path="/a.py", edits=[FileEdit(find="old", replace="new")])
            assert async_mock_transport.request_json.call_args[1]["json"]["edits"] == [{"find": "old", "replace": "new"}]

        asyncio.run(run())
