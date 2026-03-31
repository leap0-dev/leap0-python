from leap0 import FilesystemClient, GitClient, Leap0Client, LspClient, ProcessClient, PtyClient, SandboxesClient, SnapshotsClient, TemplatesClient


def test_client_import() -> None:
    client = Leap0Client(api_key="test")
    client.close()


def test_service_client_imports() -> None:
    assert FilesystemClient is not None
    assert GitClient is not None
    assert LspClient is not None
    assert ProcessClient is not None
    assert PtyClient is not None
    assert SandboxesClient is not None
    assert SnapshotsClient is not None
    assert TemplatesClient is not None
