from __future__ import annotations

import asyncio
from types import SimpleNamespace

from leap0._async.sandbox import AsyncSandbox, AsyncSandboxesClient
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
