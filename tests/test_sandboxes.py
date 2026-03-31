from __future__ import annotations

from unittest.mock import MagicMock

from leap0.sandboxes import SandboxesClient
from leap0.common.sandbox import Sandbox


class TestSandboxesClient:
    def test_create(self, mock_transport):
        mock_transport.request_json.return_value = {
            "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
            "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
        }
        result = SandboxesClient(mock_transport, sandbox_domain="s.dev").create(template_name="my-tpl", vcpu=2, memory_mib=2048)
        args, kwargs = mock_transport.request_json.call_args
        assert args == ("POST", "/v1/sandbox")
        assert kwargs["json"]["template_name"] == "my-tpl"
        assert result.id == "sbx-1"

    def test_get(self, mock_transport):
        mock_transport.request_json.return_value = {
            "id": "sbx-1", "template_id": "t", "vcpu": 1, "memory_mib": 512,
            "disk_mib": 10240, "state": "running", "auto_pause": False, "created_at": "",
        }
        SandboxesClient(mock_transport, sandbox_domain="s.dev").get("sbx-1")
        assert mock_transport.request_json.call_args[0][1] == "/v1/sandbox/sbx-1/"

    def test_delete(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        SandboxesClient(mock_transport, sandbox_domain="s.dev").delete("sbx-1")
        assert mock_transport.request.call_args[1]["expected_status"] == 204

    def test_accepts_sandbox_object(self, mock_transport):
        mock_transport.request_json.return_value = {
            "id": "sbx-1", "template_id": "t", "vcpu": 1, "memory_mib": 512,
            "disk_mib": 10240, "state": "running", "auto_pause": False, "created_at": "",
        }
        SandboxesClient(mock_transport, sandbox_domain="s.dev").get(Sandbox(id="sbx-obj"))
        assert "sbx-obj" in mock_transport.request_json.call_args[0][1]

    def test_invoke_url(self, mock_transport):
        assert SandboxesClient(mock_transport, sandbox_domain="sandbox.leap0.dev").invoke_url("sbx-1", "/api/health") == "https://sbx-1.sandbox.leap0.dev/api/health"
