from __future__ import annotations

from leap0.common.pty import PtySession


class TestPtySession:
    def test_from_dict_with_id(self):
        p = PtySession.from_dict({"id": "pty_1", "cwd": "/home/user", "cols": 80, "rows": 24, "active": True})
        assert p.id == "pty_1"
        assert p.cols == 80

    def test_from_dict_with_full_session_info(self):
        p = PtySession.from_dict(
            {
                "id": "pty_2",
                "cwd": "/tmp",
                "envs": {"TERM": "xterm-256color"},
                "cols": 120,
                "rows": 40,
                "created_at": "2026-03-31T00:00:00Z",
                "active": True,
                "lazy_start": False,
            }
        )
        assert p.id == "pty_2"
        assert p.cwd == "/tmp"
        assert p.envs == {"TERM": "xterm-256color"}
        assert p.cols == 120
        assert p.rows == 40
        assert p.created_at == "2026-03-31T00:00:00Z"
        assert p.active is True
        assert p.lazy_start is False

    def test_empty_dict(self):
        p = PtySession.from_dict({})
        assert p.id == ""
        assert p.envs == {}
