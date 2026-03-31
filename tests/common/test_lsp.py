from __future__ import annotations

from leap0.common.lsp import LspJsonRpcResponse, LspResponse


class TestLspResponse:
    def test_from_dict(self):
        assert LspResponse.from_dict({"success": True}).success is True

    def test_empty_dict(self):
        assert LspResponse.from_dict({}).success is False


class TestLspJsonRpcResponse:
    def test_result_response(self):
        response = LspJsonRpcResponse.from_dict({"jsonrpc": "2.0", "id": 1, "result": {"items": []}})
        assert response.jsonrpc == "2.0"
        assert response.id == 1
        assert response.result == {"items": []}
        assert response.error is None

    def test_error_response(self):
        response = LspJsonRpcResponse.from_dict({"jsonrpc": "2.0", "id": 2, "error": {"code": -32602, "message": "Invalid params"}})
        assert response.error is not None
        assert response.error.code == -32602
        assert response.error.message == "Invalid params"
