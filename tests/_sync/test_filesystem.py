from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0._sync.filesystem import FilesystemClient, _parse_multipart_response
from leap0.models.errors import Leap0Error
from leap0.models.filesystem import FileEdit


class TestFilesystemClient:
    def test_ls(self, mock_transport):
        mock_transport.request_json.return_value = {"items": []}
        FilesystemClient(mock_transport).ls("sbx-1", path="/workspace")
        assert "/filesystem/ls" in mock_transport.request_json.call_args[0][1]

    def test_mkdir(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        FilesystemClient(mock_transport).mkdir("sbx-1", path="/workspace/src", recursive=True)
        assert mock_transport.request.call_args[1]["json"]["recursive"] is True

    def test_exists(self, mock_transport):
        mock_transport.request_json.return_value = {"exists": True}
        assert FilesystemClient(mock_transport).exists("sbx-1", path="/workspace/main.py") is True

    def test_glob(self, mock_transport):
        mock_transport.request_json.return_value = {"items": ["/a.ts", "/b.ts"]}
        assert FilesystemClient(mock_transport).glob("sbx-1", path="/workspace", pattern="*.ts") == ["/a.ts", "/b.ts"]

    def test_edit_file(self, mock_transport):
        mock_transport.request_json.return_value = {"diff": "...", "replacements": 1}
        FilesystemClient(mock_transport).edit_file("sbx-1", path="/a.py", edits=[FileEdit(find="old", replace="new")])
        assert mock_transport.request_json.call_args[1]["json"]["edits"] == [{"find": "old", "replace": "new"}]

    def test_write_file(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        FilesystemClient(mock_transport).write_file("sbx-1", path="/workspace/hello.txt", content="Hello")
        assert mock_transport.request.call_args[1]["content"] == b"Hello"

    def test_write_bytes(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        FilesystemClient(mock_transport).write_bytes("sbx-1", path="/workspace/hello.bin", content=b"Hello")
        assert mock_transport.request.call_args[1]["headers"]["Content-Type"] == "application/octet-stream"

    def test_read_file(self, mock_transport):
        mock_transport.request.return_value = MagicMock(content=b"Hello")
        assert FilesystemClient(mock_transport).read_file("sbx-1", path="/workspace/hello.txt") == "Hello"

    def test_read_bytes(self, mock_transport):
        mock_transport.request.return_value = MagicMock(content=b"Hello")
        assert FilesystemClient(mock_transport).read_bytes("sbx-1", path="/workspace/hello.bin") == b"Hello"

    def test_read_bytes_rejects_head_and_tail(self, mock_transport):
        with pytest.raises(Leap0Error, match="mutually exclusive"):
            FilesystemClient(mock_transport).read_bytes("sbx-1", path="/workspace/hello.bin", head=1, tail=1)

    def test_set_permissions_rejects_missing_or_blank_updates(self, mock_transport):
        client = FilesystemClient(mock_transport)

        with pytest.raises(Leap0Error, match="at least one of mode, owner, or group"):
            client.set_permissions("sbx-1", path="/workspace/a.txt")
        with pytest.raises(Leap0Error, match="mode must be a non-empty string"):
            client.set_permissions("sbx-1", path="/workspace/a.txt", mode="   ")
        with pytest.raises(Leap0Error, match="owner must be a non-empty string"):
            client.set_permissions("sbx-1", path="/workspace/a.txt", owner="")

        assert mock_transport.request.call_count == 0

    def test_write_files(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        FilesystemClient(mock_transport).write_files("sbx-1", files={"/workspace/hello.txt": "Hello"})
        assert mock_transport.request.call_args[1]["files"] == [("/workspace/hello.txt", b"Hello")]

    def test_read_files(self, mock_transport):
        boundary = "boundary123"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"/a.txt\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\ncontent a\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        mock_transport.request.return_value = MagicMock(
            content=body,
            headers={"content-type": f"multipart/form-data; boundary={boundary}"},
        )
        assert FilesystemClient(mock_transport).read_files("sbx-1", paths=["/a.txt"]) == {"/a.txt": "content a"}


class TestParseMultipartResponse:
    def test_valid(self):
        boundary = "boundary123"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"/a.txt\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\ncontent a\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        result = _parse_multipart_response(f"multipart/form-data; boundary={boundary}", body)
        assert result["/a.txt"] == b"content a"

    def test_non_multipart_raises(self):
        with pytest.raises(ValueError, match="Expected multipart"):
            _parse_multipart_response("application/json", b'{"error": "bad"}')

    def test_text_part_raises(self):
        boundary = "boundary123"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"/a.txt\"\r\n"
            f"Content-Type: text/plain; charset=utf-8\r\n\r\ncontent a\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        with pytest.raises(ValueError, match="Failed to parse /read-files response"):
            _parse_multipart_response(f"multipart/form-data; boundary={boundary}", body)
