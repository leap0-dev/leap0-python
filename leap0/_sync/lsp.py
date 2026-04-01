from __future__ import annotations

from typing import cast

from .._internal.types import JsonObject
from ._transport import Transport
from .._utils.errors import intercept_errors
from .._utils.url import file_uri as _file_uri
from ..models.lsp import LspJsonRpcResponse, LspResponse
from .._schemas.lsp import LspJsonRpcResponseDict, LspSuccessResponseDict
from ..models.sandbox import SandboxRef, sandbox_id_of


class LspClient:
    """Start and interact with language servers for code intelligence inside
        a sandbox.
    
        Supported languages: Python (pyright) and TypeScript/JavaScript
        (typescript-language-server).
    
        The typical flow is ``start`` -> ``did_open`` -> ``completions`` or
        ``document_symbols`` -> ``did_close`` -> ``stop``.
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    @intercept_errors("Failed to start LSP server: ")
    def start(self, sandbox: SandboxRef, *, language_id: str, path_to_project: str) -> LspResponse:
        """Start the LSP server for a language and project.

        Spawns the server process and sends the LSP ``initialize`` handshake
        automatically.

        Args:
            sandbox: Sandbox ID or object.
            language_id: Language identifier (``"python"``, ``"typescript"``, or ``"javascript"``).
            path_to_project: Project directory path inside the sandbox.

        Args:
            sandbox: Sandbox ID or object.
            language_id: Language identifier.
            path_to_project: Project directory path.
            uri: Document URI (e.g. ``"file:///home/user/project/main.py"``).
            text: Full document text.
            version: Document version number.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            LspResponse: Server startup result.
        """
        data = cast(LspSuccessResponseDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/lsp/start", json={"language_id": language_id, "path_to_project": path_to_project}))
        return LspResponse.from_dict(data)

    @intercept_errors("Failed to stop LSP server: ")
    def stop(self, sandbox: SandboxRef, *, language_id: str, path_to_project: str) -> LspResponse:
        """Send ``shutdown`` and ``exit`` to the language server and terminate it.
        
        Args:
            sandbox: Sandbox ID or object.
            language_id: Language identifier for the LSP operation.
            path_to_project: Project path inside the sandbox.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(LspSuccessResponseDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/lsp/stop", json={"language_id": language_id, "path_to_project": path_to_project}))
        return LspResponse.from_dict(data)

    @intercept_errors("Failed to open document: ")
    def did_open(
        self,
        sandbox: SandboxRef,
        *,
        language_id: str,
        path_to_project: str,
        uri: str,
        text: str | None = None,
        version: int = 1,
        http_timeout: float | None = None,
    ) -> None:
        """Notify the language server that a document was opened.
        
                Must be called before requesting completions or symbols.
        
        Args:
            sandbox: Sandbox ID or object.
            language_id: Language identifier for the LSP operation.
            path_to_project: Project path inside the sandbox.
            uri: Document URI.
            text: Parameter for this operation.
            version: Parameter for this operation.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        payload: JsonObject = {
            "language_id": language_id,
            "path_to_project": path_to_project,
            "uri": uri,
            "version": version,
        }
        if text is not None:
            payload["text"] = text
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/lsp/did-open",
            json=payload,
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to open document: ")
    def did_open_path(
        self,
        sandbox: SandboxRef,
        *,
        language_id: str,
        path_to_project: str,
        path: str,
        text: str | None = None,
        version: int = 1,
        http_timeout: float | None = None,
    ) -> None:
        """
            Like :meth:`did_open` but accepts a file path instead of a URI.

            Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self.did_open(sandbox, language_id=language_id, path_to_project=path_to_project, uri=_file_uri(path), text=text, version=version, http_timeout=http_timeout)

    @intercept_errors("Failed to close document: ")
    def did_close(
        self,
        sandbox: SandboxRef,
        *,
        language_id: str,
        path_to_project: str,
        uri: str,
        http_timeout: float | None = None,
    ) -> None:
        """Notify the language server that a document was closed.
        
        Args:
            sandbox: Sandbox ID or object.
            language_id: Language identifier for the LSP operation.
            path_to_project: Project path inside the sandbox.
            uri: Document URI.
        """
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/lsp/did-close",
            json={"language_id": language_id, "path_to_project": path_to_project, "uri": uri},
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to close document: ")
    def did_close_path(self, sandbox: SandboxRef, *, language_id: str, path_to_project: str, path: str, http_timeout: float | None = None) -> None:
        """
            Like :meth:`did_close` but accepts a file path instead of a URI.

            Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self.did_close(sandbox, language_id=language_id, path_to_project=path_to_project, uri=_file_uri(path), http_timeout=http_timeout)

    @intercept_errors("Failed to get completions: ")
    def completions(
        self,
        sandbox: SandboxRef,
        *,
        language_id: str,
        path_to_project: str,
        uri: str,
        line: int,
        character: int,
        http_timeout: float | None = None,
    ) -> LspJsonRpcResponse:
        """Request completions from the language server.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            LspJsonRpcResponse: Raw JSON-RPC response payload.
        """
        data = cast(LspJsonRpcResponseDict, self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/lsp/completions",
            json={
                "language_id": language_id,
                "path_to_project": path_to_project,
                "uri": uri,
                "position": {"line": line, "character": character},
            },
            timeout=http_timeout,
        ))
        return LspJsonRpcResponse.from_dict(data)

    @intercept_errors("Failed to get completions: ")
    def completions_path(
        self,
        sandbox: SandboxRef,
        *,
        language_id: str,
        path_to_project: str,
        path: str,
        line: int,
        character: int,
        http_timeout: float | None = None,
    ) -> LspJsonRpcResponse:
        """
                    Like :meth:`completions` but accepts a file path instead of a URI.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        return self.completions(sandbox, language_id=language_id, path_to_project=path_to_project, uri=_file_uri(path), line=line, character=character, http_timeout=http_timeout)

    @intercept_errors("Failed to get document symbols: ")
    def document_symbols(self, sandbox: SandboxRef, *, language_id: str, path_to_project: str, uri: str, http_timeout: float | None = None) -> LspJsonRpcResponse:
        """Request document symbols from the language server.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            LspJsonRpcResponse: Raw JSON-RPC response payload.
        """
        data = cast(LspJsonRpcResponseDict, self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/lsp/document-symbols",
            json={"language_id": language_id, "path_to_project": path_to_project, "uri": uri},
            timeout=http_timeout,
        ))
        return LspJsonRpcResponse.from_dict(data)

    @intercept_errors("Failed to get document symbols: ")
    def document_symbols_path(self, sandbox: SandboxRef, *, language_id: str, path_to_project: str, path: str, http_timeout: float | None = None) -> LspJsonRpcResponse:
        """
                    Like :meth:`document_symbols` but accepts a file path instead of a URI.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        return self.document_symbols(sandbox, language_id=language_id, path_to_project=path_to_project, uri=_file_uri(path), http_timeout=http_timeout)
