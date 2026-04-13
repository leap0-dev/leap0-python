from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._async.client import AsyncLeap0, AsyncLeap0Client, AsyncPtyConnection
    from ._async.code_interpreter import AsyncCodeInterpreterClient
    from ._async.desktop import AsyncDesktopClient
    from ._async.filesystem import AsyncFilesystemClient
    from ._async.git import AsyncGitClient
    from ._async.lsp import AsyncLspClient
    from ._async.process import AsyncProcessClient
    from ._async.pty import AsyncPtyClient
    from ._async.sandbox import AsyncSandbox, AsyncSandboxesClient
    from ._async.snapshots import AsyncSnapshotsClient
    from ._async.ssh import AsyncSshClient
    from ._async.templates import AsyncTemplatesClient
    from ._sync.client import Leap0, Leap0Client
    from ._sync.code_interpreter import CodeInterpreterClient
    from .models.code_interpreter import (
        CodeLanguage,
        CodeContext,
        CodeExecutionError,
        CodeExecutionOutput,
        CodeExecutionResult,
        ExecutionLogs,
        StreamEvent,
        StreamEventType,
    )
    from .models.config import (
        DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME,
        DEFAULT_DESKTOP_TEMPLATE_NAME,
        DEFAULT_TEMPLATE_NAME,
        Leap0Config,
    )
    from .models.errors import (
        Leap0ConflictError,
        Leap0Error,
        Leap0NotFoundError,
        Leap0PermissionError,
        Leap0RateLimitError,
        Leap0TimeoutError,
        Leap0WebSocketError,
    )
    from .models.desktop import (
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
    )
    from .models.filesystem import (
        EditFileResult,
        EditResult,
        FileEdit,
        FileInfo,
        LsResult,
        SearchMatch,
        TreeEntry,
        TreeResult,
    )
    from .models.git import GitCommitResult, GitResult
    from .models.lsp import (
        LspJsonRpcError,
        LspJsonRpcResponse,
        LspResponse,
    )
    from .models.process import ProcessResult
    from .models.pty import CreatePtySessionParams, PtyConnection, PtySession
    from .models.sandbox import (
        CreateSandboxParams,
        NetworkPolicyMode,
        SandboxListItem,
        SandboxListResponse,
        SandboxState,
        SandboxStatus,
        sandbox_id_of,
    )
    from .models.snapshot import CreateSnapshotParams, ResumeSnapshotParams, Snapshot, SnapshotListResponse, snapshot_id_of
    from .models.ssh import SshAccess, SshValidation
    from .models.template import (
        AwsRegistryCredentials,
        AwsRegistryCredentialsDict,
        AzureRegistryCredentials,
        AzureRegistryCredentialsDict,
        BasicRegistryCredentials,
        BasicRegistryCredentialsDict,
        CreateTemplateParams,
        GcpRegistryCredentials,
        GcpRegistryCredentialsDict,
        ImageConfig,
        RegistryCredentialType,
        RegistryCredentials,
        RegistryCredentialsDict,
        RegistryCredentialsInput,
        RenameTemplateParams,
        Template,
    )
    from ._sync.desktop import DesktopClient
    from ._sync.filesystem import FilesystemClient
    from ._sync.git import GitClient
    from ._sync.lsp import LspClient
    from ._sync.process import ProcessClient
    from ._sync.pty import PtyClient
    from ._sync.sandbox import Sandbox, SandboxesClient
    from ._sync.snapshots import SnapshotsClient
    from ._sync.ssh import SshClient
    from ._sync.templates import TemplatesClient


