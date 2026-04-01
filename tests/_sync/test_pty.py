from __future__ import annotations

import pytest

from leap0.models.pty import CreatePtySessionParams
from leap0._sync.pty import PtyClient


class TestPtyClient:
    def test_create_builds_payload(self, mock_transport):
        mock_transport.request_json.return_value = {"id": "pty-1", "cols": 120, "rows": 30}

        PtyClient(mock_transport).create("sbx-1", session_id=" sess ", cols=120, rows=30, cwd=" /workspace ")

        args, kwargs = mock_transport.request_json.call_args
        assert args == ("POST", "/v1/sandbox/sbx-1/pty")
        assert kwargs["json"]["id"] == "sess"
        assert kwargs["json"]["cwd"] == "/workspace"


class TestCreatePtySessionParams:
    def test_invalid_cols(self):
        with pytest.raises(ValueError, match="cols"):
            CreatePtySessionParams(cols=0)
