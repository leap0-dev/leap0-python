from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0._sync.desktop import DesktopClient
from leap0.models.errors import Leap0Error


class TestDesktopClient:
    def test_status_stream_raises_on_non_dict_event(self, mock_transport):
        response = MagicMock()
        response.iter_lines.return_value = iter(["data: malformed", ""])
        mock_transport.stream.return_value = response

        with pytest.raises(Leap0Error, match="Malformed desktop status stream event"):
            list(DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").status_stream("sbx-1"))
