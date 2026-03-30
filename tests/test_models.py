"""Tests for model from_dict parsing, edge cases, and helper methods."""
from __future__ import annotations

import base64

import pytest

from leap0.models import (
    CodeContext,
    CodeExecutionError,
    CodeExecutionOutput,
    CodeExecutionResult,
    DesktopDisplayInfo,
    DesktopHealth,
    DesktopPointerPosition,
    DesktopProcessErrors,
    DesktopProcessLogs,
    DesktopProcessRestart,
    DesktopProcessStatus,
    DesktopProcessStatusList,
    DesktopRecordingStatus,
    DesktopRecordingSummary,
    DesktopWindow,
    EditFileResult,
    EditResult,
    ExecutionLogs,
    FileEdit,
    FileInfo,
    GitCommitResult,
    GitResult,
    ImageConfig,
    LsResult,
    LspResponse,
    ProcessResult,
    PtySession,
    Sandbox,
    SandboxStatus,
    SearchMatch,
    Snapshot,
    SshAccess,
    SshValidation,
    StreamEvent,
    Template,
    TreeEntry,
    TreeResult,
    sandbox_id_of,
    snapshot_id_of,
)


# sandbox_id_of / snapshot_id_of

class TestSandboxIdOf:
    def test_from_string(self):
        assert sandbox_id_of("sbx-123") == "sbx-123"

    def test_from_sandbox(self):
        s = Sandbox(id="sbx-abc")
        assert sandbox_id_of(s) == "sbx-abc"

    def test_from_sandbox_status(self):
        s = SandboxStatus(
            id="sbx-xyz", template_id="t", vcpu=1, memory_mib=512,
            disk_mib=10240, state="running", auto_pause=False, created_at="",
        )
        assert sandbox_id_of(s) == "sbx-xyz"


class TestSnapshotIdOf:
    def test_from_string(self):
        assert snapshot_id_of("snap-123") == "snap-123"

    def test_from_snapshot(self):
        s = Snapshot(snapshot_id="snap-abc", name="my-snap")
        assert snapshot_id_of(s) == "snap-abc"


# Sandbox

class TestSandbox:
    def test_full_dict(self):
        data = {
            "id": "sbx-1",
            "template_id": "tpl-1",
            "vcpu": 2,
            "memory_mib": 2048,
            "disk_mib": 10240,
            "state": "running",
            "auto_pause": True,
            "created_at": "2025-01-01",
            "network_policy": {"mode": "allow-all"},
        }
        s = Sandbox.from_dict(data)  # type: ignore[arg-type]
        assert s.id == "sbx-1"
        assert s.template_id == "tpl-1"
        assert s.vcpu == 2
        assert s.memory_mib == 2048
        assert s.disk_mib == 10240
        assert s.state == "running"
        assert s.auto_pause is True
        assert s.created_at == "2025-01-01"
        assert s.network_policy == {"mode": "allow-all"}

    def test_minimal_dict(self):
        data = {"id": "sbx-2"}
        s = Sandbox.from_dict(data)  # type: ignore[arg-type]
        assert s.id == "sbx-2"
        assert s.template_id == ""
        assert s.vcpu == 0
        assert s.state == "starting"
        assert s.auto_pause is False
        assert s.network_policy is None


# SandboxStatus

class TestSandboxStatus:
    def test_full_dict(self):
        data = {
            "id": "sbx-1",
            "template_id": "tpl-1",
            "vcpu": 4,
            "memory_mib": 4096,
            "disk_mib": 10240,
            "state": "paused",
            "auto_pause": True,
            "created_at": "2025-01-01",
        }
        s = SandboxStatus.from_dict(data)  # type: ignore[arg-type]
        assert s.id == "sbx-1"
        assert s.state == "paused"
        assert s.vcpu == 4

    def test_tolerant_parsing_missing_keys(self):
        """SandboxStatus.from_dict should not raise on missing keys."""
        data = {"id": "sbx-3"}
        s = SandboxStatus.from_dict(data)  # type: ignore[arg-type]
        assert s.id == "sbx-3"
        assert s.template_id == ""
        assert s.vcpu == 0
        assert s.memory_mib == 0
        assert s.disk_mib == 0
        assert s.state == "starting"
        assert s.auto_pause is False
        assert s.created_at == ""

    def test_empty_dict(self):
        s = SandboxStatus.from_dict({})  # type: ignore[arg-type]
        assert s.id == ""
        assert s.state == "starting"


# Snapshot

