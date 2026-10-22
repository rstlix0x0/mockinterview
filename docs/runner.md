# Runner contract

`runner/mi.py` is the single source of truth for sessions, problem selection, test results and scoring. Skills call it through the agent's Bash tool; the mod only reads the files it writes. Python 3.11 or newer, standard library only.

The runner never runs the engineer's code. The engineer solves in any language with their own toolchain; the agent writes a native test file from the pack's cases (`tests`), runs the engineer's test command, and reports which cases failed (`record`):

```
tests ──▶ agent writes stub + test file ──▶ agent runs the test command ──▶ record --failed NAMES
  (cases with expected values)              (go test, cargo test, pytest ...)     (counts, implementation score)
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" [global options] COMMAND [options]
```

## Global options

| Option | Default | Meaning |
|---|---|---|
| `--project DIR` | current directory | Project folder; session and work files go in `DIR/.mockinterview/` |
| `--data DIR` | `$CLAUDE_PLUGIN_DATA`, else `~/.mockinterview/data` | History. A value that still contains `${` is ignored |
| `--root DIR` | none, repeatable | Extra pack root |
| `--plugin-root DIR` | parent of `runner/` | Where built-in `content/` lives |
| `--pretty` | off | Indented JSON |

Every command prints **one JSON object** on stdout. Success: `{"ok": true, ...}`. Failure: `{"ok": false, "error": "message", "code": "bad_state"}`. Exit codes: `0` success, `1` user or state error, `2` internal error. `lint` and `selftest` exit `1` when a pack fails but still print `"ok": true` with the results; `record` exits `0` whatever it records. Python older than 3.11 gets `{"ok": false, "code": "python_version"}` and exit code `2`.

## Files

| File | Written by | Purpose |
|---|---|---|
| `<project>/.mockinterview/session.json` | `mi.py` only | Current session; read by skills and by the mod |
| `<project>/.mockinterview/work/` | `begin` empties it; then the agent and the engineer | The engineer's project for the round: the stub, the test file and any manifest (`go.mod`, `Cargo.toml` ...), in the session's language |
| `<project>/.mockinterview/work/design.md` | `begin` for design problems | The written design |
| `<project>/.mockinterview/work/estimate.json` | the engineer | Estimation claims for `estimate-check` |
| `<project>/.mockinterview/work/PROBLEM.md` | `begin` | Engineer-facing statement; the mod's Problem tab |
| `<project>/.mockinterview/work/archive/<time>/` | `begin` | The previous round's files, moved here, never deleted |
| `<data>/history.jsonl` | `score`, `abandon` | One JSON line per session |

`.mockinterview/` is created automatically by `draw` or `pick`, not at install. The runner prints a hint to add it to `.gitignore` and never edits that file.

## session.json

```json
{
  "schema": 1,
  "session_id": "20261021T093000Z-4f2a",
  "mode": "interview",
  "level": "senior",
  "state": "running",
  "seed": 918273,
  "round": 0,
  "rounds_total": 3,
  "language": "Go",
  "test_command": "go test ./...",
  "loop": [
    {"problem": "lc-c01-lru-cache", "type": "live-coding", "time_minutes": 30,
     "title": null, "started_at": null, "finished_at": null,
     "hints_used": [], "last_run": null, "result": null}
  ],
  "current": {
    "problem": "lc-c01-lru-cache", "type": "live-coding", "time_minutes": 30,
    "limit_seconds": 1800, "title": "LRU Cache", "started_at": "2026-10-21T09:31:12Z",
    "hints_used": [{"rung": "H1", "cost": 5}], "last_run": null
  },
  "scorecard": null,
  "created_at": "2026-10-21T09:30:00Z"
}
```

