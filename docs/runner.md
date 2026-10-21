# Runner contract

`runner/mi.py` is the single source of truth for sessions, problem selection, test running and scoring. Skills call it through the agent's Bash tool; the mod only reads the files it writes. Python 3.10 or newer, standard library only.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" [global options] COMMAND [options]
```

## Global options

| Option | Default | Meaning |
|---|---|---|
| `--project DIR` | current directory | Project folder; session and work files go in `DIR/.mockinterview/` |
| `--data DIR` | `$CLAUDE_PLUGIN_DATA`, else `~/.mockinterview/data` | History, trust list and perf cache. A value that still contains `${` is ignored |
| `--root DIR` | none, repeatable | Extra pack root |
| `--plugin-root DIR` | parent of `runner/` | Where built-in `content/` lives |
| `--pretty` | off | Indented JSON |

Every command prints **one JSON object** on stdout. Success: `{"ok": true, ...}`. Failure: `{"ok": false, "error": "message", "code": "bad_state"}`. Exit codes: `0` success, `1` user or state error, `2` internal error. `run` and `selftest` exit `1` when a test fails but still print `"ok": true` with the results.

## Files

| File | Written by | Purpose |
|---|---|---|
| `<project>/.mockinterview/session.json` | `mi.py` only | Current session; read by skills and by the mod |
| `<project>/.mockinterview/work/solution.py` | `begin` (stub), then the engineer | The solution under test |
| `<project>/.mockinterview/work/design.md` | `begin` for design problems | The written design |
| `<project>/.mockinterview/work/estimate.json` | the engineer | Estimation claims for `estimate-check` |
| `<project>/.mockinterview/work/PROBLEM.md` | `begin` | Engineer-facing statement; the mod's Problem tab |
| `<project>/.mockinterview/work/archive/` | `begin` | Earlier solutions moved here, never deleted |
| `<data>/history.jsonl` | `score`, `abandon` | One JSON line per session |
| `<data>/trust.json` | `trust` | Acknowledged non-built-in roots |

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
- `current` mirrors `loop[round]` for convenience; consumers can read only `state`, `mode`, `level`, `round`, `rounds_total` and `current`.
- `current.last_run` has the shape returned by `run` (below).
- After `score`, `scorecard` is `{"total": 78.5, "reading": "...", "rounds": [{"problem": "...", "score": 80.0, "ratings": {"dimension": 3}, "weights": {"dimension": 15}, "penalty": 5, "evidence": {"dimension": "one line"}}], "top_gap": "..."}`.
- Remaining time is `limit_seconds - (now - started_at)`; the mod computes it, the runner `status` command also reports it.

## Commands

| Command | Does |
|---|---|
| `list [--type T] [--level L] [--tag X] [--search WORD] [--roots] [--verbose]` | Index of packs (`id, title, type, level, tags, time_minutes`; `--verbose` adds `source`, `root`, `path`); `--search` also looks inside knowledge documents and adds `body_hits`; with `--roots`, roots, trust status and overrides |
| `show ID [--full]` | Prints the engineer-facing sections. `--full` (all sections, including hidden) is refused while an interview round is `drawn` or `running`; `show` itself is refused in that state. After the last round (`finished`, `scored`) or `abandon` it works again |
| `status` | `state`, `mode`, `level`, `round` (1-based, same as `round_number`), `rounds_total`, `type`, `time_minutes`, `title` (null until `begin` in interview mode), `elapsed_seconds`, `remaining_seconds`, `over_time`, `hints_used`, `has_run` |
| `draw --level L [--type T] [--seed N]` | Starts an interview: builds the loop, draws all rounds, stores them, state `drawn`. Output has round count and round types, **no titles** |
| `pick ID` | Starts a practice session on one problem (engineer's choice), state `drawn` |
| `begin` | State `running`, starts the clock, writes `PROBLEM.md`, archives any earlier `solution.py` or `design.md` into `work/archive/` (never deletes), writes the stub or design template. Output: `statement`, `title`, `limit_seconds`, `started_at`, `files`, `problem_file`. One way: no re-draw |
| `run [--mode visible\|all] [--perf] [--fuzz N]` | Runs `work/solution.py` against the current round's tests (live-coding only) |
| `hint` | Returns the next ladder rung from the notes and records its cost. Interview mode counts it; it never skips a rung. Output: `rung`, `cost`, `text`, `penalty_total`, `rungs_left` |
| `notes [--section clarify\|followups\|traps\|reference\|all] [--problem ID]` | The interviewer's route to hidden notes for the current round (or a finished round of this session with `--problem`). `reference` also returns the oracle for live-coding problems. Hint and probe ladders are never returned here; use `hint`. Refused before `begin` in interview mode |
| `finish` | Stops the round, stores the result. More rounds: state `drawn`, `round` advances. Last round: state `finished` |
| `score --ratings FILE\|-` | Takes ratings JSON, computes scores, writes `scorecard`, appends to history, state `scored` |
| `abandon` | Ends the session, state `abandoned`, logged in history (no penalty) |
| `lint PATH... \| --all` | Validates pack files |
| `selftest [ID... \| --all] [--fuzz N] [--perf]` | Runs each oracle against its own tests |
| `history [--last N]` | Past sessions and per-tag averages |
| `repeat ID --reason TEXT [--days 3]` / `repeat --list` | Marks a problem to repeat (appends to `.mockinterview/repeat.md`: `DATE \| id \| reason \| repeat after DATE`), or lists the marks and which are due |
| `trust ROOT` | Acknowledges a non-built-in root |
| `estimate-check` | Design problems: checks `work/estimate.json` against the pack's reference estimate |
| `design-lint` | Design problems: structure check of `work/design.md` |

## run result

```json
{
  "ok": true, "problem": "lc-a01-two-sum", "passed": 17, "failed": 2, "total": 19,
  "by_category": {"visible": "3/3", "edge": "3/4", "hidden": "5/6", "fuzz": "6/6"},
  "perf": {"ran": true, "ok": true, "lines": ["n=20000 120 ms (limit 3000 ms) ok"]},
  "failures": [
    {"name": "edge-duplicates", "category": "edge", "shown": true,
     "args": "...", "expected": "...", "got": "..."}
  ],
  "details_policy": "interview: only visible failures are shown; practice: all, at most 3",
  "elapsed_seconds": 1184
}
```

In `interview` mode `failures[].shown` is `false` for `edge` and `hidden` cases and their `args`, `expected` and `got` are omitted; only the counts in `by_category` are visible. In `practice` mode, details are shown for up to three failing cases.

## Scoring

Ratings are 0 to 4. `score = sum(weight x rating / 4) - hint penalties`. Rung costs are 0, 5, 10 and 20 points for H0 to H3 (live coding) and for P0 to P3 (design). In live coding every rung used is deducted (cumulative); in system design only the highest probe step reached is deducted. For live coding the `implementation` rating is computed from the last run (4 x share of passing cases, perf and fuzz included); every other rating comes from the `ratings` file.

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
