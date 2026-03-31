from __future__ import annotations

from leap0.common.pty import PtySession


class TestPtySession:
    def test_from_dict_with_id(self):
        p = PtySession.from_dict({"id": "pty_1", "cwd": "/home/user", "cols": 80, "rows": 24, "active": True})
        assert p.id == "pty_1"
        assert p.cols == 80

    def test_from_dict_with_session_id(self):
        assert PtySession.from_dict({"session_id": "pty_2", "cols": 120}).id == "pty_2"

    def test_prefers_id_over_session_id(self):
        assert PtySession.from_dict({"id": "pty_a", "session_id": "pty_b"}).id == "pty_a"

    def test_empty_dict(self):
        p = PtySession.from_dict({})
        assert p.id == ""
        assert p.envs == {}
