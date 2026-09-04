"""Command-line interface for LockPeek."""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections.abc import Sequence

from .core import Probe, probe_path

MAX_TARGETS = 128


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lockpeek",
        description="show which processes are holding a file or directory",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        help="file or directory to inspect (read-only)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable results",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return 1 when any target is locked; errors still return 2",
    )
    return parser


def _safe_terminal_text(value: str) -> str:
    output: list[str] = []
    for character in value:
        if character in "\n\r\t" or unicodedata.category(character) not in {
            "Cc",
            "Cf",
        }:
            output.append(character)
            continue
        codepoint = ord(character)
        output.append(
            f"\\x{codepoint:02x}" if codepoint <= 0xFF else f"\\u{codepoint:04x}"
        )
    return "".join(output)


def _render_human(probes: list[Probe]) -> str:
    lines: list[str] = []
    for probe in probes:
        lines.append(f"{_safe_terminal_text(probe.path)}: {probe.status.upper()}")
        for holder in probe.holders:
            lines.append(
                f"  PID {holder.pid}  {_safe_terminal_text(holder.name)}"
                f"  [{_safe_terminal_text(holder.source)}]"
            )
        if probe.message:
            lines.append(f"  {_safe_terminal_text(probe.message)}")
    return "\n".join(lines) + "\n"


def _exit_code(probes: list[Probe], strict: bool) -> int:
    if any(probe.status in {"error", "unavailable"} for probe in probes):
        return 2
    if strict and any(probe.status == "locked" for probe in probes):
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if len(args.paths) > MAX_TARGETS:
        parser.error(f"accepts at most {MAX_TARGETS} paths")

    probes = [probe_path(path) for path in args.paths]
    if args.json:
        payload = [probe.to_dict() for probe in probes]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        stream = (
            sys.stderr
            if any(probe.status in {"error", "unavailable"} for probe in probes)
            else sys.stdout
        )
        stream.write(_render_human(probes))
    return _exit_code(probes, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