class TestSnapshot:
    def test_id_property(self):
        s = Snapshot(snapshot_id="snap-1", name="test")
        assert s.id == "snap-1"

    def test_from_dict_full(self):
        data = {
            "snapshot_id": "snap-1",
            "name": "my-snap",
            "template_id": "tpl-1",
            "vcpu": 2,
            "memory_mib": 1024,
            "disk_mib": 10240,
            "network_policy": {"mode": "deny-all"},
            "created_at": "2025-01-01",
        }
        s = Snapshot.from_dict(data)  # type: ignore[arg-type]
        assert s.snapshot_id == "snap-1"
        assert s.name == "my-snap"
        assert s.network_policy == {"mode": "deny-all"}

    def test_from_dict_minimal(self):
        s = Snapshot.from_dict({})  # type: ignore[arg-type]
        assert s.snapshot_id == ""
        assert s.name == ""


# FileInfo / LsResult

class TestFileInfo:
    def test_full_dict(self):
        data = {
            "name": "main.py",
            "path": "/workspace/main.py",
            "is_dir": False,
            "size": 1234,
            "mode": "644",
            "mtime": 1700000000,
            "owner": "root",
            "group": "root",
            "is_symlink": True,
            "link_target": "/usr/bin/python",
        }
        f = FileInfo.from_dict(data)  # type: ignore[arg-type]
        assert f.name == "main.py"
        assert f.size == 1234
        assert f.is_symlink is True
        assert f.link_target == "/usr/bin/python"

    def test_empty_dict(self):
        f = FileInfo.from_dict({})  # type: ignore[arg-type]
        assert f.name == ""
        assert f.path == ""
        assert f.is_dir is False
        assert f.size == 0


class TestLsResult:
    def test_from_dict(self):
        data = {"items": [{"name": "a.py", "path": "/a.py"}, {"name": "b.py", "path": "/b.py"}]}
        r = LsResult.from_dict(data)  # type: ignore[arg-type]
        assert len(r.items) == 2
        assert r.items[0].name == "a.py"

    def test_empty_items(self):
        r = LsResult.from_dict({"items": []})  # type: ignore[arg-type]
        assert r.items == []

    def test_missing_items(self):
        r = LsResult.from_dict({})  # type: ignore[arg-type]
        assert r.items == []


# FileEdit

class TestFileEdit:
    def test_to_dict(self):
        e = FileEdit(find="hello", replace="world")
        assert e.to_dict() == {"find": "hello", "replace": "world"}

    def test_to_dict_empty_replace(self):
        e = FileEdit(find="delete_me")
        assert e.to_dict() == {"find": "delete_me", "replace": ""}


# EditFileResult / EditResult

class TestEditFileResult:
    def test_from_dict(self):
        r = EditFileResult.from_dict({"diff": "--- a\n+++ b", "replacements": 3})  # type: ignore[arg-type]
        assert r.diff == "--- a\n+++ b"
        assert r.replacements == 3

    def test_empty_dict(self):
        r = EditFileResult.from_dict({})  # type: ignore[arg-type]
        assert r.diff == ""
        assert r.replacements == 0


class TestEditResult:
    def test_from_dict(self):
        r = EditResult.from_dict({"file": "a.py", "success": True, "error": ""})  # type: ignore[arg-type]
        assert r.file == "a.py"
        assert r.success is True


# SearchMatch

class TestSearchMatch:
    def test_from_dict(self):
        m = SearchMatch.from_dict({"path": "/a.py", "line": 42, "content": "TODO"})  # type: ignore[arg-type]
        assert m.path == "/a.py"
        assert m.line == 42
        assert m.content == "TODO"

    def test_empty_dict(self):
        m = SearchMatch.from_dict({})  # type: ignore[arg-type]
        assert m.line == 0


# TreeEntry / TreeResult

class TestTreeEntry:
    def test_from_dict_with_children(self):
        data = {
            "name": "src",
            "type": "directory",
            "children": [
                {"name": "main.py", "type": "file"},
            ],
        }
        t = TreeEntry.from_dict(data)  # type: ignore[arg-type]
        assert t.name == "src"
        assert t.type == "directory"
        assert len(t.children) == 1
        assert t.children[0].name == "main.py"
        assert t.children[0].type == "file"
        assert t.children[0].children == []

    def test_empty_dict(self):
        t = TreeEntry.from_dict({})  # type: ignore[arg-type]
        assert t.name == ""
        assert t.type == "file"
        assert t.children == []


