#!/usr/bin/env python3
"""Validate the visible agent-collab/v0 Slack message envelope."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HEADER = re.compile(r"^\[agent-collab/v0\]\s+([A-Z]+)\s*$")
TYPES = {
    "OFFER",
    "CLAIM",
    "QUESTION",
    "DECISION",
    "UPDATE",
    "HANDOFF",
    "BLOCKED",
    "OWE",
    "RECONCILE",
    "DONE",
}
REQUIRED = ("from", "to", "work")


def validate(
    text: str, *, threaded: bool = False, inherited_context: bool = False
) -> list[str]:
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    errors: list[str] = []
    if not lines:
        return ["message is empty"]

    if inherited_context:
        if HEADER.fullmatch(lines[0].strip()):
            return validate(text, threaded=True)
        if lines[0].lstrip().startswith("[agent-collab/"):
            return ["invalid protocol envelope in inherited-context reply"]
        return []

    kind: str | None = None
    match = HEADER.fullmatch(lines[0].strip())
    if not match:
        errors.append("first non-empty line must be '[agent-collab/v0] TYPE'")
    else:
        kind = match.group(1)
        if kind not in TYPES:
            errors.append(f"unknown message type: {kind}")

    fields: dict[str, str] = {}
    body_start = len(lines)
    for index, line in enumerate(lines[1:], start=1):
        if not line.strip():
            body_start = index + 1
            break
        if ":" not in line:
            errors.append(f"invalid envelope line {index + 1}: expected 'key: value'")
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip()

    for key in REQUIRED:
        if not fields.get(key):
            errors.append(f"missing required field: {key}")

    body = "\n".join(lines[body_start:]).strip()
    if not body:
        errors.append("message body is empty")
    elif kind in {"OWE", "RECONCILE"} and not re.search(
        r"(?im)^Obligation:\s*\S+", body
    ):
        errors.append(f"{kind} message body must include 'Obligation: <stable-id>'")
    if not threaded and len(text) > 400:
        errors.append("top-level message exceeds 400 characters; move detail to a thread")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="-", help="message file, or - for stdin")
    parser.add_argument("--threaded", action="store_true", help="skip top-level length limit")
    parser.add_argument(
        "--inherited-context",
        action="store_true",
        help="validate a reply whose unchanged envelope is supplied by its Slack parent",
    )
    parser.add_argument("--json", action="store_true", help="emit a JSON result")
    args = parser.parse_args()

    text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    errors = validate(
        text, threaded=args.threaded, inherited_context=args.inherited_context
    )
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}))
    elif errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
    else:
        print("valid agent-collab/v0 message")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
