from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0.filesystem import FilesystemClient, _parse_multipart_response
from leap0.common.filesystem import FileEdit


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
