#!/usr/bin/env python3
"""Unit tests for slack_blocks. Run: python3 slack_blocks.test.py"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from slack_blocks import (  # noqa: E402
    SIGNAL_POST_SHORTCODES,
    C,
    D,
    F,
    H,
    S,
    BlockError,
    Digest,
    metric_prose_sections,
    permalink,
    send_thread,
    validate_blocks,
)


class TestBuilders(unittest.TestCase):
    def test_header_is_plain_text(self):
        self.assertEqual(H("Rollout check")["text"]["type"], "plain_text")

    def test_fields_become_two_column_cells(self):
        b = F(["*A*\n1", "*B*\n2"])
        self.assertEqual(len(b["fields"]), 2)
        self.assertTrue(all(c["type"] == "mrkdwn" for c in b["fields"]))

    def test_context_wraps_elements(self):
        self.assertEqual(C("small")["elements"][0]["text"], "small")


class TestValidation(unittest.TestCase):
    def ok(self):
        return [H("Title"), S("body"), D, F(["*A*\n1"]), C("note")]

    def test_accepts_a_well_formed_message(self):
        validate_blocks(self.ok())

    def test_rejects_empty(self):
        with self.assertRaises(BlockError):
            validate_blocks([])

    def test_rejects_too_many_blocks(self):
        with self.assertRaises(BlockError) as e:
            validate_blocks([D] * 51)
        self.assertIn("exceeds Slack's 50", str(e.exception))

    def test_rejects_too_many_fields(self):
        with self.assertRaises(BlockError):
            validate_blocks([H("T"), F([f"*{i}*" for i in range(11)])])

    def test_rejects_oversized_field(self):
        with self.assertRaises(BlockError):
            validate_blocks([H("T"), F(["x" * 2001])])

    def test_rejects_oversized_section(self):
        with self.assertRaises(BlockError):
            validate_blocks([H("T"), S("x" * 3001)])

    def test_rejects_malformed_link(self):
        with self.assertRaises(BlockError) as e:
            validate_blocks([H("T"), S("see <https://example.com/pull/1 for detail")])
        self.assertIn("malformed link", str(e.exception))

    def test_rejects_link_or_bold_in_header(self):
        with self.assertRaises(BlockError):
            validate_blocks([H("*bold*")])
        with self.assertRaises(BlockError):
            validate_blocks([H("<https://x|y>")])

    def test_rejects_unsupported_block_type(self):
        with self.assertRaises(BlockError):
            validate_blocks([H("T"), {"type": "image", "image_url": "u", "alt_text": "a"}])

    def test_rejects_section_with_neither_text_nor_fields(self):
        with self.assertRaises(BlockError):
            validate_blocks([H("T"), {"type": "section"}])


class TestLinkAndEmojiGuards(unittest.TestCase):
    """These are the failures that survive a JSON-valid payload."""

    def test_rejects_overlong_link_label(self):
        with self.assertRaises(BlockError) as e:
            validate_blocks([H("T"), S("<https://x|" + "word " * 40 + ">")])
        self.assertIn("labels should be short", str(e.exception))

    def test_rejects_unbalanced_bold_inside_a_link_label(self):
        """The real regression: a missing `>` let the label eat the next clause."""
        bad = ("<https://us.posthog.com/x|G16 the flag has no waitlist / random variants.* "
               "The gates doc says random users are tagged by flag variant, and that *the "
               "random group decides, waitlist is reference only>")
        with self.assertRaises(BlockError) as e:
            validate_blocks([H("T"), S(bad)])
        self.assertIn("swallowed", str(e.exception).lower() + "x")

    def test_rejects_link_label_spanning_a_sentence_break(self):
        with self.assertRaises(BlockError) as e:
            validate_blocks([H("T"), S("<https://x|A fix landed. Then another thing happened>")])
        self.assertIn("sentence break", str(e.exception))

    def test_accepts_a_normal_link(self):
        validate_blocks([H("T"), S("see <https://example.com/pull/1|cloud 1> for detail")])

    def test_rejects_shortcode_outside_the_set_when_one_is_given(self):
        with self.assertRaises(BlockError) as e:
            validate_blocks([H("T"), S(":tada: shipped")], shortcodes=SIGNAL_POST_SHORTCODES)
        self.assertIn("not in the allowed set", str(e.exception))

    def test_accepts_the_signal_post_shortcodes(self):
        validate_blocks(
            [H("T"), S(":pr-open: :pr-merged: :git-approved: :pr-closed: :github-queued: :thread:")],
            shortcodes=SIGNAL_POST_SHORTCODES,
        )

    def test_other_genres_keep_their_own_emoji(self):
        """A leaderboard's trophies are the point of that message. Universal checks still apply."""
        validate_blocks([H("Coverage Leaderboard"), S(":trophy: :first_place_medal: 82% unit")])
        with self.assertRaises(BlockError):
            validate_blocks([H("T"), S("shipped \U0001f680")])  # Unicode still rejected

    def test_rejects_unicode_emoji(self):
        with self.assertRaises(BlockError):
            validate_blocks([H("T"), S("shipped \U0001f680")])

    def test_blockquote_marker_is_not_an_unbalanced_link(self):
        validate_blocks([H("T"), S("> *verdict line* with no links at all")])


