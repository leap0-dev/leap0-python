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

    def test_set_permissions_rejects_missing_or_blank_updates(self, async_mock_transport):
        async def run() -> None:
            client = AsyncFilesystemClient(async_mock_transport)

            with pytest.raises(Leap0Error, match="at least one of mode, owner, or group"):
                await client.set_permissions("sbx-1", path="/workspace/a.txt")
            with pytest.raises(Leap0Error, match="group must be a non-empty string"):
                await client.set_permissions("sbx-1", path="/workspace/a.txt", group="   ")

            assert async_mock_transport.request.call_count == 0

        asyncio.run(run())


class TestParseMultipartResponse:
    def test_non_multipart_redacts_preview(self):
        with pytest.raises(ValueError, match="<redacted>"):
            _parse_multipart_response("application/json", b'{"secret": "value"}')

    def test_text_part_raises(self):
        boundary = "boundary123"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"/a.txt\"\r\n"
            f"Content-Type: text/plain; charset=utf-8\r\n\r\ncontent a\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        with pytest.raises(ValueError, match="Failed to parse read_files multipart body"):
            _parse_multipart_response(f"multipart/form-data; boundary={boundary}", body)
