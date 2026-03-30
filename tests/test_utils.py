"""Tests for _utils: SSE, NDJSON, URL helpers, base64, file_uri."""
from __future__ import annotations

import pytest

from leap0._utils import (
    b64decode_bytes,
    b64decode_text,
    b64encode_bytes,
    b64encode_text,
    ensure_leading_slash,
    file_uri,
    iter_ndjson,
    iter_sse_events,
    sandbox_base_url,
    websocket_url_from_http,
)


# SSE parser

class TestIterSseEvents:
    def test_standard_events(self):
        lines = ["data: {\"a\": 1}", "", "data: {\"b\": 2}", ""]
        events = list(iter_sse_events(lines))
        assert events == [{"a": 1}, {"b": 2}]

    def test_carriage_return_handling(self):
        lines = ["data: {\"x\": 1}\r", "\r", "data: {\"y\": 2}\r", "\r"]
        events = list(iter_sse_events(lines))
        assert events == [{"x": 1}, {"y": 2}]

    def test_comment_lines_skipped(self):
        lines = [": this is a comment", "data: {\"a\": 1}", "", ":another comment", "data: {\"b\": 2}", ""]
        events = list(iter_sse_events(lines))
        assert events == [{"a": 1}, {"b": 2}]

    def test_flush_on_end_without_trailing_blank(self):
        """Buffer should flush at end of stream if no trailing empty line."""
        lines = ["data: {\"z\": 99}"]
        events = list(iter_sse_events(lines))
        assert events == [{"z": 99}]

    def test_empty_stream(self):
        events = list(iter_sse_events([]))
        assert events == []

    def test_only_comments(self):
        events = list(iter_sse_events([": comment1", ": comment2"]))
        assert events == []

    def test_only_blank_lines(self):
        events = list(iter_sse_events(["", "", ""]))
        assert events == []

    def test_multiline_data(self):
        """Multiple data: lines should be joined with newlines before parsing."""
        lines = ['data: {"a":', 'data: 1}', '']
        events = list(iter_sse_events(lines))
        assert events == [{"a": 1}]

    def test_data_with_leading_space_stripped(self):
        """Per SSE spec, strip at most one leading space after 'data:'."""
        lines = ["data:  {\"s\": 1}", ""]
        events = list(iter_sse_events(lines))
        # "data:" + " {\"s\": 1}" -- first space stripped, remainder is " {\"s\": 1}"
        # json.loads(" {\"s\": 1}") is valid
        assert events == [{"s": 1}]

    def test_non_data_fields_ignored(self):
        """event:, id:, retry: fields should be buffered but not treated as data."""
        lines = ["event: update", "id: 42", "retry: 3000", "data: {\"ok\": true}", ""]
        events = list(iter_sse_events(lines))
        assert events == [{"ok": True}]


# NDJSON parser

class TestIterNdjson:
    def test_standard(self):
        lines = ['{"a": 1}', '{"b": 2}']
        events = list(iter_ndjson(lines))
        assert events == [{"a": 1}, {"b": 2}]

    def test_blank_lines_skipped(self):
        lines = ['{"a": 1}', '', '  ', '{"b": 2}']
        events = list(iter_ndjson(lines))
        assert events == [{"a": 1}, {"b": 2}]

    def test_whitespace_stripped(self):
        lines = ['  {"c": 3}  ']
        events = list(iter_ndjson(lines))
        assert events == [{"c": 3}]

    def test_empty_input(self):
        assert list(iter_ndjson([])) == []


# URL utilities

class TestSandboxBaseUrl:
    def test_basic(self):
        url = sandbox_base_url("sbx-123", "sandbox.leap0.dev")
        assert url == "https://sbx-123.sandbox.leap0.dev"

    def test_with_port(self):
        url = sandbox_base_url("sbx-123", "sandbox.leap0.dev", port=8080)
        assert url == "https://sbx-123-8080.sandbox.leap0.dev"

    def test_strips_trailing_slash(self):
        url = sandbox_base_url("sbx-123", "sandbox.leap0.dev/")
        assert url == "https://sbx-123.sandbox.leap0.dev"

    def test_raises_on_missing_domain(self):
        with pytest.raises(ValueError, match="sandbox_domain is required"):
            sandbox_base_url("sbx-123", None)

    def test_raises_on_empty_domain(self):
        with pytest.raises(ValueError, match="sandbox_domain is required"):
            sandbox_base_url("sbx-123", "")


class TestWebsocketUrlFromHttp:
    def test_https_to_wss(self):
        assert websocket_url_from_http("https://example.com/ws") == "wss://example.com/ws"

    def test_http_to_ws(self):
        assert websocket_url_from_http("http://localhost:8080/ws") == "ws://localhost:8080/ws"

    def test_other_scheme_unchanged(self):
        assert websocket_url_from_http("wss://already.ws") == "wss://already.ws"

    def test_no_scheme(self):
        assert websocket_url_from_http("example.com/ws") == "example.com/ws"


class TestEnsureLeadingSlash:
    def test_already_has_slash(self):
        assert ensure_leading_slash("/path") == "/path"

    def test_missing_slash(self):
        assert ensure_leading_slash("path") == "/path"

    def test_empty_string(self):
        assert ensure_leading_slash("") == "/"


class TestFileUri:
    def test_absolute_path(self):
        assert file_uri("/home/user/file.py") == "file:///home/user/file.py"

    def test_relative_path(self):
        assert file_uri("home/user/file.py") == "file:///home/user/file.py"


# Base64 utilities

class TestBase64:
    def test_bytes_roundtrip(self):
        data = b"hello world"
        encoded = b64encode_bytes(data)
        assert isinstance(encoded, str)
        assert b64decode_bytes(encoded) == data

    def test_text_roundtrip(self):
        text = "hello world"
        encoded = b64encode_text(text)
        assert isinstance(encoded, str)
        assert b64decode_text(encoded) == text

    def test_text_utf8(self):
        text = "unicode: \u00e9\u00e8\u00ea"
        encoded = b64encode_text(text, "utf-8")
        assert b64decode_text(encoded, "utf-8") == text
