# Contributing to LockPeek

Thanks for helping make file-lock diagnosis less mysterious.

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

Keep backend calls read-only. Do not add process termination, shell execution,
clipboard access, telemetry, or network requests without a separate design and
security review. Add a regression test for every parser, platform, or output
boundary change.

## Pull requests

- Explain the user-visible problem and platform scope.
- Include a deterministic test or a manual reproduction.
- Keep public fixtures synthetic and free of personal paths or secrets.
- Run the complete command list above before requesting review.
