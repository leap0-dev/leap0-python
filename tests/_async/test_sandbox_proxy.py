from __future__ import annotations

import asyncio

from leap0._async.sandbox import _AsyncSandboxServiceProxy


class _Sandbox:
    pass


class _Service:
    async def async_method(self, sandbox, value: int) -> tuple[object, int]:
        return sandbox, value

    def sync_method(self, sandbox, value: int) -> tuple[object, int]:
        return sandbox, value


class TestAsyncSandboxServiceProxy:
    def test_sync_methods_are_not_awaited(self):
        sandbox = _Sandbox()
        proxy = _AsyncSandboxServiceProxy(_Service(), sandbox)

        assert proxy.sync_method(3) == (sandbox, 3)

    def test_async_methods_are_bound(self):
        async def run() -> None:
            sandbox = _Sandbox()
            proxy = _AsyncSandboxServiceProxy(_Service(), sandbox)
            assert await proxy.async_method(3) == (sandbox, 3)

        asyncio.run(run())
