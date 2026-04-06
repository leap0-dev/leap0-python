from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0._sync.desktop import DesktopClient
from leap0.models.errors import Leap0Error


class TestDesktopClient:
    def test_validates_request_payloads(self, mock_transport):
        client = DesktopClient(mock_transport, sandbox_domain="sandbox.example.com")

        with pytest.raises(Leap0Error, match="width must be between 320 and 7680"):
            client.resize_screen("sbx-1", width=100, height=720)
        with pytest.raises(Leap0Error, match="width and height must be provided together"):
            client.screenshot("sbx-1", width=100)
        with pytest.raises(Leap0Error, match="format must be one of: png, jpg, jpeg"):
            client.screenshot("sbx-1", image_format="webp")
        with pytest.raises(Leap0Error, match="quality must be between 1 and 100"):
            client.screenshot("sbx-1", quality=101)
        with pytest.raises(Leap0Error, match="height must be >= 1"):
            client.screenshot_region("sbx-1", x=0, y=0, width=10, height=0)
        with pytest.raises(Leap0Error, match="x and y must be provided together"):
            client.click("sbx-1", x=10)

        assert mock_transport.request_target.call_count == 0
        assert mock_transport.request_target_json.call_count == 0

    def test_screenshot_allows_zero_sized_paired_region_query(self, mock_transport):
        response = MagicMock()
        response.content = b"image"
        mock_transport.request_target.return_value = response

        result = DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").screenshot(
            "sbx-1",
            width=0,
            height=0,
        )

        assert result == b"image"
        assert mock_transport.request_target.call_args.kwargs["params"] == {"width": 0, "height": 0}

    def test_requires_boolean_ok_response(self, mock_transport):
        mock_transport.request_target_json.return_value = {"ok": "false"}

        with pytest.raises(Leap0Error, match="missing boolean 'ok'"):
            DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").type_text("sbx-1", text="hello")

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
            'data: {"status": "running", "items": [{"name": "xvfb", "running": true, "stdout_log": "/tmp/xvfb.stdout.log", "stderr_log": "/tmp/xvfb.stderr.log"}], "running": 1, "total": 1}',
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
            'data: {"status": "running", "items": [{"name": "xvfb", "running": true, "stdout_log": "/tmp/xvfb.stdout.log", "stderr_log": "/tmp/xvfb.stderr.log"}], "running": 1, "total": 1}',
            "",
        ])
        mock_transport.stream.side_effect = [bad, good]

        with pytest.raises(Leap0Error, match="Malformed desktop status stream event"):
            DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").wait_until_ready("sbx-1", timeout=1)

        assert mock_transport.stream.call_count == 1

    def test_wait_until_ready_accepts_count_only_running_updates(self, mock_transport):
        response = MagicMock()
        response.iter_lines.return_value = iter([
            'data: {"status": "degraded", "items": [{"name": "xvfb", "running": true, "stdout_log": "/tmp/xvfb.stdout.log", "stderr_log": "/tmp/xvfb.stderr.log"}], "running": 4, "total": 4}',
            "",
        ])
        mock_transport.stream.return_value = response

        DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").wait_until_ready("sbx-1", timeout=1)

    def test_status_stream_raises_on_plain_text_error_event(self, mock_transport):
        response = MagicMock()
        response.iter_lines.return_value = iter([
            "event: error",
            "data: Desktop request failed",
            "",
        ])
        mock_transport.stream.return_value = response

        with pytest.raises(Leap0Error, match="Desktop status stream error"):
            list(DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").status_stream("sbx-1"))

    def test_status_stream_raises_structured_error_detail(self, mock_transport):
        response = MagicMock()
        response.iter_lines.return_value = iter([
            "event: error",
            'data: {"message": "Desktop request failed"}',
            "",
        ])
        mock_transport.stream.return_value = response

        with pytest.raises(Leap0Error, match="Desktop status stream error") as exc_info:
            list(DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").status_stream("sbx-1"))

        assert exc_info.value.body == "Desktop request failed"

    def test_process_status_requires_documented_fields(self, mock_transport):
        mock_transport.request_target_json.return_value = {"items": [], "running": 0, "total": 0}

        with pytest.raises(Leap0Error, match="missing string 'status'"):
            DesktopClient(mock_transport, sandbox_domain="sandbox.example.com").process_status("sbx-1")
