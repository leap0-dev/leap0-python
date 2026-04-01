from leap0 import (
    AsyncLeap0,
    AsyncLeap0Client,
    AsyncCodeInterpreterClient,
    AsyncDesktopClient,
    AsyncFilesystemClient,
    AsyncGitClient,
    AsyncLspClient,
    AsyncProcessClient,
    AsyncPtyClient,
    AsyncPtyConnection,
    AsyncSandbox,
    AsyncSandboxesClient,
    AsyncSnapshotsClient,
    AsyncSshClient,
    AsyncTemplatesClient,
    CreatePtySessionParams,
    CreateSandboxParams,
    CreateSnapshotParams,
    CreateTemplateParams,
    DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME,
    DEFAULT_TEMPLATE_NAME,
    FilesystemClient,
    GitClient,
    Leap0Client,
    LspClient,
    ProcessClient,
    PtyClient,
    RenameTemplateParams,
    ResumeSnapshotParams,
    Sandbox,
    SandboxesClient,
    SnapshotsClient,
    TemplatesClient,
)


def test_client_import() -> None:
    client = Leap0Client(api_key="test")
    client.close()


def test_service_client_imports() -> None:
    assert FilesystemClient is not None
    assert GitClient is not None
    assert LspClient is not None
    assert ProcessClient is not None
    assert PtyClient is not None
    assert Sandbox is not None
    assert SandboxesClient is not None
    assert SnapshotsClient is not None
    assert TemplatesClient is not None
    assert AsyncLeap0 is not None
    assert AsyncLeap0Client is not None
    assert AsyncCodeInterpreterClient is not None
    assert AsyncDesktopClient is not None
    assert AsyncFilesystemClient is not None
    assert AsyncGitClient is not None
    assert AsyncLspClient is not None
    assert AsyncProcessClient is not None
    assert AsyncPtyClient is not None
    assert AsyncSandbox is not None
    assert AsyncSandboxesClient is not None
    assert AsyncSnapshotsClient is not None
    assert AsyncSshClient is not None
    assert AsyncTemplatesClient is not None
    assert AsyncPtyConnection is not None
    assert CreateSandboxParams is not None
    assert CreateSnapshotParams is not None
    assert ResumeSnapshotParams is not None
    assert CreateTemplateParams is not None
    assert RenameTemplateParams is not None
    assert CreatePtySessionParams is not None
    assert DEFAULT_TEMPLATE_NAME == "system/debian:bookworm"
    assert DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME == "system/code-interpreter:v0.1.0"


def test_package_layout_imports() -> None:
    from leap0._async import AsyncLeap0Client as PackageAsyncLeap0Client
    from leap0._sync import Leap0Client as PackageLeap0Client

    assert PackageLeap0Client is Leap0Client
    assert PackageAsyncLeap0Client is AsyncLeap0Client