class TestTreeResult:
    def test_from_dict(self):
        r = TreeResult.from_dict({"items": [{"name": "a", "type": "file"}]})  # type: ignore[arg-type]
        assert len(r.items) == 1

    def test_missing_items(self):
        r = TreeResult.from_dict({})  # type: ignore[arg-type]
        assert r.items == []


# GitResult / GitCommitResult

class TestGitResult:
    def test_from_dict(self):
        r = GitResult.from_dict({"output": "ok", "exit_code": 0})  # type: ignore[arg-type]
        assert r.output == "ok"
        assert r.exit_code == 0

    def test_empty_dict(self):
        r = GitResult.from_dict({})  # type: ignore[arg-type]
        assert r.output == ""
        assert r.exit_code == 0


class TestGitCommitResult:
    def test_with_result(self):
        data = {"sha": "abc123", "result": {"output": "committed", "exit_code": 0}}
        r = GitCommitResult.from_dict(data)  # type: ignore[arg-type]
        assert r.sha == "abc123"
        assert r.result is not None
        assert r.result.output == "committed"

    def test_without_result(self):
        r = GitCommitResult.from_dict({"sha": "abc"})  # type: ignore[arg-type]
        assert r.sha == "abc"
        assert r.result is None

    def test_null_result(self):
        r = GitCommitResult.from_dict({"sha": None, "result": None})  # type: ignore[arg-type]
        assert r.sha is None
        assert r.result is None


# ProcessResult

class TestProcessResult:
    def test_from_dict(self):
        r = ProcessResult.from_dict({"exit_code": 1, "result": "error output"})  # type: ignore[arg-type]
        assert r.exit_code == 1
        assert r.result == "error output"


# SshAccess / SshValidation

class TestSshAccess:
    def test_from_dict(self):
        data = {
            "id": "ssh-1",
            "password": "secret",
            "ssh_command": "ssh user@host",
            "sandbox_id": "sbx-1",
            "expires_at": "2025-12-31",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-01",
        }
        s = SshAccess.from_dict(data)  # type: ignore[arg-type]
        assert s.id == "ssh-1"
        assert s.password == "secret"
        assert s.ssh_command == "ssh user@host"


class TestSshValidation:
    def test_from_dict(self):
        v = SshValidation.from_dict({"valid": True, "sandbox_id": "sbx-1"})  # type: ignore[arg-type]
        assert v.valid is True
        assert v.sandbox_id == "sbx-1"

    def test_empty_dict(self):
        v = SshValidation.from_dict({})  # type: ignore[arg-type]
        assert v.valid is False
        assert v.sandbox_id == ""


# PtySession

class TestPtySession:
    def test_from_dict_with_id(self):
        data = {"id": "pty_1", "cwd": "/home/user", "cols": 80, "rows": 24, "active": True}
        p = PtySession.from_dict(data)  # type: ignore[arg-type]
        assert p.id == "pty_1"
        assert p.cwd == "/home/user"
        assert p.cols == 80
        assert p.active is True

    def test_from_dict_with_session_id(self):
        """Should fall back to session_id when id is missing."""
        data = {"session_id": "pty_2", "cols": 120, "rows": 40}
        p = PtySession.from_dict(data)  # type: ignore[arg-type]
        assert p.id == "pty_2"

    def test_prefers_id_over_session_id(self):
        data = {"id": "pty_a", "session_id": "pty_b"}
        p = PtySession.from_dict(data)  # type: ignore[arg-type]
        assert p.id == "pty_a"

    def test_empty_dict(self):
        p = PtySession.from_dict({})  # type: ignore[arg-type]
        assert p.id == ""
        assert p.envs == {}
        assert p.lazy_start is False


# LspResponse

class TestLspResponse:
    def test_from_dict(self):
        r = LspResponse.from_dict({"success": True})  # type: ignore[arg-type]
        assert r.success is True

    def test_empty_dict(self):
        r = LspResponse.from_dict({})  # type: ignore[arg-type]
        assert r.success is False


# ImageConfig

class TestImageConfig:
    def test_from_dict_full(self):
        data = {
            "entrypoint": ["/bin/sh"],
            "cmd": ["-c", "echo hi"],
            "working_dir": "/workspace",
            "env": {"PATH": "/usr/bin"},
        }
        c = ImageConfig.from_dict(data)  # type: ignore[arg-type]
        assert c.entrypoint == ["/bin/sh"]
        assert c.cmd == ["-c", "echo hi"]
        assert c.working_dir == "/workspace"
        assert c.env == {"PATH": "/usr/bin"}

    def test_null_lists(self):
        data = {"entrypoint": None, "cmd": None}
        c = ImageConfig.from_dict(data)  # type: ignore[arg-type]
        assert c.entrypoint == []
        assert c.cmd == []


