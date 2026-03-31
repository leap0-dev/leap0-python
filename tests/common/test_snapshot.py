from __future__ import annotations

from leap0.common.snapshot import Snapshot, snapshot_id_of


class TestSnapshotIdOf:
    def test_from_string(self):
        assert snapshot_id_of("snap-123") == "snap-123"

    def test_from_snapshot(self):
        assert snapshot_id_of(Snapshot(snapshot_id="snap-abc", name="my-snap")) == "snap-abc"


class TestSnapshot:
    def test_id_property(self):
        assert Snapshot(snapshot_id="snap-1", name="test").id == "snap-1"

    def test_from_dict_full(self):
        s = Snapshot.from_dict({"snapshot_id": "snap-1", "name": "my-snap", "template_id": "tpl-1",
                                "vcpu": 2, "memory_mib": 1024, "disk_mib": 10240,
                                "network_policy": {"mode": "deny-all"}, "created_at": "2025-01-01"})
        assert s.snapshot_id == "snap-1"
        assert s.network_policy == {"mode": "deny-all"}

    def test_from_dict_minimal(self):
        s = Snapshot.from_dict({})
        assert s.snapshot_id == ""
        assert s.name == ""
