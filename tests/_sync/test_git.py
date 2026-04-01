from __future__ import annotations

from leap0._sync.git import GitClient


class TestGitClient:
    def test_clone(self, mock_transport):
        mock_transport.request_json.return_value = {"output": "cloned", "exit_code": 0}
        GitClient(mock_transport).clone("sbx-1", url="https://github.com/test/repo.git", path="/workspace/repo")
        args, kwargs = mock_transport.request_json.call_args
        assert args[1] == "/v1/sandbox/sbx-1/git/clone"
        assert kwargs["json"]["url"] == "https://github.com/test/repo.git"

    def test_status(self, mock_transport):
        mock_transport.request_json.return_value = {"output": "", "exit_code": 0}
        GitClient(mock_transport).status("sbx-1", path="/workspace/repo")
        assert "/git/status" in mock_transport.request_json.call_args[0][1]