# Template

class TestTemplate:
    def test_from_dict_full(self):
        data = {
            "id": "tpl-1",
            "name": "my-template",
            "digest": "sha256:abc",
            "image_config": {"entrypoint": ["/bin/sh"]},
            "is_system": False,
            "created_at": "2025-01-01",
        }
        t = Template.from_dict(data)  # type: ignore[arg-type]
        assert t.id == "tpl-1"
        assert t.name == "my-template"
        assert t.image_config is not None
        assert t.image_config.entrypoint == ["/bin/sh"]

    def test_from_dict_null_image_config(self):
        data = {"id": "tpl-2", "name": "t2", "digest": "", "image_config": None, "is_system": True, "created_at": ""}
        t = Template.from_dict(data)  # type: ignore[arg-type]
        assert t.image_config is None
        assert t.is_system is True


# CodeExecutionOutput

class TestCodeExecutionOutput:
    def test_from_dict_full(self):
        data = {
            "is_primary": True,
            "text": "hello",
            "png": base64.b64encode(b"PNG_DATA").decode(),
            "svg": "<svg></svg>",
            "html": "<p>hi</p>",
            "markdown": "# hi",
            "json": {"key": "val"},
            "jpeg": base64.b64encode(b"JPEG_DATA").decode(),
            "pdf": base64.b64encode(b"PDF_DATA").decode(),
            "latex": "\\frac{1}{2}",
            "javascript": "console.log('hi')",
            "extra": {"custom": True},
        }
        o = CodeExecutionOutput.from_dict(data)  # type: ignore[arg-type]
        assert o.is_primary is True
        assert o.is_main_result is True
        assert o.text == "hello"
        assert o.json_data == {"key": "val"}
        assert o.extra == {"custom": True}

    def test_is_main_result_alias(self):
        """is_main_result should accept is_main_result key from dict."""
        data = {"is_main_result": True}
        o = CodeExecutionOutput.from_dict(data)  # type: ignore[arg-type]
        assert o.is_primary is True
        assert o.is_main_result is True

    def test_png_bytes(self):
        raw = b"PNG_DATA"
        o = CodeExecutionOutput(png=base64.b64encode(raw).decode())
        assert o.png_bytes() == raw

    def test_png_bytes_none(self):
        o = CodeExecutionOutput()
        assert o.png_bytes() is None

    def test_jpeg_bytes(self):
        raw = b"JPEG"
        o = CodeExecutionOutput(jpeg=base64.b64encode(raw).decode())
        assert o.jpeg_bytes() == raw

    def test_jpeg_bytes_none(self):
        o = CodeExecutionOutput()
        assert o.jpeg_bytes() is None

    def test_pdf_bytes(self):
        raw = b"PDF"
        o = CodeExecutionOutput(pdf=base64.b64encode(raw).decode())
        assert o.pdf_bytes() == raw

    def test_pdf_bytes_none(self):
        o = CodeExecutionOutput()
        assert o.pdf_bytes() is None

    def test_empty_dict(self):
        o = CodeExecutionOutput.from_dict({})  # type: ignore[arg-type]
        assert o.is_primary is False
        assert o.text is None
        assert o.png is None


# CodeExecutionError

class TestCodeExecutionError:
    def test_from_dict(self):
        e = CodeExecutionError.from_dict({"name": "ValueError", "value": "bad", "traceback": "line 1"})  # type: ignore[arg-type]
        assert e.name == "ValueError"
        assert e.value == "bad"
        assert e.traceback == "line 1"

    def test_empty_dict(self):
        e = CodeExecutionError.from_dict({})  # type: ignore[arg-type]
        assert e.name == ""


# ExecutionLogs

class TestExecutionLogs:
    def test_from_dict(self):
        logs = ExecutionLogs.from_dict({"stdout": ["hello"], "stderr": ["oops"]})  # type: ignore[arg-type]
        assert logs.stdout == ["hello"]
        assert logs.stderr == ["oops"]

    def test_null_lists(self):
        logs = ExecutionLogs.from_dict({"stdout": None, "stderr": None})  # type: ignore[arg-type]
        assert logs.stdout == []
        assert logs.stderr == []

    def test_empty_dict(self):
        logs = ExecutionLogs.from_dict({})  # type: ignore[arg-type]
        assert logs.stdout == []


