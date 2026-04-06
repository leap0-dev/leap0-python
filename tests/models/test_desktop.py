from __future__ import annotations

import pytest

from leap0.models.desktop import (
    DesktopDisplayInfo, DesktopHealth, DesktopPointerPosition, DesktopProcessErrors,
    DesktopProcessLogs, DesktopProcessRestart, DesktopProcessStatus, DesktopProcessStatusList,
    DesktopRecordingStatus, DesktopRecordingSummary, DesktopWindow,
)


class TestDesktopHealth:
    def test_ok_true(self):
        assert DesktopHealth.from_dict({"ok": True}).ok is True

    def test_requires_ok(self):
        with pytest.raises(ValueError, match="missing boolean 'ok'"):
            DesktopHealth.from_dict({})


class TestDesktopDisplayInfo:
    def test_from_dict(self):
        d = DesktopDisplayInfo.from_dict({"display": ":0", "width": 1920, "height": 1080})
        assert d.width == 1920


class TestDesktopWindow:
    def test_class_key(self):
        assert DesktopWindow.from_dict({"id": "w1", "class": "Firefox"}).window_class == "Firefox"

    def test_class_underscore_key(self):
        assert DesktopWindow.from_dict({"id": "w2", "class_": "Chrome"}).window_class == "Chrome"

    def test_prefers_class(self):
        assert DesktopWindow.from_dict({"id": "w3", "class": "A", "class_": "B"}).window_class == "A"

    def test_empty_dict(self):
        assert DesktopWindow.from_dict({}).window_class == ""


class TestDesktopPointerPosition:
    def test_from_dict(self):
        p = DesktopPointerPosition.from_dict({"x": 100, "y": 200})
        assert p.x == 100


class TestDesktopRecordingStatus:
    def test_from_dict(self):
        r = DesktopRecordingStatus.from_dict({"id": "rec_1", "active": True, "started_at": "2025-01-01",
                                              "display": ":0", "resolution": "1920x1080"})
        assert r.active is True


class TestDesktopRecordingSummary:
    def test_from_dict(self):
        assert DesktopRecordingSummary.from_dict({"id": "rec_1", "file_name": "a.mp4", "size_bytes": 1024}).size_bytes == 1024


class TestDesktopProcessStatus:
    def test_from_dict(self):
        p = DesktopProcessStatus.from_dict(
            {
                "name": "xvfb",
                "running": True,
                "pid": 123,
                "stdout_log": "/tmp/xvfb.stdout.log",
                "stderr_log": "/tmp/xvfb.stderr.log",
            }
        )
        assert p.running is True


class TestDesktopProcessStatusList:
    def test_from_dict(self):
        sl = DesktopProcessStatusList.from_dict(
            {
                "status": "running",
                "items": [
                    {
                        "name": "xvfb",
                        "running": True,
                        "pid": 1,
                        "stdout_log": "/tmp/xvfb.stdout.log",
                        "stderr_log": "/tmp/xvfb.stderr.log",
                    }
                ],
                "running": 1,
                "total": 4,
            }
        )
        assert len(sl.items) == 1
        assert sl.total == 4

    def test_requires_status_fields(self):
        with pytest.raises(ValueError, match="missing array 'items'"):
            DesktopProcessStatusList.from_dict({})


class TestDesktopProcessRestart:
    def test_with_status(self):
        r = DesktopProcessRestart.from_dict(
            {
                "message": "restarted",
                "status": {
                    "name": "xvfb",
                    "running": True,
                    "pid": 42,
                    "stdout_log": "/tmp/xvfb.stdout.log",
                    "stderr_log": "/tmp/xvfb.stderr.log",
                },
            }
        )
        assert r.status.pid == 42

    def test_without_status(self):
        assert DesktopProcessRestart.from_dict({"message": "ok"}).status is None


class TestDesktopProcessLogs:
    def test_from_dict(self):
        assert DesktopProcessLogs.from_dict({"process": "xvfb", "logs": "output..."}).logs == "output..."


class TestDesktopProcessErrors:
    def test_from_dict(self):
        assert DesktopProcessErrors.from_dict({"process": "x11vnc", "errors": "fail"}).errors == "fail"
