from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from leap0._async.snapshots import AsyncSnapshotsClient
from leap0.models.snapshot import Snapshot


class TestAsyncSnapshotsClient:
    def test_create(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {
                "id": "snap-1", "name": "s", "template_id": "t",
                "vcpu": 1, "memory_mib": 512, "disk_mib": 10240, "network_policy": None, "created_at": "",
            }
            await AsyncSnapshotsClient(async_mock_transport).create("sbx-1", name="my-snap")
            args, kwargs = async_mock_transport.request_json.call_args
            assert args[1] == "/v1/sandbox/sbx-1/snapshot/create"
            assert kwargs["json"]["name"] == "my-snap"

        asyncio.run(run())

    def test_delete_accepts_object(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request.return_value = MagicMock(status_code=204)
            await AsyncSnapshotsClient(async_mock_transport).delete(Snapshot(id="snap-obj", name="n"))
            assert "snap-obj" in async_mock_transport.request.call_args[0][1]

        asyncio.run(run())
