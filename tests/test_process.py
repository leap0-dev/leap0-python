from __future__ import annotations

from leap0.process import ProcessClient


class TestProcessClient:
    def test_execute(self, mock_transport):
        mock_transport.request_json.return_value = {"exit_code": 0, "result": "hello"}
        result = ProcessClient(mock_transport).execute("sbx-1", command="echo hello")
        assert result.exit_code == 0
        assert result.result == "hello"
        assert "/process/execute" in mock_transport.request_json.call_args[0][1]
