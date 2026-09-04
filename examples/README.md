# LockPeek examples

Use any file or directory that is safe to inspect:

```console
lockpeek README.md
lockpeek --json README.md
lockpeek --strict README.md
```

To see a `LOCKED` result locally, open a document in an editor and run
`lockpeek` against that document. Some editors share files permissively, so an
`UNLOCKED` result is also valid. LockPeek never kills the editor.