# CodeExecutionResult

class TestCodeExecutionResult:
    def test_main_text_primary(self):
        """main_text should return the primary item's text."""
        r = CodeExecutionResult.from_dict({
            "items": [
                {"text": "secondary", "is_primary": False},
                {"text": "primary", "is_primary": True},
            ],
            "logs": {},
            "error": None,
            "execution_count": 1,
        })  # type: ignore[arg-type]
        assert r.main_text == "primary"

    def test_main_text_fallback(self):
        """main_text should fall back to last item when no primary."""
        r = CodeExecutionResult.from_dict({
            "items": [
                {"text": "first"},
                {"text": "last"},
            ],
            "logs": {},
            "error": None,
            "execution_count": 1,
        })  # type: ignore[arg-type]
        assert r.main_text == "last"

    def test_main_text_empty(self):
        r = CodeExecutionResult.from_dict({
            "items": [],
            "logs": {},
            "error": None,
            "execution_count": 0,
        })  # type: ignore[arg-type]
        assert r.main_text is None

    def test_with_error(self):
        r = CodeExecutionResult.from_dict({
            "items": [],
            "logs": {"stdout": ["out"]},
            "error": {"name": "Err", "value": "msg", "traceback": "tb"},
            "execution_count": 1,
        })  # type: ignore[arg-type]
        assert r.error is not None
        assert r.error.name == "Err"
        assert r.logs.stdout == ["out"]

    def test_context_id_passthrough(self):
        r = CodeExecutionResult.from_dict(
            {"items": [], "logs": {}, "error": None, "execution_count": 0},
            context_id="ctx_1",
        )  # type: ignore[arg-type]
        assert r.context_id == "ctx_1"


# StreamEvent

class TestStreamEvent:
    def test_integer_type_stdout(self):
        e = StreamEvent.from_dict({"type": 0, "data": "hello"})  # type: ignore[arg-type]
        assert e.type == "stdout"

    def test_integer_type_stderr(self):
        e = StreamEvent.from_dict({"type": 1, "data": "err"})  # type: ignore[arg-type]
        assert e.type == "stderr"

    def test_integer_type_exit(self):
        e = StreamEvent.from_dict({"type": 2, "data": "", "code": 0})  # type: ignore[arg-type]
        assert e.type == "exit"
        assert e.code == 0

    def test_integer_type_error(self):
        e = StreamEvent.from_dict({"type": 3, "data": "bad"})  # type: ignore[arg-type]
        assert e.type == "error"

    def test_string_type(self):
        e = StreamEvent.from_dict({"type": "stdout", "data": "hi"})  # type: ignore[arg-type]
        assert e.type == "stdout"

    def test_unknown_integer_type(self):
        e = StreamEvent.from_dict({"type": 99, "data": ""})  # type: ignore[arg-type]
        assert e.type == "99"

    def test_empty_dict(self):
        e = StreamEvent.from_dict({})  # type: ignore[arg-type]
        assert e.type == ""
        assert e.data == ""
        assert e.code is None


# CodeContext

class TestCodeContext:
    def test_integer_language_python(self):
        c = CodeContext.from_dict({"id": "ctx_1", "language": 1, "cwd": "/home"})  # type: ignore[arg-type]
        assert c.id == "ctx_1"
        assert c.language == "python"

    def test_integer_language_typescript(self):
        c = CodeContext.from_dict({"id": "ctx_2", "language": 2})  # type: ignore[arg-type]
        assert c.language == "typescript"

    def test_string_language(self):
        c = CodeContext.from_dict({"id": "ctx_3", "language": "python"})  # type: ignore[arg-type]
        assert c.language == "python"

    def test_context_id_fallback(self):
        """Should fall back to context_id when id is missing."""
        c = CodeContext.from_dict({"context_id": "ctx_4"})  # type: ignore[arg-type]
        assert c.id == "ctx_4"

    def test_prefers_id_over_context_id(self):
        c = CodeContext.from_dict({"id": "ctx_a", "context_id": "ctx_b"})  # type: ignore[arg-type]
        assert c.id == "ctx_a"

    def test_empty_dict(self):
        c = CodeContext.from_dict({})  # type: ignore[arg-type]
        assert c.id == ""
        assert c.language == ""


# Desktop models

