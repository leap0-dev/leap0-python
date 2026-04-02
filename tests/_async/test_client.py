from __future__ import annotations

import asyncio

from leap0._async.client import AsyncLeap0Client
from leap0._async.sandbox import AsyncSandbox
from leap0.models.sandbox import Sandbox


class _FakeAsyncTransport:
    def __init__(self, **_kwargs):
        self.closed = False

    async def close(self):
        self.closed = True


def test_async_client_native_transport(monkeypatch):
    import leap0._async.client as async_client_module

    monkeypatch.setattr(async_client_module, "AsyncTransport", _FakeAsyncTransport)

    async def run() -> None:
        client = AsyncLeap0Client(api_key="test")
        try:
            _ = client.filesystem
        except AttributeError as exc:
            assert "sandbox.filesystem" in str(exc)
        else:
            raise AssertionError("expected sandbox-scoped service access to fail")

        async def fake_get(_sandbox_id: str) -> AsyncSandbox:
            return AsyncSandbox(client, Sandbox(id="sbx-1", state="running"))

        client.sandboxes.get = fake_get  # type: ignore[method-assign]

        sandbox = await client.get_sandbox("sbx-1")
        assert isinstance(sandbox, AsyncSandbox)

        await client.close()
        assert client._transport.closed is True

    asyncio.run(run())
