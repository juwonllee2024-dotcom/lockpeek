# LockPeek research note

Date: 2026-09-04
Timezone: America/Los_Angeles

## Product decision

Build **LockPeek** as a separate public repository. It answers one ordinary,
high-friction question: “What is holding this file?” The MVP is read-only,
cross-platform, local, and scriptable. It reports uncertainty instead of
pretending an unavailable backend proves a file is free.

The name `whylocked` was rejected after a GitHub search found an existing
repository with that name. `lockpeek` was available when checked.

## Four independent innovation questions

### 1. LockPeek — identify the holder before taking action

- **Confirmed fact:** users report that Windows “file in use” errors often hide
  which background program is responsible; one recent discussion received
  strong agreement ([example](https://www.reddit.com/r/pcmasterrace/comments/1sjp149/so_accurate/)).
  Microsoft File Locksmith can identify processes, but lives inside PowerToys,
  may need elevation, and also offers an inherently risky kill path
  ([Microsoft docs](https://learn.microsoft.com/en-us/windows/powertoys/file-locksmith)).
  POSIX `lsof` can identify users of a specific file, but its raw output is
  designed for inspection rather than a tiny cross-platform JSON contract
  ([lsof tutorial](https://github.com/lsof-org/lsof/blob/master/docs/tutorial.md)).
- **Innovation hypothesis:** a safe first answer—path, PID, process name,
  backend, confidence boundary—will be used more often than an unlock/kill
  button because it preserves user control.
- **One difference:** no destructive action; Windows Restart Manager and POSIX
  `lsof` share one minimal human/JSON surface.
- **Smallest 7-day experiment:** give ten Windows developers one locked-file
  scenario and measure whether they find the holder in under 30 seconds without
  opening Task Manager or Resource Monitor.

### 2. ArchiveLens — inspect an archive before extraction

- **Confirmed fact:** Zip Slip, symlink escapes, and archive bombs are real
  extraction boundaries. Existing projects already provide serious solutions:
  [safezip](https://github.com/barseghyanartur/safezip),
  [exarch](https://github.com/bug-ops/exarch), and
  [safe_unzip](https://github.com/tenuo-ai/safe_unzip).
- **Innovation hypothesis:** a zero-write “show me exactly what this archive
  would do” command could make safe extraction understandable.
- **One difference:** preview-only risk explanation before any write.
- **Smallest 7-day experiment:** audit 20 downloaded archives and compare
  preview usefulness against the existing archive manager.
- **Decision:** reject today; strong security value, but crowded implementation
  surface and greater format/edge-case burden than LockPeek.

### 3. PasteTable — turn a copied web table into safe TSV

- **Confirmed fact:** users still report tables collapsing into one spreadsheet
  cell or numbers being misread across locales ([example discussion](https://www.reddit.com/r/sheets/comments/10lp2qi/very_annoying_table_to_copy_paste_in_google_sheets/)).
  Browser extensions already advertise plain text, Markdown, JSON, and CSV
  transformations ([example](https://www.reddit.com/r/u_gowthamshankar05/comments/1n1bl6v/i_built_copy_master_pro_a_chrome_extension_that_makes_copy-paste_actually_useful_text_html_markdown_json_csv_colors_snippets_more/)).
- **Innovation hypothesis:** a local preview that shows column boundaries before
  copying could eliminate spreadsheet surprises.
- **One difference:** preview first, no clipboard watcher, no account.
- **Smallest 7-day experiment:** test 15 copied tables from three sites and
  measure clean paste rate into Sheets/Excel.
- **Decision:** reject today; useful but too close to established copy-format
  extensions and the previous LinePatch/browser-context portfolio.

### 4. QueueBite — finish saved reading instead of collecting it

- **Confirmed fact:** people describe saved-article backlogs as a processing
  problem, not a saving problem ([example](https://www.reddit.com/r/koreader/comments/1ucmw00/backlog_release_v13_save_articles_for_later_per_article_read_tracker_update/)).
  Read-it-later tools already cover saving, queues, and summaries.
- **Innovation hypothesis:** a local “one next item” queue with an expiry rule
  might reduce backlog guilt better than another library.
- **One difference:** completion pressure and expiry, not collection.
- **Smallest 7-day experiment:** ask ten readers to process one saved item daily
  for a week and record completion and abandonment.
- **Decision:** reject today; requires content fetching, reader integrations, or
  a service boundary before the value can be demonstrated safely.

## Score and selection

Scores are 1–5 for pain, novelty, buildability today, organic shareability,
and open-source fit.

| Candidate | Pain | Novelty | Build | Share | OSS | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LockPeek | 5 | 3 | 5 | 4 | 5 | **22/25** |
| ArchiveLens | 4 | 3 | 4 | 4 | 5 | 20/25 |
| PasteTable | 4 | 2 | 5 | 3 | 4 | 18/25 |
| QueueBite | 4 | 2 | 3 | 3 | 3 | 15/25 |

LockPeek wins because its first use is immediate, its result is visibly useful,
and its safety boundary is easy to explain. It does not promise complete kernel
visibility: permissions, elevated processes, and driver-level locks remain
known uncertainty.

## Business wedge

- **First customer:** Windows developers and support engineers who lose time to
  “file is in use” during builds, renames, sync, or removable-drive work.
- **First ten users:** local developer communities, Windows support threads, and
  colleagues who recently asked why a file cannot be moved. Ask for a task result,
  not a star.
- **Repeat reason:** the command is memorable and useful at the exact moment a
  file operation fails; JSON makes it reusable in scripts.
- **Revenue hypothesis:** core CLI stays free and MIT. A future optional desktop
  integration or team support bundle could be paid, but no revenue is validated.
- **Cost:** $0 for the MVP. Python standard library, Windows system DLL, and
  existing `lsof`; no runtime service or API key.

## Current trend signal

The current GitHub trend surface is rewarding highly legible developer tools,
agent tooling, and CLI-first projects ([GitHub Trending](https://github.com/trending),
[GitTrend daily ranking](https://gittrend.io/)). LockPeek follows the legibility
pattern without wrapping a model: one painful sentence, one command, one answer.

## Next decision

Do not change direction after stars alone. Measure ten first-use sessions,
record missing-holder cases, and only then decide whether an Explorer/Finder
copy-report integration deserves v0.2.0.