class TestDigest(unittest.TestCase):
    def build(self):
        d = Digest(channel="C1", headline_fallback="fallback")
        d.headline = [H("Title"), S("> *verdict*"), D, F(["*A*\n1"])]
        d.add_part("1 · Detail", [S("body")])
        return d

    def test_add_part_prepends_its_own_header(self):
        d = self.build()
        self.assertEqual(d.parts[0].blocks[0]["type"], "header")
        self.assertEqual(d.parts[0].blocks[0]["text"]["text"], "1 · Detail")

    def test_headline_must_open_with_a_header(self):
        d = self.build()
        d.headline = [S("no header")]
        with self.assertRaises(BlockError):
            d.validate()

    def test_payloads_carry_channel_and_fallback_and_disable_unfurl(self):
        p = self.build().payloads()
        self.assertEqual(len(p), 2)
        self.assertTrue(all(x["channel"] == "C1" for x in p))
        self.assertFalse(p[0]["unfurl_links"])
        self.assertEqual(p[0]["text"], "fallback")
        self.assertEqual(p[1]["text"], "1 · Detail")

    def test_write_names_the_headline_first(self):
        import tempfile

        with tempfile.TemporaryDirectory() as t:
            paths = self.build().write(f"{t}/run-")
            self.assertTrue(paths[0].endswith("00-head.json"))
            self.assertTrue(paths[1].endswith("01.json"))


class TestSendThread(unittest.TestCase):
    def payloads(self):
        return [{"text": "head"}, {"text": "p1"}, {"text": "p2"}]

    def test_parts_are_threaded_under_the_headline(self):
        seen = []

        def poster(p):
            seen.append(p)
            return {"ok": True, "ts": f"ts{len(seen)}"}

        ts = send_thread(self.payloads(), poster)
        self.assertEqual(ts, ["ts1", "ts2", "ts3"])
        self.assertNotIn("thread_ts", seen[0])
        self.assertEqual(seen[1]["thread_ts"], "ts1")
        self.assertEqual(seen[2]["thread_ts"], "ts1")

    def test_a_failed_headline_sends_nothing_else(self):
        calls = []

        def poster(p):
            calls.append(p)
            return {"ok": False, "error": "invalid_blocks"}

        with self.assertRaises(BlockError) as e:
            send_thread(self.payloads(), poster)
        self.assertIn("no parts sent", str(e.exception))
        self.assertEqual(len(calls), 1)

    def test_a_failed_part_reports_which_index_stopped(self):
        def poster(p):
            if p.get("text") == "p2":
                return {"ok": False, "error": "ratelimited"}
            return {"ok": True, "ts": "t"}

        with self.assertRaises(BlockError) as e:
            send_thread(self.payloads(), poster)
        self.assertIn("part 2 failed", str(e.exception))

    def test_empty_input_is_a_noop(self):
        self.assertEqual(send_thread([], lambda p: {"ok": True, "ts": "x"}), [])


class TestPermalink(unittest.TestCase):
    def test_strips_the_dot(self):
        self.assertEqual(
            permalink("example", "C0123456789", "1790292488.923229"),
            "https://example.slack.com/archives/C0123456789/p1790292488923229",
        )


class TestTwoColumnDefault(unittest.TestCase):
    """Numbers belong in a two-column `fields` block, not in a prose section.

    The check has to reject a table typed as prose while leaving real prose alone, so
    every control below is a message that must still validate.
    """

    def test_rejects_a_table_typed_as_prose(self):
        blocks = [
            H("Report"),
            S("*Opened* 220\n*Sent* 79\n*Ran it* 25"),
        ]
        with self.assertRaises(BlockError) as ctx:
            validate_blocks(blocks, "prose-table")
        self.assertIn("fields", str(ctx.exception))

    def test_reports_index_and_count(self):
        blocks = [H("Report"), S("prose"), S("*A* 1\n*B* 2\n*C* 3\n*D* 4")]
        self.assertEqual(metric_prose_sections(blocks), [(2, 4)])

    def test_control_prose_with_numbers_inline_is_fine(self):
        """A figure inside a sentence is prose, not a table."""
        blocks = [
            H("Report"),
            S(
                "The agent is making money. Yesterday it earned $259 from the 79 people who "
                "used it, keeping 30 cents on the dollar.\n"
                "It is only switched on for 14.1% of Cloud, and at that take-up it is a "
                "$25-35M a year business.\n"
                "Most people who see it still will not touch it, which is the whole point."
            ),
        ]
        validate_blocks(blocks, "prose")

    def test_control_pr_bullet_list_is_fine(self):
        """Fix-status bullets carry PR numbers but each line is a clause, not a cell."""
        blocks = [
            H("Report"),
            S(
                "• <https://example.com/1|10593> (workflows saved in an older internal format "
                "were refused outright, killing every request on that canvas) is live in prod\n"
                "• <https://example.com/2|10607> (the setup step gave up when the document "
                "moved mid-request, which is why one customer failed on every prompt) is merged\n"
                "• <https://example.com/3|10625> (whitelisted people were locked out because "
                "the server checked the flag without sending their email) is awaiting review"
            ),
        ]
        validate_blocks(blocks, "fixes")

    def test_control_fields_block_is_the_right_answer(self):
        blocks = [H("Report"), F(["*Opened*\n220", "*Sent*\n79", "*Ran it*\n25"])]
        validate_blocks(blocks, "fields")

    def test_escape_hatch(self):
        blocks = [H("Report"), S("*A* 1\n*B* 2\n*C* 3")]
        validate_blocks(blocks, "opt-out", require_columns=False)

    def test_two_short_metric_lines_are_below_the_threshold(self):
        blocks = [H("Report"), S("*A* 1\n*B* 2")]
        validate_blocks(blocks, "two-lines")


