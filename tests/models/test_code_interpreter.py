from __future__ import annotations

import base64

from leap0.models.code_interpreter import (
    CodeContext, CodeExecutionError, CodeExecutionOutput, CodeExecutionResult, ExecutionLogs, StreamEvent,
)


class TestCodeExecutionOutput:
    def test_full(self):
        o = CodeExecutionOutput.from_dict({"is_primary": True, "text": "hello",
                                           "png": base64.b64encode(b"PNG").decode(),
                                           "json": {"key": "val"}, "extra": {"custom": True}})
        assert o.is_primary is True
        assert o.is_main_result is True
        assert o.json_data == {"key": "val"}

    def test_png_bytes(self):
        o = CodeExecutionOutput(png=base64.b64encode(b"PNG_DATA").decode())
        assert o.png_bytes() == b"PNG_DATA"

    def test_png_bytes_none(self):
        assert CodeExecutionOutput().png_bytes() is None

    def test_jpeg_bytes(self):
        o = CodeExecutionOutput(jpeg=base64.b64encode(b"JPEG").decode())
        assert o.jpeg_bytes() == b"JPEG"

    def test_pdf_bytes(self):
        o = CodeExecutionOutput(pdf=base64.b64encode(b"PDF").decode())
        assert o.pdf_bytes() == b"PDF"

    def test_empty_dict(self):
        o = CodeExecutionOutput.from_dict({})
        assert o.is_primary is False
        assert o.text is None


class TestCodeExecutionError:
    def test_from_dict(self):
        e = CodeExecutionError.from_dict({"name": "ValueError", "value": "bad", "traceback": "line 1"})
        assert e.name == "ValueError"

    def test_empty_dict(self):
        assert CodeExecutionError.from_dict({}).name == ""


class TestExecutionLogs:
    def test_from_dict(self):
        logs = ExecutionLogs.from_dict({"stdout": ["hello"], "stderr": ["oops"]})
        assert logs.stdout == ["hello"]

    def test_null_lists(self):
        assert ExecutionLogs.from_dict({"stdout": None}).stdout == []

    def test_empty_dict(self):
        assert ExecutionLogs.from_dict({}).stdout == []


class TestCodeExecutionResult:
    def test_main_text_primary(self):
        r = CodeExecutionResult.from_dict({"items": [{"text": "secondary"}, {"text": "primary", "is_primary": True}],
                                           "logs": {}, "error": None, "execution_count": 1})
        assert r.main_text == "primary"

    def test_main_text_fallback(self):
        r = CodeExecutionResult.from_dict({"items": [{"text": "first"}, {"text": "last"}],
                                           "logs": {}, "error": None, "execution_count": 1})
        assert r.main_text == "last"

    def test_main_text_empty(self):
        assert CodeExecutionResult.from_dict({"items": [], "logs": {}, "error": None, "execution_count": 0}).main_text is None

    def test_with_error(self):
        r = CodeExecutionResult.from_dict({"items": [], "logs": {"stdout": ["out"]},
                                           "error": {"name": "Err", "value": "msg", "traceback": "tb"}, "execution_count": 1})
        assert r.error.name == "Err"
        assert r.logs.stdout == ["out"]

    def test_context_id_from_body(self):
        r = CodeExecutionResult.from_dict({"context_id": "ctx_1", "items": [], "logs": {}, "error": None, "execution_count": 0})
        assert r.context_id == "ctx_1"

    def test_context_id_missing(self):
        assert CodeExecutionResult.from_dict({"items": [], "logs": {}, "error": None, "execution_count": 0}).context_id is None


class TestStreamEvent:
    def test_integer_types(self):
        assert StreamEvent.from_dict({"type": 0, "data": "hello"}).type == "stdout"
        assert StreamEvent.from_dict({"type": 1, "data": "err"}).type == "stderr"
        assert StreamEvent.from_dict({"type": 2, "data": "", "code": 0}).type == "exit"
        assert StreamEvent.from_dict({"type": 3, "data": "bad"}).type == "error"

    def test_string_type(self):
        assert StreamEvent.from_dict({"type": "stdout", "data": "hi"}).type == "stdout"

    def test_unknown_integer(self):
        assert StreamEvent.from_dict({"type": 99, "data": ""}).type == "99"

    def test_empty_dict(self):
        e = StreamEvent.from_dict({})
        assert e.type == ""
        assert e.code is None


class TestCodeContext:
    def test_integer_languages(self):
        assert CodeContext.from_dict({"id": "ctx_1", "language": 1}).language == "python"
        assert CodeContext.from_dict({"id": "ctx_2", "language": 2}).language == "typescript"

    def test_string_language(self):
        assert CodeContext.from_dict({"id": "ctx_3", "language": "python"}).language == "python"

    def test_empty_dict(self):
        c = CodeContext.from_dict({})
        assert c.id == ""
        assert c.language == ""
