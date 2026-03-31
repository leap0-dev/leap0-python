from __future__ import annotations

from unittest.mock import MagicMock

from leap0.snapshots import SnapshotsClient
from leap0.common.snapshot import Snapshot


class TestSnapshotsClient:
    def test_create(self, mock_transport):
        mock_transport.request_json.return_value = {
            "snapshot_id": "snap-1", "name": "s", "template_id": "t",
            "vcpu": 1, "memory_mib": 512, "disk_mib": 10240, "network_policy": None, "created_at": "",
        }
        SnapshotsClient(mock_transport).create("sbx-1", name="my-snap")
        args, kwargs = mock_transport.request_json.call_args
        assert args[1] == "/v1/sandbox/sbx-1/snapshot/create"
        assert kwargs["json"]["name"] == "my-snap"

    def test_delete(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        SnapshotsClient(mock_transport).delete("snap-1")
        assert "snap-1" in mock_transport.request.call_args[0][1]

    def test_delete_accepts_object(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        SnapshotsClient(mock_transport).delete(Snapshot(snapshot_id="snap-obj", name="n"))
        assert "snap-obj" in mock_transport.request.call_args[0][1]