- `state`: `drawn` (a round is chosen, hidden), `running` (clock on), `finished` (all rounds done, not scored), `scored`, `abandoned`.
- In `interview` mode, `title` is `null` and the statement is withheld until `begin`. `current.title` and `PROBLEM.md` appear only after `begin`.
- `language` and `test_command` are set by `draw` or `pick` (`--lang`, `--test-cmd`) and hold for the whole session. Both are free text, stored with runs of whitespace collapsed; `language` defaults to `python`, `test_command` to null (the agent proposes one). The runner never runs either.
- `current` mirrors `loop[round]` for convenience; consumers can read only `state`, `mode`, `level`, `round`, `rounds_total` and `current`.
- `current.last_run` has the shape returned by `record` (below).
- After `score`, `scorecard` is `{"total": 78.5, "reading": "...", "rounds": [{"problem": "...", "score": 80.0, "ratings": {"dimension": 3}, "weights": {"dimension": 15}, "penalty": 5, "evidence": {"dimension": "one line"}}], "top_gap": "..."}`.
- Remaining time is `limit_seconds - (now - started_at)`; the mod computes it, the runner `status` command also reports it.

## Commands

| Command | Does |
|---|---|
| `list [--type T] [--level L] [--tag X] [--search WORD] [--roots] [--verbose]` | Index of packs (`id, title, type, level, tags, time_minutes`; `--verbose` adds `source`, `root`, `path`); `--search` also looks inside knowledge documents and adds `body_hits`; with `--roots`, roots and overrides |
| `show ID [--full]` | Prints the engineer-facing sections. `--full` (all sections, including hidden) is refused while an interview round is `drawn` or `running`; `show` itself is refused in that state. After the last round (`finished`, `scored`) or `abandon` it works again |
| `status` | `state`, `mode`, `level`, `round` (1-based, same as `round_number`), `rounds_total`, `type`, `time_minutes`, `title` (null until `begin` in interview mode), `elapsed_seconds`, `remaining_seconds`, `over_time`, `hints_used`, `has_run`, `language`, `test_command` |
| `draw --level L [--type T] [--seed N] [--lang TEXT] [--test-cmd TEXT]` | Starts an interview: builds the loop, draws all rounds, stores them, state `drawn`. Output has round count and round types, **no titles**, and `language`, `test_command` |
| `pick ID [--replace] [--lang TEXT] [--test-cmd TEXT]` | Starts a practice session on one problem (engineer's choice), state `drawn` |
| `begin` | State `running`, starts the clock, moves everything in `work/` into `work/archive/<time>/` (never deletes), writes `PROBLEM.md` (the statement plus the signature for live coding), and for design problems `work/design.md` from the template. Output: `statement`, `title`, `limit_seconds`, `started_at`, `files` (`work_dir`, and `design`), `problem_file`, `archived_previous`; live coding adds `signature`, `language`, `test_command`. One way: no re-draw |
| `tests [--all]` | Live coding, state `running`: the round's test cases. Output: `function`, `kind`, `compare`, `signature`, `language`, `test_command`, `set`, `count`, `cases[]` (`name`, `category`, `args`, `expected`). Visible cases only, or with `--all` also edge and hidden ones; in interview mode `--all` adds a `policy` reminder that those stay with the agent |
| `record [--mode visible\|all] [--failed NAMES] [--got NAME=VALUE]... [--error TEXT]` | Live coding, state `running`: stores the result of running the engineer's tests as `last_run`. `--mode` names the case set that was run (default `all`); `--failed` lists the failing case names, comma-separated, every other case of the set passed; `--got` adds what a failing case returned, shown in its details; `--error` means nothing ran (build or syntax error): every case of the set fails and the text is kept (last 2000 characters). A name outside the set is `unknown_case`, with `cases` |
| `hint` | Returns the next ladder rung from the notes and records its cost. Interview mode counts it; it never skips a rung. Output: `rung`, `cost`, `text`, `penalty_total`, `rungs_left` |
| `notes [--section clarify\|followups\|traps\|reference\|all] [--problem ID]` | The interviewer's route to hidden notes for the current round (or a finished round of this session with `--problem`). `reference` also returns the reference solution (Python) for live-coding problems. Hint and probe ladders are never returned here; use `hint`. Refused before `begin` in interview mode |
| `finish` | Stops the round, stores the result. More rounds: state `drawn`, `round` advances. Last round: state `finished` |
| `score --ratings FILE\|-` | Takes ratings JSON, computes scores, writes `scorecard`, appends to history, state `scored` |
| `abandon` | Ends the session, state `abandoned`, logged in history (no penalty) |
| `lint PATH... \| --all` | Validates pack files |
| `selftest [ID... \| --all] [--write-expected]` | Runs each pack's reference solution on its cases and compares with the stored `expected` values (`failures` lists the first three that differ). `--write-expected` first sets every `expected` from the reference and rewrites the tests block. The only command that executes pack code |
| `history [--last N]` | Past sessions and per-tag averages |
| `repeat ID --reason TEXT [--days 3]` / `repeat --list` | Marks a problem to repeat (appends to `.mockinterview/repeat.md`: `DATE \| id \| reason \| repeat after DATE`), or lists the marks and which are due |
| `estimate-check` | Design problems: checks `work/estimate.json` against the pack's reference estimate |
| `design-lint` | Design problems: structure check of `work/design.md` |

## record result

```json
{
  "ok": true, "pass": false, "problem": "lc-a01-two-sum", "mode": "all",
  "passed": 9, "failed": 2, "total": 11,
  "by_category": {"visible": "2/2", "edge": "2/3", "hidden": "5/6"},
  "failures": [
    {"name": "edge-duplicates", "category": "edge", "shown": true,
     "args": "{\"nums\": [3, 3], \"target\": 6}", "expected": "[0, 1]", "got": "[0,0]"},
    {"name": "random-2", "category": "hidden", "shown": false}
  ],
  "details_policy": "interview: only visible failures are shown",
  "recorded_at": "2026-10-22T09:11:13Z",
  "elapsed_seconds": 412, "remaining_seconds": 188, "over_time": false
}
```

With `--error`, the result also has `error` (the build or run output). In `interview` mode `failures[].shown` is `false` for `edge` and `hidden` cases and their `args`, `expected` and `got` are omitted; only the counts in `by_category` are visible. In `practice` mode, details are shown for up to three failing cases.

## Scoring

Ratings are 0 to 4. `score = sum(weight x rating / 4) - hint penalties`. Rung costs are 0, 5, 10 and 20 points for H0 to H3 (live coding) and for P0 to P3 (design). In live coding every rung used is deducted (cumulative); in system design only the highest probe step reached is deducted. For live coding the `implementation` rating is computed from the last `record` (4 x share of passing cases; a visible-only record counts only the visible cases); every other rating comes from the `ratings` file.

Live-coding dimensions and weights: `framing` 15, `approach` 15, `implementation` 25, `quality` 10, `testing` 15, `communication` 10, `adaptability` 10.

System-design dimensions and weights: `scoping` 15, `estimation` 10, `architecture` 25, `deep_dives` 30, `reliability` 10, `communication` 10.

Ratings file:

```json
{"ratings": {"lc-c01-lru-cache": {"framing": 3, "approach": 3, "quality": 2, "testing": 3, "communication": 3, "adaptability": 2}},
 "evidence": {"lc-c01-lru-cache": {"framing": "asked about capacity zero"}},
 "top_gap": "testing before coding"}
```

Readings: 85 or more ready for senior rounds on this kind of problem; 70 to 84 close, repeat with a different problem; 55 to 69 repeat in 3 days after review; below 55 go back one level. These thresholds are this project's own calibration, not an industry standard.

## Selection

Loop templates by level: junior `lc lc`; mid `lc lc sd`; senior `lc lc sd`; staff `sd sd lc`. Each round draws from packs of that type whose `level` contains the level, excluding ids from the last 6 sessions, weighted toward tags with the lowest past scores, using `random.Random(seed)`. If a pool is empty, the runner first allows recent ids, then adjacent levels, and reports a `warnings` entry. `--type` forces every round to that type. Packs that fail structural checks at load are skipped and reported in `warnings`.
