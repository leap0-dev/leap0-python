from __future__ import annotations

import pytest

from leap0._utils.url import ensure_leading_slash, file_uri, sandbox_base_url, websocket_url_from_http


class TestSandboxBaseUrl:
    def test_basic(self):
        assert sandbox_base_url("sbx-123", "sandbox.leap0.dev") == "https://sbx-123.sandbox.leap0.dev"

    def test_with_port(self):
        assert sandbox_base_url("sbx-123", "sandbox.leap0.dev", port=8080) == "https://sbx-123-8080.sandbox.leap0.dev"

    def test_strips_trailing_slash(self):
        assert sandbox_base_url("sbx-123", "sandbox.leap0.dev/") == "https://sbx-123.sandbox.leap0.dev"

    def test_raises_on_missing_domain(self):
        with pytest.raises(ValueError):
            sandbox_base_url("sbx-123", None)

    def test_raises_on_empty_domain(self):
        with pytest.raises(ValueError):
            sandbox_base_url("sbx-123", "")


class TestWebsocketUrlFromHttp:
    def test_https_to_wss(self):
        assert websocket_url_from_http("https://example.com/ws") == "wss://example.com/ws"

    def test_http_to_ws(self):
        assert websocket_url_from_http("http://localhost:8080/ws") == "ws://localhost:8080/ws"

    def test_other_scheme(self):
        assert websocket_url_from_http("wss://already.ws") == "wss://already.ws"


class TestEnsureLeadingSlash:
    def test_already_has(self):
        assert ensure_leading_slash("/path") == "/path"

    def test_missing(self):
        assert ensure_leading_slash("path") == "/path"

    def test_empty(self):
        assert ensure_leading_slash("") == "/"


class TestFileUri:
    def test_absolute(self):
        assert file_uri("/home/user/file.py") == "file:///home/user/file.py"

    def test_relative(self):
        assert file_uri("home/user/file.py") == "file:///home/user/file.py"
