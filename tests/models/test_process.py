from __future__ import annotations

from leap0.models.process import ProcessResult


class TestProcessResult:
    def test_from_dict(self):
        r = ProcessResult.from_dict({"exit_code": 1, "stdout": "hello", "stderr": "error output"})
        assert r.exit_code == 1
        assert r.stdout == "hello"
        assert r.stderr == "error output"

    def test_from_dict_accepts_legacy_result_string(self):
        r = ProcessResult.from_dict({"exit_code": 0, "result": "hello"})
        assert r.stdout == "hello"
        assert r.stderr == ""
        assert r.result == "hello"

    def test_from_dict_accepts_legacy_result_mapping(self):
        r = ProcessResult.from_dict({"exit_code": 0, "result": {"stdout": "hello", "stderr": "warn"}})
        assert r.stdout == "hello"
        assert r.stderr == "warn"
        assert r.result == {"stdout": "hello", "stderr": "warn"}
