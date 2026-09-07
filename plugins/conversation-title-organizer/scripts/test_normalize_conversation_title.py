#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).with_name("normalize_conversation_title.py")
SPEC = importlib.util.spec_from_file_location("conversation_title_organizer", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ConversationTitleOrganizerTests(unittest.TestCase):
    def config(self):
        return MODULE.load_config(Path("/nonexistent/user-config.json"))

    def paths(self, root: Path):
        return MODULE.StoragePaths(
            state_db=root / "state.sqlite",
            catalog_db=root / "catalog.sqlite",
            session_index=root / "session_index.jsonl",
            lock_file=root / "normalizer.lock",
            history_file=root / "history.jsonl",
            error_file=root / "errors.log",
            attempt_db=root / "attempts.sqlite",
        )

    def create_thread(
        self,
        paths,
        title="修复会话标题自动命名",
        message="帮我排查为什么没有自动改名",
    ):
        with sqlite3.connect(paths.state_db) as connection:
            connection.execute(
                "CREATE TABLE threads (id TEXT PRIMARY KEY, name TEXT, title TEXT NOT NULL, created_at INTEGER NOT NULL, archived INTEGER NOT NULL, thread_source TEXT, cwd TEXT NOT NULL, first_user_message TEXT)"
            )
            connection.execute(
                "INSERT INTO threads VALUES ('thread-1', ?, ?, 1788750938, 0, 'user', '/tmp/project', ?)",
                (title, title, message),
            )
        with sqlite3.connect(paths.catalog_db) as connection:
            connection.execute(
                "CREATE TABLE local_thread_catalog (host_id TEXT, thread_id TEXT, display_title TEXT, pending_observed_title INTEGER)"
            )
            connection.execute(
                "INSERT INTO local_thread_catalog VALUES ('local', 'thread-1', ?, 0)",
                (title,),
            )
        paths.session_index.write_text(
            json.dumps({"id": "thread-1", "thread_name": title}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def test_default_config_has_fixed_types(self):
        config = self.config()
        self.assertIn("排障", config["profiles"]["general"]["types"])
        self.assertNotIn("卸载", config["profiles"]["general"]["types"])

    def test_local_fast_path_uses_zero_tokens(self):
        config = self.config()
        policy = MODULE.match_policy("/tmp/project", config)
        result = MODULE.classify_locally(policy, "修复自动命名", "帮我排查标题错误", config)
        self.assertIsNotNone(result)
        self.assertEqual(result.title_type, "排障")
        self.assertEqual(result.input_tokens, 0)

    def test_ambiguous_request_is_left_for_ai(self):
        config = self.config()
        policy = MODULE.match_policy("/tmp/project", config)
        result = MODULE.classify_locally(policy, "聊聊这个想法", "你怎么看", config)
        self.assertIsNone(result)

    def test_ai_fallback_is_optional(self):
        config = self.config()
        policy = MODULE.match_policy("/tmp/project", config)
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(MODULE.classify_with_ai(policy, "聊聊", "你怎么看", config))

    def test_ai_fallback_redacts_payload_and_records_usage(self):
        config = self.config()
        policy = MODULE.match_policy("/tmp/project", config)
        captured = {}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps(
                    {
                        "output_text": '{"type":"评估","theme":"方案可行性"}',
                        "usage": {
                            "input_tokens": 100,
                            "output_tokens": 20,
                            "input_tokens_details": {"cached_tokens": 64},
                            "output_tokens_details": {"reasoning_tokens": 8},
                        },
                    }
                ).encode("utf-8")

        def fake_urlopen(request, timeout):
            captured["body"] = request.data.decode("utf-8")
            captured["timeout"] = timeout
            return FakeResponse()

        with mock.patch.dict(os.environ, {"CONVERSATION_TITLE_API_KEY": "test-only"}, clear=True):
            with mock.patch.object(MODULE.urllib.request, "urlopen", fake_urlopen):
                result = MODULE.classify_with_ai(
                    policy,
                    "评估 person@example.com 的方案",
                    "查看 https://example.com/private 是否可行",
                    config,
                )

        self.assertEqual(result.title_type, "评估")
        self.assertEqual(result.cached_input_tokens, 64)
        self.assertEqual(result.reasoning_tokens, 8)
        self.assertNotIn("person@example.com", captured["body"])
        self.assertNotIn("https://example.com/private", captured["body"])
        self.assertNotIn("test-only", captured["body"])

    def test_redaction_removes_private_values(self):
        text = MODULE._redact(
            "person@example.com 13800138000 /home/alex/private C:\\Users\\alex\\private https://example.com/a",
            300,
        )
        self.assertNotIn("person@example.com", text)
        self.assertNotIn("13800138000", text)
        self.assertNotIn("/home/alex", text)
        self.assertNotIn("C:\\Users\\alex", text)
        self.assertNotIn("https://", text)

    def test_local_theme_rejects_redacted_paths(self):
        self.assertIsNone(MODULE._usable_local_theme("处理 /home/alex/private", 24))

    def test_generic_openai_key_is_not_borrowed(self):
        config = self.config()
        policy = MODULE.match_policy("/tmp/project", config)
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "must-not-be-used"}, clear=True):
            self.assertIsNone(MODULE.classify_with_ai(policy, "聊聊", "你怎么看", config))

    def test_user_config_rejects_secret_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text('{"api_key":"must-not-live-here"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.load_config(path)

    def test_discovers_compatible_state_database(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = self.paths(root)
            self.create_thread(paths)
            self.assertEqual(MODULE.discover_state_db(root), paths.state_db)

    def test_integration_updates_all_available_indexes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = self.paths(root)
            self.create_thread(paths)
            status, new_title = MODULE.rename_thread(
                "thread-1",
                "/tmp/project",
                paths,
                self.config(),
            )
            self.assertEqual(status, "renamed")
            self.assertEqual(new_title, "0907｜排障｜修复会话标题自动命名")
            with sqlite3.connect(paths.state_db) as connection:
                self.assertEqual(connection.execute("SELECT name FROM threads").fetchone()[0], new_title)
            with sqlite3.connect(paths.catalog_db) as connection:
                self.assertEqual(
                    connection.execute("SELECT display_title FROM local_thread_catalog").fetchone()[0],
                    new_title,
                )
            self.assertEqual(
                json.loads(paths.session_index.read_text(encoding="utf-8"))["thread_name"],
                new_title,
            )
            history = json.loads(paths.history_file.read_text(encoding="utf-8"))
            self.assertEqual(history["classifier_mode"], "local")
            self.assertEqual(history["input_tokens"], 0)
            self.assertNotIn("new_title", history)

    def test_attempt_is_claimed_once(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.paths(Path(directory))
            self.assertTrue(MODULE._claim_attempt(paths, "thread-1"))
            self.assertFalse(MODULE._claim_attempt(paths, "thread-1"))


if __name__ == "__main__":
    unittest.main()
