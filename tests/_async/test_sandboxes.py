from __future__ import annotations

import asyncio
import pytest
from types import SimpleNamespace

from leap0._async.sandbox import AsyncSandbox, AsyncSandboxesClient
from leap0.models.errors import Leap0Error
from leap0.models.sandbox import Sandbox


class TestAsyncSandboxesClient:
    def test_create(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {
                "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
                "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
            }
            result = await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").create(template_name="my-tpl", vcpu=2, memory_mib=2048)
            args, kwargs = async_mock_transport.request_json.call_args
            assert args == ("POST", "/v1/sandbox")
            assert kwargs["json"]["template_name"] == "my-tpl"
            assert result.id == "sbx-1"

        asyncio.run(run())

    def test_factory_returns_async_sandbox(self, async_mock_transport):
        async def run() -> None:
            fake_client = SimpleNamespace(
                filesystem=SimpleNamespace(), git=SimpleNamespace(), process=SimpleNamespace(), pty=SimpleNamespace(),
                lsp=SimpleNamespace(), ssh=SimpleNamespace(), code_interpreter=SimpleNamespace(), desktop=SimpleNamespace(),
            )
            client = AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev", sandbox_factory=lambda data: AsyncSandbox(fake_client, data))
            async_mock_transport.request_json.return_value = {
                "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
                "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
            }
            result = await client.create(template_name="my-tpl")
            assert isinstance(result, AsyncSandbox)

        asyncio.run(run())

    def test_create_injects_otel_env_when_enabled(self, async_mock_transport, monkeypatch):
        async def run() -> None:
            monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")
            monkeypatch.setenv("OTEL_EXPORTER_OTLP_HEADERS", "authorization=token")
            async_mock_transport.request_json.return_value = {
                "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
                "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
            }

            await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").create(
                otel_export=True,
                env_vars={"APP_ENV": "test"},
            )

            sent_env = async_mock_transport.request_json.call_args.kwargs["json"]["env_vars"]
            assert sent_env == {
                "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector:4318",
                "OTEL_EXPORTER_OTLP_HEADERS": "authorization=token",
                "APP_ENV": "test",
            }

        asyncio.run(run())

    def test_create_rejects_otel_export_without_endpoint(self, async_mock_transport, monkeypatch):
        async def run() -> None:
            monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
            monkeypatch.delenv("OTEL_EXPORTER_OTLP_HEADERS", raising=False)

            with pytest.raises(Leap0Error, match="OTEL_EXPORTER_OTLP_ENDPOINT"):
                await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").create(otel_export=True)

        asyncio.run(run())
