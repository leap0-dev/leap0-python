from __future__ import annotations
from unittest.mock import MagicMock
from types import SimpleNamespace

import pytest

from leap0.models.errors import Leap0Error
from leap0._sync.sandbox import Sandbox as RichSandbox, SandboxesClient
from leap0.models.sandbox import CreateSandboxParams, Sandbox


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

    def test_factory_returns_rich_sandbox(self, mock_transport):
        fake_client = SimpleNamespace(
            _filesystem=MagicMock(),
            _git=MagicMock(),
            _process=MagicMock(),
            _pty=MagicMock(),
            _lsp=MagicMock(),
            _ssh=MagicMock(),
            _code_interpreter=MagicMock(),
            _desktop=MagicMock(),
        )
        client = SandboxesClient(
            mock_transport,
            sandbox_domain="s.dev",
            sandbox_factory=lambda data: RichSandbox(fake_client, data),
        )
        fake_client.sandboxes = client
        mock_transport.request_json.return_value = {
            "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
            "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
        }

        result = client.create(template_name="my-tpl")

        assert isinstance(result, RichSandbox)
        assert result.id == "sbx-1"

    def test_create_validates_input(self, mock_transport):
        with pytest.raises(Leap0Error, match="memory_mib"):
            SandboxesClient(mock_transport, sandbox_domain="s.dev").create(memory_mib=513)

    def test_create_injects_otel_env_when_enabled(self, mock_transport, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_HEADERS", "authorization=token")
        mock_transport.request_json.return_value = {
            "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
            "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
        }

        SandboxesClient(mock_transport, sandbox_domain="s.dev").create(
            otel_export=True,
            env_vars={"APP_ENV": "test"},
        )

        sent_env = mock_transport.request_json.call_args.kwargs["json"]["env_vars"]
        assert sent_env == {
            "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector:4318",
            "OTEL_EXPORTER_OTLP_HEADERS": "authorization=token",
            "APP_ENV": "test",
        }

    def test_create_accepts_legacy_telemetry_flag(self, mock_transport, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")
        mock_transport.request_json.return_value = {
            "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
            "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
        }

        SandboxesClient(mock_transport, sandbox_domain="s.dev").create(telemetry=True)

        sent_env = mock_transport.request_json.call_args.kwargs["json"]["env_vars"]
        assert sent_env == {"OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector:4318"}

    def test_create_prefers_otel_export_over_legacy_telemetry(self, mock_transport, monkeypatch):
        mock_transport.request_json.return_value = {
            "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
            "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
        }

        SandboxesClient(mock_transport, sandbox_domain="s.dev").create(
            otel_export=False,
            telemetry=True,
            env_vars={"APP_ENV": "test"},
        )

        sent_env = mock_transport.request_json.call_args.kwargs["json"]["env_vars"]
        assert sent_env == {"APP_ENV": "test"}

    def test_create_rejects_otel_export_without_endpoint(self, mock_transport, monkeypatch):
        monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
        monkeypatch.delenv("OTEL_EXPORTER_OTLP_HEADERS", raising=False)

        with pytest.raises(Leap0Error, match="OTEL_EXPORTER_OTLP_ENDPOINT"):
            SandboxesClient(mock_transport, sandbox_domain="s.dev").create(otel_export=True)


class TestCreateSandboxParams:
    def test_default_template_is_bookworm(self):
        assert CreateSandboxParams().template_name == "system/debian:bookworm"


class TestRichSandbox:
    def test_bound_service_methods_pass_sandbox(self):
        process = MagicMock()
        process.execute.return_value = MagicMock(stdout="Python 3.12")
        sandboxes = MagicMock()
        client = SimpleNamespace(
            _filesystem=MagicMock(),
            _git=MagicMock(),
            _process=process,
            _pty=MagicMock(),
            _lsp=MagicMock(),
            _ssh=MagicMock(),
            _code_interpreter=MagicMock(),
            _desktop=MagicMock(),
            sandboxes=sandboxes,
        )

        sandbox = RichSandbox(client, Sandbox(id="sbx-1"))
        result = sandbox.process.execute(command="python --version")

        process.execute.assert_called_once_with(sandbox, command="python --version")
        assert result.stdout == "Python 3.12"

    def test_refresh_updates_metadata(self):
        sandboxes = MagicMock()
        client = SimpleNamespace(
            _filesystem=MagicMock(),
            _git=MagicMock(),
            _process=MagicMock(),
            _pty=MagicMock(),
            _lsp=MagicMock(),
            _ssh=MagicMock(),
            _code_interpreter=MagicMock(),
            _desktop=MagicMock(),
            sandboxes=sandboxes,
        )
        sandbox = RichSandbox(client, Sandbox(id="sbx-1", state="starting"))
        sandboxes.get.return_value = RichSandbox(client, Sandbox(id="sbx-1", state="running"))

        sandbox.refresh()

        assert sandbox.state == "running"
