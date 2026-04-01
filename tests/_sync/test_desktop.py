from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0._sync.desktop import DesktopClient
from leap0.models.errors import Leap0Error, Leap0TimeoutError


class TestDesktopClient:
    def test_status_stream_raises_on_non_dict_event(self, mock_transport):
        response = MagicMock()
        response.iter_lines.return_value = iter(["data: malformed", ""])
        mock_transport.stream.return_value = response

        with pytest.raises(Leap0Error, match="Malformed desktop status stream event"):
            list(DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").status_stream("sbx-1"))

    def test_wait_until_ready_retries_only_retryable_errors(self, mock_transport):
        first = MagicMock()
        first.iter_lines.return_value = iter([])
        second = MagicMock()
        second.iter_lines.return_value = iter([
            'data: {"status": "running", "items": []}',
            "",
        ])
        mock_transport.stream.side_effect = [first, second]

        DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").wait_until_ready("sbx-1", timeout=1)

        assert mock_transport.stream.call_count == 2

    def test_wait_until_ready_stops_on_malformed_stream(self, mock_transport):
        bad = MagicMock()
        bad.iter_lines.return_value = iter(["data: malformed", ""])
        good = MagicMock()
        good.iter_lines.return_value = iter([
            'data: {"status": "running", "items": []}',
            "",
        ])
        mock_transport.stream.side_effect = [bad, good]

        with pytest.raises(Leap0TimeoutError, match="Malformed desktop status stream event"):
            DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").wait_until_ready("sbx-1", timeout=1)

        assert mock_transport.stream.call_count == 1
