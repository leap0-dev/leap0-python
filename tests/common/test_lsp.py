from __future__ import annotations

from leap0.common.lsp import LspResponse


class TestLspResponse:
    def test_from_dict(self):
        assert LspResponse.from_dict({"success": True}).success is True

    def test_empty_dict(self):
        assert LspResponse.from_dict({}).success is False
