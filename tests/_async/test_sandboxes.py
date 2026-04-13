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
                _filesystem=SimpleNamespace(), _git=SimpleNamespace(), _process=SimpleNamespace(), _pty=SimpleNamespace(),
                _lsp=SimpleNamespace(), _ssh=SimpleNamespace(), _code_interpreter=SimpleNamespace(), _desktop=SimpleNamespace(),
            )
            client = AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev", sandbox_factory=lambda data: AsyncSandbox(fake_client, data))
            async_mock_transport.request_json.return_value = {
                "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
                "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
            }
            result = await client.create(template_name="my-tpl")
            assert isinstance(result, AsyncSandbox)

        asyncio.run(run())

    def test_list(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {
                "items": [{
                    "id": "sbx-1", "template_id": "tpl-1", "pod_id": "pod-1", "state": "running",
                    "created_at": "2026-01-01T00:00:00Z",
                }],
                "total_items": 1,
            }

            result = await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").list(
                state="running", sort="state", order_by="asc", page=2, page_size=10,
            )

            args, kwargs = async_mock_transport.request_json.call_args
            assert args == ("GET", "/v1/sandboxes")
            assert kwargs["params"] == {
                "state": "running",
                "sort": "state",
                "order-by": "asc",
                "page": 2,
                "page-size": 10,
            }
            assert result.total_items == 1

        asyncio.run(run())

    def test_list_validates_input(self, async_mock_transport):
        async def run() -> None:
            with pytest.raises(Leap0Error, match="state must be one of"):
                await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").list(state="deleted")

        asyncio.run(run())

    def test_list_omits_state_when_not_provided(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"items": [], "total_items": 0}

            await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").list()

            assert async_mock_transport.request_json.call_args[1]["params"] == {
                "sort": "created_at",
                "order-by": "desc",
                "page": 1,
                "page-size": 20,
            }

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

    def test_pause_forwards_http_timeout(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {
                "id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
                "disk_mib": 10240, "state": "paused", "auto_pause": False, "created_at": "",
            }

            await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").pause(
                "sbx-1",
                http_timeout=4.0,
            )

            assert async_mock_transport.request_json.call_args.kwargs["timeout"] == 4.0

        asyncio.run(run())

    def test_get_user_home_dir(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"user_home_dir": "/home/steven"}

            result = await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").get_user_home_dir("sbx-1")

            assert result == "/home/steven"
            assert async_mock_transport.request_json.call_args[0][1] == "/v1/sandbox/sbx-1/system/user-home-dir"

        asyncio.run(run())

    def test_get_workdir(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"workdir": "/home/steve/agent"}

            result = await AsyncSandboxesClient(async_mock_transport, sandbox_domain="s.dev").get_workdir("sbx-1")

            assert result == "/home/steve/agent"
            assert async_mock_transport.request_json.call_args[0][1] == "/v1/sandbox/sbx-1/system/workdir"

        asyncio.run(run())



class TestAsyncSandbox:
    def test_pause_forwards_http_timeout(self):
        async def run() -> None:
            sandboxes = SimpleNamespace()
            fake_client = SimpleNamespace(
                _filesystem=SimpleNamespace(), _git=SimpleNamespace(), _process=SimpleNamespace(), _pty=SimpleNamespace(),
                _lsp=SimpleNamespace(), _ssh=SimpleNamespace(), _code_interpreter=SimpleNamespace(), _desktop=SimpleNamespace(),
                sandboxes=sandboxes,
            )

            async def pause(sandbox: object, http_timeout: float | None = None):
                assert http_timeout == 2.5
                return AsyncSandbox(fake_client, Sandbox(id="sbx-1", state="paused"))

            sandboxes.pause = pause
            sandbox = AsyncSandbox(fake_client, Sandbox(id="sbx-1", state="running"))

            await sandbox.pause(http_timeout=2.5)

            assert sandbox.state == "paused"

        asyncio.run(run())

    def test_runtime_info_helpers_delegate_to_sandboxes_client(self):
        async def run() -> None:
            sandboxes = SimpleNamespace()
            fake_client = SimpleNamespace(
                _filesystem=SimpleNamespace(), _git=SimpleNamespace(), _process=SimpleNamespace(), _pty=SimpleNamespace(),
                _lsp=SimpleNamespace(), _ssh=SimpleNamespace(), _code_interpreter=SimpleNamespace(), _desktop=SimpleNamespace(),
                sandboxes=sandboxes,
            )

            async def get_user_home_dir(sandbox: object, http_timeout: float | None = None):
                assert http_timeout == 1.5
                return "/home/steven"

            async def get_workdir(sandbox: object, http_timeout: float | None = None):
                assert http_timeout == 2.5
                return "/home/steve/agent"

            sandboxes.get_user_home_dir = get_user_home_dir
            sandboxes.get_workdir = get_workdir
            sandbox = AsyncSandbox(fake_client, Sandbox(id="sbx-1", state="running"))

            assert await sandbox.get_user_home_dir(http_timeout=1.5) == "/home/steven"
            assert await sandbox.get_workdir(http_timeout=2.5) == "/home/steve/agent"

        asyncio.run(run())
