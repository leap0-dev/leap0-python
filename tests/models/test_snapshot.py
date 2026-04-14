from __future__ import annotations

import pytest

from leap0.models.snapshot import Snapshot, snapshot_id_of


class TestSnapshotIdOf:
    def test_from_string(self):
        assert snapshot_id_of("snap-123") == "snap-123"

    def test_from_snapshot(self):
        assert snapshot_id_of(Snapshot(id="snap-abc", name="my-snap")) == "snap-abc"


class TestSnapshot:
    def test_id_field(self):
        assert Snapshot(id="snap-1", name="test").id == "snap-1"

    def test_from_dict_full(self):
        s = Snapshot.from_dict({"id": "snap-1", "name": "my-snap", "template_id": "tpl-1",
                                "vcpu": 2, "memory": 1024, "disk": 10240,
                                "network_policy": {"mode": "deny-all"}, "created_at": "2025-01-01"})
        assert s.id == "snap-1"
        assert s.state is None
        assert s.network_policy == {"mode": "deny-all"}

    def test_from_dict_with_state(self):
        s = Snapshot.from_dict({"id": "snap-1", "name": "my-snap", "state": "paused"})
        assert s.state == "paused"

    def test_from_dict_strips_required_fields(self):
        s = Snapshot.from_dict({"id": " snap-1 ", "name": " my-snap "})
        assert s.id == "snap-1"
        assert s.name == "my-snap"

    def test_from_dict_requires_id(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'id'"):
            Snapshot.from_dict({"name": "my-snap"})

    def test_from_dict_rejects_empty_id(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'id'"):
            Snapshot.from_dict({"id": "", "name": "my-snap"})

    def test_from_dict_rejects_whitespace_only_id(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'id'"):
            Snapshot.from_dict({"id": "   ", "name": "my-snap"})

    def test_from_dict_rejects_non_string_id(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'id'"):
            Snapshot.from_dict({"id": 123, "name": "my-snap"})

    def test_from_dict_requires_name(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'name'"):
            Snapshot.from_dict({"id": "snap-1"})

    def test_from_dict_rejects_empty_name(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'name'"):
            Snapshot.from_dict({"id": "snap-1", "name": ""})

    def test_from_dict_rejects_whitespace_only_name(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'name'"):
            Snapshot.from_dict({"id": "snap-1", "name": "   "})

    def test_from_dict_rejects_non_string_name(self):
        with pytest.raises(ValueError, match="Snapshot response missing required non-empty string 'name'"):
            Snapshot.from_dict({"id": "snap-1", "name": 123})
