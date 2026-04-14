from __future__ import annotations

from unittest.mock import MagicMock

from leap0._sync.ssh import SshClient


class TestSshClient:
    def test_create_access(self, mock_transport):
        mock_transport.request_json.return_value = {
            "id": "ssh-1", "password": "pw", "ssh_command": "ssh u@h", "sandbox_id": "sbx-1",
        }
        result = SshClient(mock_transport).create_access("sbx-1")
        assert result.id == "ssh-1"

    def test_delete_access(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        SshClient(mock_transport).delete_access("sbx-1", id="ssh-1")
        assert mock_transport.request.call_args[0][:2] == ("DELETE", "/v1/sandbox/sbx-1/ssh/ssh-1")
