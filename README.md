# LockPeek 🔎

### Stop guessing which app is holding your file.

One command. Read-only answer. No kill button.

```console
lockpeek report.docx
```

```text
C:\work\report.docx: LOCKED
  PID 4312  WINWORD.EXE  [restart-manager]
```

LockPeek turns the vague “file is in use” moment into a small, reviewable
answer. It checks a file or directory with the native Windows Restart Manager,
or POSIX `lsof` on Linux and macOS. It never terminates a process or edits the
target.

## Why this exists

The operating system knows a process may be holding a file, but the useful
answer is often buried behind Resource Monitor, a large `lsof` listing, or a
third-party “unlock” button. LockPeek gives developers, support engineers, and
everyday desktop users one safe first step:

```text
name the path → see the holder → decide yourself
```

## Install

Requires Python 3.10 or newer.

```console
git clone https://github.com/juwonllee2024-dotcom/lockpeek.git
cd lockpeek
python -m pip install .
```

On Linux or macOS, install `lsof` through your operating system package
manager. Windows uses `rstrtmgr.dll`, which is included with Windows.

## Use it

Inspect one or more paths:

```console
lockpeek report.docx
lockpeek build/ dist/app.exe
```

Produce stable output for a script:

```console
lockpeek --json report.docx
```

Make a check fail when a holder is found:

```console
lockpeek --strict report.docx
```

Exit codes:

- `0`: every target is reported `UNLOCKED`, or a holder exists without `--strict`.
- `1`: a target is `LOCKED` and `--strict` was supplied.
- `2`: a path, backend, permission, or usage error occurred.

## What you can trust

- No process termination or “force unlock”.
- No shell, network, cloud account, clipboard, or telemetry.
- Human output plus machine-readable JSON.
- Windows and POSIX backends behind one small command.
- `UNAVAILABLE` means “could not inspect”, never “safe to delete”.

Results are best-effort. Windows may omit elevated or unregistered processes;
POSIX `lsof` may need additional permission to see another user's files. See
[`SECURITY.md`](SECURITY.md) for the boundary.

## Development

```console
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
mypy
python -m build
pip-audit --local
```

The release checklist and a real local probe are recorded in
[`docs/verification.md`](docs/verification.md). Research and rejected
alternatives are in [`docs/research.md`](docs/research.md).

## Roadmap

The next experiment is a tiny Explorer/Finder integration that only copies a
read-only LockPeek report. Process termination remains out of scope until a
separate safety review proves it belongs.

## License

MIT. See [`LICENSE`](LICENSE).
