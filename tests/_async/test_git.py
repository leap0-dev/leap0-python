from __future__ import annotations

import asyncio

from leap0._async.git import AsyncGitClient


class TestAsyncGitClient:
    def test_clone(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"output": "cloned", "exit_code": 0}
            await AsyncGitClient(async_mock_transport).clone("sbx-1", url="https://github.com/test/repo.git", path="/workspace/repo")
            args, kwargs = async_mock_transport.request_json.call_args
            assert args[1] == "/v1/sandbox/sbx-1/git/clone"
            assert kwargs["json"]["url"] == "https://github.com/test/repo.git"

        asyncio.run(run())

    def test_status(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {"output": "", "exit_code": 0}
            await AsyncGitClient(async_mock_transport).status("sbx-1", path="/workspace/repo")
            assert "/git/status" in async_mock_transport.request_json.call_args[0][1]

        asyncio.run(run())
