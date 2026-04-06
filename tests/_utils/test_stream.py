from __future__ import annotations

from leap0._utils.stream import iter_ndjson, iter_sse_events


class TestIterSseEvents:
    def test_standard_events(self):
        assert list(iter_sse_events(["data: {\"a\": 1}", "", "data: {\"b\": 2}", ""])) == [{"a": 1}, {"b": 2}]

    def test_carriage_return(self):
        assert list(iter_sse_events(["data: {\"x\": 1}\r", "\r"])) == [{"x": 1}]

    def test_comments_skipped(self):
        assert list(iter_sse_events([": comment", "data: {\"a\": 1}", ""])) == [{"a": 1}]

    def test_flush_at_end(self):
        assert list(iter_sse_events(["data: {\"z\": 99}"])) == [{"z": 99}]

    def test_empty(self):
        assert list(iter_sse_events([])) == []

    def test_only_comments(self):
        assert list(iter_sse_events([": c1", ": c2"])) == []

    def test_only_blanks(self):
        assert list(iter_sse_events(["", "", ""])) == []

    def test_multiline_data(self):
        assert list(iter_sse_events(['data: {"a":', 'data: 1}', ''])) == [{"a": 1}]

    def test_leading_space_stripped(self):
        assert list(iter_sse_events(["data:  {\"s\": 1}", ""])) == [{"s": 1}]

    def test_non_data_fields_ignored(self):
        assert list(iter_sse_events(["event: update", "id: 42", "data: {\"ok\": true}", ""])) == [{"ok": True}]

    def test_error_json_data_parsed(self):
        assert list(iter_sse_events(["event: error", 'data: {"error":"boom"}', ""])) == [{"error": "boom"}]


class TestIterNdjson:
    def test_standard(self):
        assert list(iter_ndjson(['{"a": 1}', '{"b": 2}'])) == [{"a": 1}, {"b": 2}]

    def test_blank_lines_skipped(self):
        assert list(iter_ndjson(['{"a": 1}', '', '{"b": 2}'])) == [{"a": 1}, {"b": 2}]

    def test_empty(self):
        assert list(iter_ndjson([])) == []
