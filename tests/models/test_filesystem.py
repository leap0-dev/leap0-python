from __future__ import annotations

from leap0.models.filesystem import (
    EditFileResult, EditResult, FileEdit, FileInfo, LsResult, SearchMatch, TreeEntry, TreeResult,
)


class TestFileInfo:
    def test_full_dict(self):
        f = FileInfo.from_dict({"name": "main.py", "path": "/workspace/main.py", "is_dir": False,
                                "size": 1234, "mode": "644", "mtime": 1700000000, "owner": "root",
                                "group": "root", "is_symlink": True, "link_target": "/usr/bin/python"})
        assert f.name == "main.py"
        assert f.size == 1234
        assert f.is_symlink is True

    def test_empty_dict(self):
        f = FileInfo.from_dict({})
        assert f.name == ""
        assert f.size == 0


class TestLsResult:
    def test_from_dict(self):
        r = LsResult.from_dict({"items": [{"name": "a.py", "path": "/a.py"}, {"name": "b.py", "path": "/b.py"}]})
        assert len(r.items) == 2

    def test_empty_items(self):
        assert LsResult.from_dict({"items": []}).items == []

    def test_missing_items(self):
        assert LsResult.from_dict({}).items == []


class TestFileEdit:
    def test_to_dict(self):
        assert FileEdit(find="hello", replace="world").to_dict() == {"find": "hello", "replace": "world"}

    def test_to_dict_empty_replace(self):
        assert FileEdit(find="delete_me").to_dict() == {"find": "delete_me", "replace": ""}


class TestEditFileResult:
    def test_from_dict(self):
        r = EditFileResult.from_dict({"diff": "--- a\n+++ b", "replacements": 3})
        assert r.replacements == 3

    def test_empty_dict(self):
        assert EditFileResult.from_dict({}).diff == ""


class TestEditResult:
    def test_from_dict(self):
        r = EditResult.from_dict({"file": "a.py", "success": True, "error": ""})
        assert r.success is True


class TestSearchMatch:
    def test_from_dict(self):
        m = SearchMatch.from_dict({"path": "/a.py", "line": 42, "content": "TODO"})
        assert m.line == 42

    def test_empty_dict(self):
        assert SearchMatch.from_dict({}).line == 0


class TestTreeEntry:
    def test_with_children(self):
        t = TreeEntry.from_dict({"name": "src", "type": "directory",
                                 "children": [{"name": "main.py", "type": "file"}]})
        assert len(t.children) == 1
        assert t.children[0].name == "main.py"

    def test_empty_dict(self):
        t = TreeEntry.from_dict({})
        assert t.name == ""
        assert t.children == []


class TestTreeResult:
    def test_from_dict(self):
        assert len(TreeResult.from_dict({"items": [{"name": "a", "type": "file"}]}).items) == 1

    def test_missing_items(self):
        assert TreeResult.from_dict({}).items == []
