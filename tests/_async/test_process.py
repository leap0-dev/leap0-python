from __future__ import annotations

import asyncio

from leap0._async.process import AsyncProcessClient


class TestAsyncProcessClient:
    def test_execute(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"exit_code": 0, "stdout": "hello", "stderr": "warn"}
            result = await AsyncProcessClient(async_mock_transport).execute("sbx-1", command="echo hello")
            assert result.exit_code == 0
            assert result.stdout == "hello"
            assert result.stderr == "warn"
            assert async_mock_transport.request_json.call_args[0][:2] == ("POST", "/v1/sandbox/sbx-1/process/execute")

        asyncio.run(run())
