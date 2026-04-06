from __future__ import annotations

from leap0.models.process import ProcessResult


class TestProcessResult:
    def test_from_dict(self):
        r = ProcessResult.from_dict({"exit_code": 1, "stdout": "hello", "stderr": "error output"})
        assert r.exit_code == 1
        assert r.stdout == "hello"
        assert r.stderr == "error output"
