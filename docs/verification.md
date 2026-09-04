# Verification record

Status: `v0.1.0` is published; this record captures the local and remote
evidence for the release.

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
- Package smoke: the built wheel installed into a fresh offline virtual
  environment and returned a valid JSON result for `examples/sample.txt`.

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

Dedicated protected security scan: unavailable in this execution because no
Codex Security connector was exposed. No protected result is represented as a
success.

Local security evidence:

- Source-boundary scan found no shell execution, process termination, network
  client, or socket calls.
- Secret-pattern scan found no token, API-key, password, or secret assignments.
- `pip-audit --local` reported no known vulnerabilities in the installed
  dependencies; local unpublished packages were listed as skipped.

Security boundary reviewed: no shell invocation, no process termination, no
file writes, bounded target count, lsof timeout, escaped terminal controls,
and explicit `UNAVAILABLE`/`ERROR` states for incomplete inspection.

## Release identity

- Release commit: `2980f78c4f01aba5b929010290a59a7d91eab8b3`.
- CI run: 12/12 matrix jobs passed —
  https://github.com/juwonllee2024-dotcom/lockpeek/actions/runs/33897992443
- Release: https://github.com/juwonllee2024-dotcom/lockpeek/releases/tag/v0.1.0
- Package SHA-256:
  - `lockpeek-0.1.0-py3-none-any.whl`: `f69013d3e42aa18b67d242b9a141d308f41808a73c98145ab977eca3b93b6e82`
  - `lockpeek-0.1.0.tar.gz`: `4f7a9259c92befb5d13f20822adb5f6a29cc7b75b0b1faa09848bdd25f81f9ae`
