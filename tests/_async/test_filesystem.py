from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from leap0._async.filesystem import AsyncFilesystemClient, _parse_multipart_response
from leap0.models.errors import Leap0Error
from leap0.models.filesystem import FileEdit


class TestAsyncFilesystemClient:
    def test_ls(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"items": []}
            await AsyncFilesystemClient(async_mock_transport).ls("sbx-1", path="/workspace", http_timeout=1.5)
            assert "/filesystem/ls" in async_mock_transport.request_json.call_args[0][1]
            assert async_mock_transport.request_json.call_args.kwargs["timeout"] == 1.5

        asyncio.run(run())

    def test_stat_forwards_timeout(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"path": "/workspace", "name": "workspace", "type": "dir"}
            await AsyncFilesystemClient(async_mock_transport).stat("sbx-1", path="/workspace", http_timeout=2.0)
            assert async_mock_transport.request_json.call_args.kwargs["timeout"] == 2.0

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

    def test_read_bytes_rejects_head_and_tail(self, async_mock_transport):
        async def run() -> None:
            with pytest.raises(Leap0Error, match="mutually exclusive"):
                await AsyncFilesystemClient(async_mock_transport).read_bytes(
                    "sbx-1",
                    path="/workspace/hello.txt",
                    head=1,
                    tail=1,
                )

        asyncio.run(run())


class TestParseMultipartResponse:
    def test_non_multipart_redacts_preview(self):
        with pytest.raises(ValueError, match="<redacted>"):
            _parse_multipart_response("application/json", b'{"secret": "value"}')
