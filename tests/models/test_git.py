from __future__ import annotations

from leap0.models.git import GitCommitResult, GitResult


class TestGitResult:
    def test_from_dict(self):
        r = GitResult.from_dict({"output": "ok", "exit_code": 0})
        assert r.output == "ok"

    def test_empty_dict(self):
        assert GitResult.from_dict({}).exit_code == 0


class TestGitCommitResult:
    def test_with_result(self):
        r = GitCommitResult.from_dict({"sha": "abc123", "result": {"output": "committed", "exit_code": 0}})
        assert r.sha == "abc123"
        assert r.result.output == "committed"

    def test_without_result(self):
        assert GitCommitResult.from_dict({"sha": "abc"}).result is None

    def test_null_result(self):
        r = GitCommitResult.from_dict({"sha": None, "result": None})
        assert r.sha is None
        assert r.result is None
