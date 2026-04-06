from __future__ import annotations

from leap0._sync.process import ProcessClient


class TestProcessClient:
    def test_execute(self, mock_transport):
        mock_transport.request_json.return_value = {"exit_code": 0, "stdout": "hello", "stderr": "warn"}
        result = ProcessClient(mock_transport).execute("sbx-1", command="echo hello")
        assert result.exit_code == 0
        assert result.stdout == "hello"
        assert result.stderr == "warn"
        assert mock_transport.request_json.call_args[0][:2] == ("POST", "/v1/sandbox/sbx-1/process/execute")
