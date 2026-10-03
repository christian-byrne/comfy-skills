#!/usr/bin/env python3
"""Behavioral tests for validate-message.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate-message.py")
SPEC = importlib.util.spec_from_file_location("validate_message", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


VALID = """[agent-collab/v0] OFFER
from: dev-a/frontend
work: primevue-overlay

I can own Dialog wrappers if you take Select and Popover.
Need: accept or counter-propose
"""


class ValidateMessageTest(unittest.TestCase):
    def test_valid_message(self) -> None:
        self.assertEqual(MODULE.validate(VALID), [])

    def test_all_message_types(self) -> None:
        for kind in MODULE.TYPES - {"OWE", "RECONCILE"}:
            with self.subTest(kind=kind):
                self.assertEqual(MODULE.validate(VALID.replace("OFFER", kind, 1)), [])

    def test_obligation_messages_require_stable_id(self) -> None:
        for kind in ("OWE", "RECONCILE"):
            with self.subTest(kind=kind):
                message = VALID.replace("OFFER", kind, 1)
                self.assertTrue(any("Obligation" in error for error in MODULE.validate(message)))
                self.assertEqual(MODULE.validate(message + "Obligation: OBL-014\n"), [])

    def test_to_is_optional_metadata(self) -> None:
        with_to = VALID.replace("work:", "to: dev-b/frontend\nwork:")
        self.assertEqual(MODULE.validate(with_to), [])

    def test_compact_envelope(self) -> None:
        message = """[agent-collab/v0] UPDATE · dev-a/frontend · primevue-overlay

No action needed: the review build is available.
"""
        self.assertEqual(MODULE.validate(message), [])

    def test_missing_required_field(self) -> None:
        errors = MODULE.validate(VALID.replace("from: dev-a/frontend\n", ""))
        self.assertIn("missing required field: from", errors)

    def test_unknown_version(self) -> None:
        errors = MODULE.validate(VALID.replace("agent-collab/v0", "agent-collab/v1"))
        self.assertTrue(any("first non-empty line" in error for error in errors))

    def test_unknown_type(self) -> None:
        errors = MODULE.validate(VALID.replace("OFFER", "PING", 1))
        self.assertIn("unknown message type: PING", errors)

    def test_empty_body(self) -> None:
        message = "[agent-collab/v0] DONE\nfrom: a\nwork: unit\n"
        self.assertIn("message body is empty", MODULE.validate(message))

    def test_long_top_level_moves_to_thread(self) -> None:
        message = VALID + ("detail " * 70)
        self.assertTrue(any("exceeds 400" in error for error in MODULE.validate(message)))
        self.assertEqual(MODULE.validate(message, threaded=True), [])

    def test_connector_whitespace_is_accepted(self) -> None:
        self.assertEqual(MODULE.validate("\n\n" + VALID), [])

    def test_reply_can_inherit_parent_context_explicitly(self) -> None:
        reply = "Verified CI is green. Need: human review from Simon."
        self.assertTrue(MODULE.validate(reply))
        self.assertEqual(MODULE.validate(reply, inherited_context=True), [])

    def test_inherited_context_still_validates_full_envelope(self) -> None:
        invalid = VALID.replace("work: primevue-overlay\n", "")
        self.assertIn(
            "missing required field: work",
            MODULE.validate(invalid, inherited_context=True),
        )

    def test_inherited_context_accepts_compact_envelope(self) -> None:
        message = "[agent-collab/v0] UPDATE · dev-a/frontend · primevue-overlay\n\nChanged."
        self.assertEqual(MODULE.validate(message, inherited_context=True), [])

    def test_inherited_context_rejects_malformed_protocol_header(self) -> None:
        errors = MODULE.validate(
            "[agent-collab/v1] UPDATE\nUnversioned reply",
            inherited_context=True,
        )
        self.assertIn("invalid protocol envelope in inherited-context reply", errors)


if __name__ == "__main__":
    unittest.main()