__all__ = [
    "AsyncLeap0",
    "AsyncLeap0Client",
    "AsyncCodeInterpreterClient",
    "AsyncDesktopClient",
    "AsyncFilesystemClient",
    "AsyncGitClient",
    "AsyncLspClient",
    "AsyncProcessClient",
    "AsyncPtyClient",
    "AsyncPtyConnection",
    "AsyncSandbox",
    "AsyncSandboxesClient",
    "AsyncSnapshotsClient",
    "AsyncSshClient",
    "AsyncTemplatesClient",
    "AwsRegistryCredentials",
    "AwsRegistryCredentialsDict",
    "AzureRegistryCredentials",
    "AzureRegistryCredentialsDict",
    "BasicRegistryCredentials",
    "BasicRegistryCredentialsDict",
    "CodeLanguage",
    "CodeContext",
    "CodeExecutionError",
    "CodeExecutionOutput",
    "CodeExecutionResult",
    "CodeInterpreterClient",
    "CreatePtySessionParams",
    "CreateSandboxParams",
    "CreateSnapshotParams",
    "CreateTemplateParams",
    "DesktopClient",
    "DesktopDisplayInfo",
    "DesktopHealth",
    "DesktopPointerPosition",
    "DesktopProcessErrors",
    "DesktopProcessLogs",
    "DesktopProcessRestart",
    "DesktopProcessStatus",
    "DesktopProcessStatusList",
    "DesktopRecordingStatus",
    "DesktopRecordingSummary",
    "DesktopWindow",
    "EditFileResult",
    "EditResult",
    "ExecutionLogs",
    "FileEdit",
    "FileInfo",
    "FilesystemClient",
    "GcpRegistryCredentials",
    "GitClient",
    "GitCommitResult",
    "GitResult",
    "ImageConfig",
    "Leap0",
    "Leap0Client",
    "Leap0Config",
    "Leap0ConflictError",
    "Leap0Error",
    "Leap0NotFoundError",
    "Leap0PermissionError",
    "Leap0RateLimitError",
    "Leap0TimeoutError",
    "Leap0WebSocketError",
    "DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME",
    "DEFAULT_DESKTOP_TEMPLATE_NAME",
    "DEFAULT_TEMPLATE_NAME",
    "LsResult",
    "LspClient",
    "LspJsonRpcError",
    "LspJsonRpcResponse",
    "LspResponse",
    "NetworkPolicyMode",
    "ProcessClient",
    "ProcessResult",
    "PtyClient",
    "PtyConnection",
    "PtySession",
    "RenameTemplateParams",
    "RegistryCredentialType",
    "RegistryCredentials",
    "RegistryCredentialsDict",
    "RegistryCredentialsInput",
    "ResumeSnapshotParams",
    "Sandbox",
    "SandboxListItem",
    "SandboxListResponse",
    "SandboxState",
    "SandboxStatus",
    "SandboxesClient",
    "SearchMatch",
    "Snapshot",
    "SnapshotListResponse",
    "snapshot_id_of",
    "SnapshotsClient",
    "SshAccess",
    "SshClient",
    "SshValidation",
    "StreamEvent",
    "StreamEventType",
    "sandbox_id_of",
    "Template",
    "TemplatesClient",
    "TreeEntry",
    "TreeResult",
]


