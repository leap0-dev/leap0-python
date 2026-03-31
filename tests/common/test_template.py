from __future__ import annotations

from leap0.common.template import ImageConfig, Template


class TestImageConfig:
    def test_full(self):
        c = ImageConfig.from_dict({"entrypoint": ["/bin/sh"], "cmd": ["-c", "echo hi"],
                                   "working_dir": "/workspace", "user": "appuser", "env": {"PATH": "/usr/bin"}})
        assert c.entrypoint == ["/bin/sh"]
        assert c.user == "appuser"

    def test_null_lists(self):
        c = ImageConfig.from_dict({"entrypoint": None, "cmd": None})
        assert c.entrypoint == []
        assert c.cmd == []


class TestTemplate:
    def test_full(self):
        t = Template.from_dict({"id": "tpl-1", "name": "my-template", "digest": "sha256:abc",
                                "image_config": {"entrypoint": ["/bin/sh"]}, "is_system": False, "created_at": "2025-01-01"})
        assert t.image_config.entrypoint == ["/bin/sh"]

    def test_null_image_config(self):
        t = Template.from_dict({"id": "tpl-2", "name": "t2", "digest": "", "image_config": None,
                                "is_system": True, "created_at": ""})
        assert t.image_config is None
        assert t.is_system is True