class TestCodeBlocksAreExemptFromShortcodeScan(unittest.TestCase):
    """`:name:` does not render inside a code fence or span, so it must not be scanned.

    A chronological trace is the real case: 01:02:48 contains the substring `:02:`, which
    the scanner read as an unknown emoji and rejected a legitimate Datadog trace.
    """

    def test_timestamps_in_a_fence_are_allowed(self):
        blocks = [H("Trace"), S("```\n01:02:48  opened the panel\n01:36:03  credit stopped\n```")]
        validate_blocks(blocks, "fence", SIGNAL_POST_SHORTCODES)

    def test_timestamps_in_an_inline_span_are_allowed(self):
        blocks = [H("Trace"), S("It stopped at `01:36:03` which is two seconds later.")]
        validate_blocks(blocks, "span", SIGNAL_POST_SHORTCODES)

    def test_a_bad_shortcode_outside_code_still_raises(self):
        blocks = [H("Trace"), S("```\n01:02:48\n```\nand then :definitely_not_allowed: after")]
        with self.assertRaises(BlockError) as ctx:
            validate_blocks(blocks, "outside", SIGNAL_POST_SHORTCODES)
        self.assertIn("definitely_not_allowed", str(ctx.exception))

    def test_an_allowed_shortcode_outside_code_still_passes(self):
        blocks = [H("Trace"), S("```\n01:02:48\n```\nshipped :pr-merged: and done")]
        validate_blocks(blocks, "allowed", SIGNAL_POST_SHORTCODES)

    def test_a_fence_split_across_blocks_does_not_exempt_what_is_between(self):
        """Slack formats each block independently, so it can never pair these delimiters.

        A regex over the joined payload can, and then it deletes the middle block before
        the scan. This is the payload the previous version of this test claimed to cover
        and did not — it passed with and without the fix.
        """
        blocks = [H("T"), S("```\n01:02:48"), S("tail :nope_not_real:"), S("01:36:03\n```")]
        with self.assertRaises(BlockError):
            validate_blocks(blocks, "split-fence", SIGNAL_POST_SHORTCODES, require_columns=False)

    def test_two_stray_backticks_in_different_blocks_do_not_exempt_the_middle(self):
        """The realistic case: one unmatched backtick in each of two blocks of prose."""
        blocks = [H("T"), S("the `flag is on"), S("bad :nope_not_real: here"), S("and `done")]
        with self.assertRaises(BlockError):
            validate_blocks(blocks, "stray", SIGNAL_POST_SHORTCODES, require_columns=False)

    def test_a_fence_marker_in_a_header_does_not_exempt_the_next_block(self):
        blocks = [H("``` T"), S("bad :nope_not_real: `x`")]
        with self.assertRaises(BlockError):
            validate_blocks(blocks, "header-fence", SIGNAL_POST_SHORTCODES, require_columns=False)

    def test_field_cells_are_scanned_separately_from_each_other(self):
        blocks = [H("T"), F(["*A*\n```\n01:02:48", "*B*\n:nope_not_real:", "*C*\n```"])]
        with self.assertRaises(BlockError):
            validate_blocks(blocks, "cells", SIGNAL_POST_SHORTCODES, require_columns=False)

    def test_a_multi_line_trace_validates_through_the_digest_entry_point(self):
        """The reported payload has 3+ lines, so it also trips the column check.

        The old regression test used a two-line trace, which sits under MIN_METRIC_LINES
        and therefore never reproduced the real message. Digest has to be able to carry
        one, or the documented genre is unreachable from the documented entry point.
        """
        d = Digest("C0", "fallback", require_columns=False)
        d.headline = [H("Trace"), S("body")]
        d.add_part("trace", [S("```\n01:02:48  opened\n01:19:11  ran it\n01:36:03  stopped\n```")])
        d.validate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
