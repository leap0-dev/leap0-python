from __future__ import annotations

from unittest.mock import MagicMock

from leap0.templates import TemplatesClient


class TestTemplatesClient:
    def test_create(self, mock_transport):
        mock_transport.request_json.return_value = {
            "id": "tpl-1", "name": "my-tpl", "digest": "sha256:abc",
            "image_config": None, "is_system": False, "created_at": "",
        }
        result = TemplatesClient(mock_transport).create(name="my-tpl", uri="docker.io/library/python:3.12")
        args, kwargs = mock_transport.request_json.call_args
        assert args[1] == "/v1/template"
        assert result.name == "my-tpl"

    def test_rename(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        TemplatesClient(mock_transport).rename("tpl-1", name="new-name")
        args, kwargs = mock_transport.request.call_args
        assert args == ("PATCH", "/v1/template/tpl-1")
        assert kwargs["expected_status"] == 204

    def test_delete(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        TemplatesClient(mock_transport).delete("tpl-1")
        assert mock_transport.request.call_args[1]["expected_status"] == 204
