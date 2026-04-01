from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0._sync.code_interpreter import CodeInterpreterClient
from leap0.models.errors import Leap0Error


class TestCodeInterpreterClient:
    def test_execute_stream_skips_non_dict_frames(self, mock_transport):
        response = MagicMock()
        response.iter_lines.return_value = iter([
            "data: heartbeat",
            "",
            'data: {"type": "stdout", "data": "ok"}',
            "",
        ])
        mock_transport.stream.return_value = response

        events = list(
            CodeInterpreterClient(mock_transport, sandbox_domain="sandbox.example.com").execute_stream(
                "sbx-1",
                code="print('ok')",
            )
        )

        assert [event.data for event in events] == ["ok"]

    def test_execute_stream_raises_on_error_envelope(self, mock_transport):
        response = MagicMock()
        response.iter_lines.return_value = iter([
            'data: {"envelope": "error", "message": "boom"}',
            "",
        ])
        mock_transport.stream.return_value = response

        with pytest.raises(Leap0Error, match="boom"):
            list(
                CodeInterpreterClient(mock_transport, sandbox_domain="sandbox.example.com").execute_stream(
                    "sbx-1",
                    code="print('ok')",
                )
            )
