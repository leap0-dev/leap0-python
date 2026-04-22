from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from leap0._async.snapshots import AsyncSnapshotsClient
from leap0.models.errors import Leap0Error
from leap0.models.snapshot import Snapshot


class TestAsyncSnapshotsClient:
    def test_delete_accepts_object(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request.return_value = MagicMock(status_code=204)
            await AsyncSnapshotsClient(async_mock_transport).delete(Snapshot(id="snap-obj", name="n"))
            assert "snap-obj" in async_mock_transport.request.call_args[0][1]

        asyncio.run(run())

    def test_list(self, async_mock_transport):
        async def run() -> None:
            async_mock_transport.request_json.return_value = {
                "items": [{
                    "id": "snap-1", "name": "snap-a", "template_id": "tpl-1", "vcpu": 2,
                    "memory": 1024, "disk": 4096, "created_at": "2026-01-01T00:00:00Z",
                }],
                "total_items": 1,
            }

            result = await AsyncSnapshotsClient(async_mock_transport).list(query="snap", sort="template_id", order_by="asc", page=2, page_size=5)

            args, kwargs = async_mock_transport.request_json.call_args
            assert args == ("GET", "/v1/snapshots")
            assert kwargs["params"] == {
                "query": "snap",
                "sort": "template_id",
                "order-by": "asc",
                "page": 2,
                "page-size": 5,
            }
            assert result.total_items == 1

        asyncio.run(run())

    def test_list_validates_page_size(self, async_mock_transport):
        async def run() -> None:
            with pytest.raises(Leap0Error, match="page_size"):
                await AsyncSnapshotsClient(async_mock_transport).list(page_size=101)

        asyncio.run(run())
