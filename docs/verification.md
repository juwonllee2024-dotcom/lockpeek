# Verification record

Status: release candidate; local and remote evidence are recorded before
publishing `v0.1.0`.

## TDD evidence

- **RED:** tests were written before implementation and failed with
  `ModuleNotFoundError: No module named 'lockpeek'`.
- **GREEN:** the parser, platform-neutral result contract, CLI JSON output,
  strict exit code, missing-path behavior, and lsof error handling passed after
  implementation.
- **Regression:** tests cover lsof record grouping, empty records, stable JSON,
  locked/unlocked status, stderr separation, and strict checks.

## Fresh command evidence

```text
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
mypy
python -m compileall -q src tests
python -m build
pip-audit --local
git diff --check
```

Observed locally with Python 3.11:

- `python -m unittest discover -s tests -v`: **8 tests passed**.
- `ruff check .`: exit 0.
- `ruff format --check .`: all Python files formatted.
- `mypy`: no issues found.
- `python -m compileall -q src tests`: exit 0.
- `python -m build`: wheel and sdist built successfully.
- `pip-audit --local`: no known vulnerabilities in installed dependencies;
  unpublished local packages may be listed as skipped.
- `git diff --check`: exit 0.

## Real input smoke test

```text
lockpeek examples/sample.txt
```

Observed behavior on Windows: `status=locked` and a `Python` holder were
returned while a short-lived local Python process held the fixture open. A
second probe after the child exited returned `status=unlocked`. The command did
not modify the fixture, kill a process, call a network service, or write a
report file.

## Security evidence

Codex Security standard scan:

- Scan ID: recorded after the final source snapshot is scanned.
- Coverage: complete repository snapshot.
- Findings: recorded from the canonical report; no unavailable protected result
  is represented as a success.
- TAC: recorded as unavailable if the connector is not connected.

Security boundary reviewed: no shell invocation, no process termination, no
file writes, bounded target count, lsof timeout, escaped terminal controls,
and explicit `UNAVAILABLE`/`ERROR` states for incomplete inspection.

## Release identity

- Release commit: recorded after all checks pass.
- CI run: recorded after public push and matrix success.
- Release: recorded after `v0.1.0` is published.
- Package SHA-256: recorded from exact GitHub release assets.