class TestDesktopHealth:
    def test_with_state(self):
        h = DesktopHealth.from_dict({"ok": True, "state": "ready"})  # type: ignore[arg-type]
        assert h.ok is True
        assert h.state == "ready"

    def test_missing_state(self):
        h = DesktopHealth.from_dict({"ok": False})  # type: ignore[arg-type]
        assert h.ok is False
        assert h.state == ""

    def test_empty_dict(self):
        h = DesktopHealth.from_dict({})  # type: ignore[arg-type]
        assert h.ok is False
        assert h.state == ""


class TestDesktopDisplayInfo:
    def test_from_dict(self):
        d = DesktopDisplayInfo.from_dict({"display": ":0", "width": 1920, "height": 1080})  # type: ignore[arg-type]
        assert d.display == ":0"
        assert d.width == 1920
        assert d.height == 1080


class TestDesktopWindow:
    def test_class_key(self):
        w = DesktopWindow.from_dict({"id": "w1", "class": "Firefox"})  # type: ignore[arg-type]
        assert w.window_class == "Firefox"

    def test_class_underscore_key(self):
        w = DesktopWindow.from_dict({"id": "w2", "class_": "Chrome"})  # type: ignore[arg-type]
        assert w.window_class == "Chrome"

    def test_prefers_class_over_class_(self):
        w = DesktopWindow.from_dict({"id": "w3", "class": "A", "class_": "B"})  # type: ignore[arg-type]
        assert w.window_class == "A"

    def test_empty_dict(self):
        w = DesktopWindow.from_dict({})  # type: ignore[arg-type]
        assert w.window_class == ""


class TestDesktopPointerPosition:
    def test_from_dict(self):
        p = DesktopPointerPosition.from_dict({"x": 100, "y": 200})  # type: ignore[arg-type]
        assert p.x == 100
        assert p.y == 200


class TestDesktopRecordingStatus:
    def test_from_dict(self):
        data = {
            "id": "rec_1",
            "active": True,
            "started_at": "2025-01-01",
            "download": "/api/recordings/rec_1/download",
            "mime_type": "video/mp4",
            "file_name": "recording.mp4",
            "display": ":0",
            "resolution": "1920x1080",
        }
        r = DesktopRecordingStatus.from_dict(data)  # type: ignore[arg-type]
        assert r.id == "rec_1"
        assert r.active is True


class TestDesktopRecordingSummary:
    def test_from_dict(self):
        data = {"id": "rec_1", "file_name": "a.mp4", "size_bytes": 1024}
        r = DesktopRecordingSummary.from_dict(data)  # type: ignore[arg-type]
        assert r.size_bytes == 1024


class TestDesktopProcessStatus:
    def test_from_dict(self):
        p = DesktopProcessStatus.from_dict({"name": "xvfb", "running": True, "pid": 123})  # type: ignore[arg-type]
        assert p.name == "xvfb"
        assert p.running is True
        assert p.pid == 123


class TestDesktopProcessStatusList:
    def test_from_dict(self):
        data = {
            "status": "running",
            "items": [{"name": "xvfb", "running": True, "pid": 1}],
            "running": 1,
            "total": 4,
        }
        status_list = DesktopProcessStatusList.from_dict(data)  # type: ignore[arg-type]
        assert status_list.status == "running"
        assert len(status_list.items) == 1
        assert status_list.running == 1
        assert status_list.total == 4

    def test_empty_dict(self):
        status_list = DesktopProcessStatusList.from_dict({})  # type: ignore[arg-type]
        assert status_list.items == []


class TestDesktopProcessRestart:
    def test_with_status(self):
        data = {"message": "restarted", "status": {"name": "xvfb", "running": True, "pid": 42}}
        r = DesktopProcessRestart.from_dict(data)  # type: ignore[arg-type]
        assert r.message == "restarted"
        assert r.status is not None
        assert r.status.pid == 42

    def test_without_status(self):
        r = DesktopProcessRestart.from_dict({"message": "ok"})  # type: ignore[arg-type]
        assert r.status is None


class TestDesktopProcessLogs:
    def test_from_dict(self):
        process_logs = DesktopProcessLogs.from_dict({"process": "xvfb", "logs": "output..."})  # type: ignore[arg-type]
        assert process_logs.process == "xvfb"
        assert process_logs.logs == "output..."


class TestDesktopProcessErrors:
    def test_from_dict(self):
        e = DesktopProcessErrors.from_dict({"process": "x11vnc", "errors": "fail"})  # type: ignore[arg-type]
        assert e.process == "x11vnc"
        assert e.errors == "fail"
