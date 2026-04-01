from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0.models.errors import Leap0Error
from leap0._sync.templates import TemplatesClient
from leap0.models.template import CreateTemplateParams


class TestTemplatesClient:
    def test_create(self, mock_transport):
        mock_transport.request_json.return_value = {
            "id": "tpl-1", "name": "my-tpl", "digest": "sha256:abc",
            "image_config": None, "is_system": False, "created_at": "",
        }
        result = TemplatesClient(mock_transport).create(name="my-tpl", uri="docker.io/library/python:3.12")
        args, _kwargs = mock_transport.request_json.call_args
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

    def test_create_validates_name(self, mock_transport):
        with pytest.raises(Leap0Error, match="system/"):
            TemplatesClient(mock_transport).create(name="system/bad", uri="docker.io/library/python:3.12")


class TestCreateTemplateParams:
    def test_payload_trims_values(self):
        payload = CreateTemplateParams(name=" my-template ", uri=" docker.io/library/python:3.12 ").to_payload()
        assert payload["name"] == "my-template"
        assert payload["uri"] == "docker.io/library/python:3.12"
