# Security policy

## Scope

LockPeek is a local, read-only diagnostic. It inspects a user-selected file or
directory through Windows Restart Manager or the POSIX `lsof` executable. It
does not kill processes, change permissions, modify files, run a shell, call a
network service, access the clipboard, or upload paths or contents.

Results are best-effort. Windows can omit processes that require higher
privileges or are not registered with Restart Manager. `lsof` can omit files
the current user cannot inspect. An `UNAVAILABLE` or `ERROR` result must be
treated as unknown, not as proof that a path is free.

The CLI passes arguments as an argv list with no shell. It limits one invocation
to 128 targets, uses a five-second `lsof` timeout, and emits control characters
as escaped text in human output. JSON output is intended for local scripts.

## Reporting a vulnerability

Please report security issues privately through
[GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/about-repository-security-advisories).
Include the affected version, OS, reproduction steps, and a minimal safe
sample. Do not attach private paths, credentials, or proprietary documents.

If private reporting is unavailable, open a public issue with a sanitized
description and ask for a private contact route.
