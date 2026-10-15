#!/usr/bin/env python3
"""Regression tests for trial-derived collaboration guidance."""

from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class GuidanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.protocol = (SKILL_DIR / "reference/protocol.md").read_text(encoding="utf-8")
        cls.harness = (SKILL_DIR / "reference/harness-integration.md").read_text(
            encoding="utf-8"
        )

    def test_v0_compatibility_floor_is_preserved(self) -> None:
        self.assertIn("Follow [`agent-collab/v0`]", self.skill)
        self.assertNotIn("agent-collab/v1", self.skill + self.protocol + self.harness)

    def test_authority_requires_scoped_provenance(self) -> None:
        self.assertIn("scoped standing delegation", self.skill)
        self.assertIn("subject, action class, venue", self.protocol)

    def test_review_verdict_is_revision_specific(self) -> None:
        self.assertIn("exact artifact revision", self.skill)
        self.assertIn("changed head, base, integration result", self.protocol)

    def test_root_and_reply_cursors_are_independent(self) -> None:
        for key in (
            "coordination_roots",
            "coordination_replies",
            "learning_roots",
            "learning_replies",
        ):
            self.assertIn(key, self.harness)

    def test_no_delta_path_is_quiet_but_observable(self) -> None:
        self.assertIn("liveness receipt", self.harness)
        self.assertIn("healthy ticks remain silent", self.harness)


if __name__ == "__main__":
    unittest.main()