_DYNAMIC_IMPORTS: dict[str, tuple[str, str]] = {
    "AsyncLeap0": ("._async.client", "AsyncLeap0"),
    "AsyncLeap0Client": ("._async.client", "AsyncLeap0Client"),
    "AsyncCodeInterpreterClient": ("._async.code_interpreter", "AsyncCodeInterpreterClient"),
    "AsyncDesktopClient": ("._async.desktop", "AsyncDesktopClient"),
    "AsyncFilesystemClient": ("._async.filesystem", "AsyncFilesystemClient"),
    "AsyncGitClient": ("._async.git", "AsyncGitClient"),
    "AsyncLspClient": ("._async.lsp", "AsyncLspClient"),
    "AsyncProcessClient": ("._async.process", "AsyncProcessClient"),
    "AsyncPtyClient": ("._async.pty", "AsyncPtyClient"),
    "AsyncPtyConnection": ("._async.client", "AsyncPtyConnection"),
    "AsyncSandbox": ("._async.sandbox", "AsyncSandbox"),
    "AsyncSandboxesClient": ("._async.sandbox", "AsyncSandboxesClient"),
    "AsyncSnapshotsClient": ("._async.snapshots", "AsyncSnapshotsClient"),
    "AsyncSshClient": ("._async.ssh", "AsyncSshClient"),
    "AsyncTemplatesClient": ("._async.templates", "AsyncTemplatesClient"),
    "Leap0": ("._sync.client", "Leap0"),
    "Leap0Client": ("._sync.client", "Leap0Client"),
    "CodeInterpreterClient": ("._sync.code_interpreter", "CodeInterpreterClient"),
    "DesktopClient": ("._sync.desktop", "DesktopClient"),
    "FilesystemClient": ("._sync.filesystem", "FilesystemClient"),
    "GitClient": ("._sync.git", "GitClient"),
    "LspClient": ("._sync.lsp", "LspClient"),
    "ProcessClient": ("._sync.process", "ProcessClient"),
    "PtyClient": ("._sync.pty", "PtyClient"),
    "Sandbox": ("._sync.sandbox", "Sandbox"),
    "SandboxesClient": ("._sync.sandbox", "SandboxesClient"),
    "SnapshotsClient": ("._sync.snapshots", "SnapshotsClient"),
    "SshClient": ("._sync.ssh", "SshClient"),
    "TemplatesClient": ("._sync.templates", "TemplatesClient"),
    "Leap0Config": (".models.config", "Leap0Config"),
    "DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME": (".models.config", "DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME"),
    "DEFAULT_DESKTOP_TEMPLATE_NAME": (".models.config", "DEFAULT_DESKTOP_TEMPLATE_NAME"),
    "DEFAULT_TEMPLATE_NAME": (".models.config", "DEFAULT_TEMPLATE_NAME"),
    "Leap0ConflictError": (".models.errors", "Leap0ConflictError"),
    "Leap0Error": (".models.errors", "Leap0Error"),
    "Leap0NotFoundError": (".models.errors", "Leap0NotFoundError"),
    "Leap0PermissionError": (".models.errors", "Leap0PermissionError"),
    "Leap0RateLimitError": (".models.errors", "Leap0RateLimitError"),
    "Leap0TimeoutError": (".models.errors", "Leap0TimeoutError"),
    "Leap0WebSocketError": (".models.errors", "Leap0WebSocketError"),
    "CreateSandboxParams": (".models.sandbox", "CreateSandboxParams"),
    "NetworkPolicyMode": (".models.sandbox", "NetworkPolicyMode"),
    "SandboxListItem": (".models.sandbox", "SandboxListItem"),
    "SandboxListResponse": (".models.sandbox", "SandboxListResponse"),
    "SandboxStatus": (".models.sandbox", "SandboxStatus"),
    "SandboxState": (".models.sandbox", "SandboxState"),
    "sandbox_id_of": (".models.sandbox", "sandbox_id_of"),
    "CreateSnapshotParams": (".models.snapshot", "CreateSnapshotParams"),
    "ResumeSnapshotParams": (".models.snapshot", "ResumeSnapshotParams"),
    "Snapshot": (".models.snapshot", "Snapshot"),
    "SnapshotListResponse": (".models.snapshot", "SnapshotListResponse"),
    "snapshot_id_of": (".models.snapshot", "snapshot_id_of"),
    "EditFileResult": (".models.filesystem", "EditFileResult"),
    "EditResult": (".models.filesystem", "EditResult"),
    "FileEdit": (".models.filesystem", "FileEdit"),
    "FileInfo": (".models.filesystem", "FileInfo"),
    "LsResult": (".models.filesystem", "LsResult"),
    "SearchMatch": (".models.filesystem", "SearchMatch"),
    "TreeEntry": (".models.filesystem", "TreeEntry"),
    "TreeResult": (".models.filesystem", "TreeResult"),
    "GitCommitResult": (".models.git", "GitCommitResult"),
    "GitResult": (".models.git", "GitResult"),
    "ProcessResult": (".models.process", "ProcessResult"),
    "CreatePtySessionParams": (".models.pty", "CreatePtySessionParams"),
    "PtyConnection": (".models.pty", "PtyConnection"),
    "PtySession": (".models.pty", "PtySession"),
    "LspJsonRpcError": (".models.lsp", "LspJsonRpcError"),
    "LspJsonRpcResponse": (".models.lsp", "LspJsonRpcResponse"),
    "LspResponse": (".models.lsp", "LspResponse"),
    "SshAccess": (".models.ssh", "SshAccess"),
    "SshValidation": (".models.ssh", "SshValidation"),
    "CreateTemplateParams": (".models.template", "CreateTemplateParams"),
    "BasicRegistryCredentials": (".models.template", "BasicRegistryCredentials"),
    "BasicRegistryCredentialsDict": (".models.template", "BasicRegistryCredentialsDict"),
    "AwsRegistryCredentials": (".models.template", "AwsRegistryCredentials"),
    "AwsRegistryCredentialsDict": (".models.template", "AwsRegistryCredentialsDict"),
    "GcpRegistryCredentials": (".models.template", "GcpRegistryCredentials"),
    "GcpRegistryCredentialsDict": (".models.template", "GcpRegistryCredentialsDict"),
    "AzureRegistryCredentials": (".models.template", "AzureRegistryCredentials"),
    "AzureRegistryCredentialsDict": (".models.template", "AzureRegistryCredentialsDict"),
    "ImageConfig": (".models.template", "ImageConfig"),
    "RegistryCredentialType": (".models.template", "RegistryCredentialType"),
    "RegistryCredentials": (".models.template", "RegistryCredentials"),
    "RegistryCredentialsDict": (".models.template", "RegistryCredentialsDict"),
    "RegistryCredentialsInput": (".models.template", "RegistryCredentialsInput"),
    "Template": (".models.template", "Template"),
    "RenameTemplateParams": (".models.template", "RenameTemplateParams"),
    "CodeLanguage": (".models.code_interpreter", "CodeLanguage"),
    "CodeContext": (".models.code_interpreter", "CodeContext"),
    "CodeExecutionError": (".models.code_interpreter", "CodeExecutionError"),
    "CodeExecutionOutput": (".models.code_interpreter", "CodeExecutionOutput"),
    "CodeExecutionResult": (".models.code_interpreter", "CodeExecutionResult"),
    "ExecutionLogs": (".models.code_interpreter", "ExecutionLogs"),
    "StreamEvent": (".models.code_interpreter", "StreamEvent"),
    "StreamEventType": (".models.code_interpreter", "StreamEventType"),
    "DesktopDisplayInfo": (".models.desktop", "DesktopDisplayInfo"),
    "DesktopHealth": (".models.desktop", "DesktopHealth"),
    "DesktopPointerPosition": (".models.desktop", "DesktopPointerPosition"),
    "DesktopProcessErrors": (".models.desktop", "DesktopProcessErrors"),
    "DesktopProcessLogs": (".models.desktop", "DesktopProcessLogs"),
    "DesktopProcessRestart": (".models.desktop", "DesktopProcessRestart"),
    "DesktopProcessStatus": (".models.desktop", "DesktopProcessStatus"),
    "DesktopProcessStatusList": (".models.desktop", "DesktopProcessStatusList"),
    "DesktopRecordingStatus": (".models.desktop", "DesktopRecordingStatus"),
    "DesktopRecordingSummary": (".models.desktop", "DesktopRecordingSummary"),
    "DesktopWindow": (".models.desktop", "DesktopWindow"),
}


def __getattr__(name: str) -> object:
    target = _DYNAMIC_IMPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = target
    module = importlib.import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
