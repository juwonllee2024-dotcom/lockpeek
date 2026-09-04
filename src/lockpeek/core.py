"""Cross-platform, read-only file-holder inspection."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ProbeStatus = Literal["locked", "unlocked", "unavailable", "error"]


@dataclass(frozen=True)
class Holder:
    """A process reported as using a target path."""

    pid: int
    name: str
    source: str


@dataclass(frozen=True)
class Probe:
    """A stable, JSON-friendly inspection result."""

    path: str
    status: ProbeStatus
    holders: tuple[Holder, ...]
    backend: str
    message: str | None

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic representation for scripts and JSON."""

        return {
            "path": self.path,
            "status": self.status,
            "backend": self.backend,
            "message": self.message,
            "holders": [
                {"pid": holder.pid, "name": holder.name, "source": holder.source}
                for holder in self.holders
            ],
        }


def parse_lsof_output(output: str) -> list[Holder]:
    """Parse lsof's machine-readable ``-Fpcfn`` output."""

    holders: list[Holder] = []
    current: dict[str, str] = {}

    def flush() -> None:
        pid_text = current.get("p")
        if pid_text is None or not pid_text.isdigit():
            return
        holders.append(
            Holder(
                pid=int(pid_text),
                name=current.get("c") or "unknown",
                source="lsof",
            )
        )

    for line in output.splitlines():
        if not line:
            continue
        field, value = line[0], line[1:]
        if field == "p":
            flush()
            current = {"p": value}
        elif field in {"c", "n"}:
            current[field] = value
    flush()
    return holders


def probe_from_holders(
    path: str, holders: list[Holder], *, backend: str, message: str | None = None
) -> Probe:
    """Build a result from backend-neutral holder data."""

    frozen_holders = tuple(holders)
    return Probe(
        path=path,
        status="locked" if frozen_holders else "unlocked",
        holders=frozen_holders,
        backend=backend,
        message=message,
    )


def _probe_lsof(path: Path) -> Probe:
    executable = shutil.which("lsof")
    if executable is None:
        return Probe(
            path=str(path),
            status="unavailable",
            holders=(),
            backend="lsof",
            message="lsof was not found on PATH",
        )

    try:
        completed = subprocess.run(
            [executable, "-Fpcfn", "--", str(path)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Probe(
            path=str(path),
            status="error",
            holders=(),
            backend="lsof",
            message=f"lsof failed: {exc}",
        )

    holders = parse_lsof_output(completed.stdout)
    if holders or completed.returncode == 0:
        return probe_from_holders(str(path), holders, backend="lsof")
    if completed.returncode == 1 and not completed.stderr.strip():
        return probe_from_holders(str(path), [], backend="lsof")
    detail = completed.stderr.strip() or (
        f"lsof exited with status {completed.returncode}"
    )
    return Probe(
        path=str(path),
        status="error",
        holders=(),
        backend="lsof",
        message=detail,
    )


def _probe_windows(path: Path) -> Probe:
    try:
        from .windows import find_holders

        holders = find_holders(path)
    except OSError as exc:
        return Probe(
            path=str(path),
            status="error",
            holders=(),
            backend="restart-manager",
            message=f"Windows Restart Manager failed: {exc}",
        )
    return probe_from_holders(str(path), holders, backend="restart-manager")


def probe_path(value: str | Path) -> Probe:
    """Inspect one existing file or directory without modifying it."""

    path = Path(value).expanduser()
    if not path.exists():
        return Probe(
            path=str(path),
            status="error",
            holders=(),
            backend="filesystem",
            message="path does not exist",
        )

    resolved = path.resolve()
    if os.name == "nt":
        return _probe_windows(resolved)
    return _probe_lsof(resolved)
