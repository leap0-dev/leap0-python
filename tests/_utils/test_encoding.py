from __future__ import annotations

from leap0._utils.encoding import b64decode_bytes, b64decode_text, b64encode_bytes, b64encode_text


class TestBase64:
    def test_bytes_roundtrip(self):
        data = b"hello world"
        assert b64decode_bytes(b64encode_bytes(data)) == data

    def test_text_roundtrip(self):
        assert b64decode_text(b64encode_text("hello world")) == "hello world"

    def test_text_utf8(self):
        text = "unicode: \u00e9\u00e8\u00ea"
        assert b64decode_text(b64encode_text(text, "utf-8"), "utf-8") == text
