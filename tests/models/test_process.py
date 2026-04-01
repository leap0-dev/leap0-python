from __future__ import annotations

from leap0.models.process import ProcessResult


class TestProcessResult:
    def test_from_dict(self):
        r = ProcessResult.from_dict({"exit_code": 1, "result": "error output"})
        assert r.exit_code == 1
        assert r.result == "error output"
