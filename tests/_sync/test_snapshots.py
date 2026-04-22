from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from leap0.models.errors import Leap0Error
from leap0._sync.snapshots import SnapshotsClient
from leap0.models.snapshot import RestoreSnapshotParams, Snapshot


class TestSnapshotsClient:
    def test_delete(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        SnapshotsClient(mock_transport).delete("snap-1")
        assert "snap-1" in mock_transport.request.call_args[0][1]

    def test_delete_accepts_object(self, mock_transport):
        mock_transport.request.return_value = MagicMock(status_code=204)
        SnapshotsClient(mock_transport).delete(Snapshot(id="snap-obj", name="n"))
        assert "snap-obj" in mock_transport.request.call_args[0][1]

    def test_list(self, mock_transport):
        mock_transport.request_json.return_value = {
            "items": [{
                "id": "snap-1", "name": "snap-a", "template_id": "tpl-1", "vcpu": 2,
                "memory": 1024, "disk": 4096, "created_at": "2026-01-01T00:00:00Z",
            }],
            "total_items": 1,
        }

        result = SnapshotsClient(mock_transport).list(query="snap", sort="template_id", order_by="asc", page=2, page_size=5)

        args, kwargs = mock_transport.request_json.call_args
        assert args == ("GET", "/v1/snapshots")
        assert kwargs["params"] == {
            "query": "snap",
            "sort": "template_id",
            "order-by": "asc",
            "page": 2,
            "page-size": 5,
        }
        assert result.total_items == 1

    def test_list_validates_page_size(self, mock_transport):
        with pytest.raises(Leap0Error, match="page_size"):
            SnapshotsClient(mock_transport).list(page_size=101)

    def test_restore(self, mock_transport):
        mock_transport.request_json.return_value = {
            "id": "sbx-1",
            "template_id": "tpl-1",
            "vcpu": 2,
            "memory": 1024,
            "disk": 4096,
            "state": "running",
            "created_at": "2026-01-01T00:00:00Z",
        }

        result = SnapshotsClient(mock_transport).restore(snapshot_name="snap-1")

        args, kwargs = mock_transport.request_json.call_args
        assert args == ("POST", "/v1/snapshot/restore")
        assert kwargs["json"] == RestoreSnapshotParams(snapshot_name="snap-1").to_payload()
        assert kwargs["expected_status"] == 201
        assert result.id == "sbx-1"
        assert result.template_id == "tpl-1"
        assert result.state == "running"

    def test_restore_validates_input(self, mock_transport):
        with pytest.raises(Leap0Error, match="snapshot_name"):
            SnapshotsClient(mock_transport).restore(snapshot_name="   ")


class TestRestoreSnapshotParams:
    def test_payload_trims_snapshot_name(self):
        payload = RestoreSnapshotParams(snapshot_name="  snap-1  ").to_payload()
        assert payload["snapshot_name"] == "snap-1"
