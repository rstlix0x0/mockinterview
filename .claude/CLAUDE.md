# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Claude Code **plugin** (`mockinterview`) for practising software-engineering interviews: skills act as Interviewer/Teacher personas, a Python runner owns all state (sessions, problem selection, test results, scoring), content lives in Markdown "packs" (the problem bank), and an optional early-access **mod** (TypeScript) draws a pane, timer and spoiler guard. The engineer solves in any language with their own toolchain; the agent writes the tests from the pack's cases and runs them.

## Commands

All run from the repository root. The runner is Python 3.11+, standard library only (no install step).

```bash
python3 -m unittest discover -s tests -v                      # runner tests
python3 -m unittest tests.test_runner.RunnerTest.test_lint_and_selftest_pass   # one test
python3 runner/mi.py lint --all                               # structural check of every pack
python3 runner/mi.py selftest --all                           # stored expected values agree with each reference solution
python3 runner/mi.py selftest lc-a01-two-sum --write-expected # one pack; fill expected values from its reference
python3 runner/mi.py lint path/to/pack.md
claude plugin validate                                        # manifest + layout
claude plugin test .                                          # mod tests (tests/mod/*.test.ts)
```

`mi.py` refuses Python < 3.11 (`code: python_version`), and the tests then fail on every call. If the `python3` on PATH is older, use e.g. `uv run --no-project --python 3.12 python -m unittest discover -s tests`. The tests launch `mi.py` with the same interpreter that runs them.

Set `MI_DEBUG=1` to get a traceback in the JSON output on internal errors. Load the plugin live with `claude --plugin-dir .` and `/reload-plugins` while iterating.

## Architecture

```
skills/*/SKILL.md ──Bash──▶ runner/mi.py ──writes──▶ <project>/.mockinterview/session.json
agents/scorer.md  ──Bash──▶   (notes only)          <project>/.mockinterview/work/{PROBLEM.md, design.md}
                              │ reads                <data>/history.jsonl
                              ▼
                    content/ + user/project/option pack roots
hooks/register.tsx (mod) ──reads only──▶ session.json, work/PROBLEM.md

live coding:  tests ──▶ agent writes stub + native test file in work/ ──▶ agent runs the engineer's
              test command (go test, cargo test, pytest ...) ──▶ record --failed NAMES ──▶ last_run
```

- **The runner is the single source of truth.** Only `mi.py` writes `session.json`. Skills call it through Bash with the prefix `python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" --data "${CLAUDE_PLUGIN_DATA}" ...`. The mod never writes, never runs the runner and registers no tools (`$.process` is CLI only), so the plugin must keep working with the mod absent.
- **Runner contract** (`docs/runner.md`): every command prints exactly one JSON object (`{"ok": true, ...}` / `{"ok": false, "error", "code"}`); exit 0 ok, 1 user/state error or failing pack, 2 internal. Changing output shape affects the skills, the scorer agent and the mod's parser (`hooks/lib/session.ts`) — keep them in sync.
- **Runner layout**: `mi.py` is argparse only; command implementations live in `runner/lib/commands.py`; pack parsing/discovery/lint in `packs.py`; `selftest` and value comparison in `reference.py` (the only code that executes pack Python, and only on an author's request); selection in `draw.py`; scoring maths in `score.py`; `tools/` holds standalone scripts (`designlint.py`, `estimate.py`, `sim_*.py`).
- **Languages**: free text. `draw`/`pick --lang TEXT --test-cmd TEXT` store `language` and `test_command` in `session.json`; the runner never runs them. The skills (`skills/interview/rounds.md`, "Live-coding round") tell the agent how to scaffold the stub and test file, run the command and call `record`. 0.3.0 had a per-language runner (generated Go/Rust glue, `## Signature` grammar); it was removed in 0.4.0 (commit `f5e3e7d` is the last 0.3.0 state).
- **Test results**: `tests [--all]` hands the agent cases with stored `expected` values; `record --mode visible|all --failed NAMES [--got NAME=VALUE] [--error TEXT]` turns failing case names into `last_run` (counts by category, details for shown failures). In interview mode only visible failures carry details.
- **Session state machine**: `drawn → running → (drawn for next round | finished) → scored`, or `abandoned`. In interview mode, titles/statements are withheld until `begin`, and `show`, `show --full` and `notes` are refused accordingly; hidden material reaches the interviewer only via `notes`, `hint` and `tests --all`. `begin` moves the previous round's `work/` files into `work/archive/<time>/`.
- **Scoring**: `implementation` is computed from the last `record`; all other dimensions come from the scorer subagent's ratings JSON passed to `mi.py score`. Dimension keys and weights are fixed (see `docs/runner.md`). There is no timing test: complexity is judged under `approach`.
- **Mod** (`hooks/`): `register.tsx` polls the session file and renders panes; `lib/guard.ts` denies reads of pack files during an active interview round (friction, not security); `lib/format.ts` builds pane blocks; `lib/library.ts` backs the Library tab (a TS port of the runner's frontmatter parser — keep it in step with `parse_frontmatter` in `runner/lib/packs.py`). Library buttons only `$.prompt.fill` a skill command. Tests use `claude-code/testing`. `claude plugin validate` requires `$` to flow only into top-level functions of the module.

## Packs (content)

One Markdown file per problem: frontmatter (small YAML subset parsed by the runner, not a full YAML parser) plus `##` sections. Format in `docs/authoring.md`. Key invariants enforced by `lint`:

- `id` is stable forever, prefixed `lc-`/`sd-`/`kb-`; `entry` must equal the tests block's `function`.
- Live-coding: `## Statement`, `## Signature` (language-neutral types; the first line declares `entry` and its params are the cases' `args` keys), `## Tests` (one ` ```json tests ` block, each case tagged exactly one of `visible|edge|hidden` and carrying `expected`), `## Reference solution` (one ` ```python reference ` block, self-contained, defining `solve`/the class), `## Interviewer notes`.
- Hint/probe ladder lines must keep the exact shape `- H0 (free): ...`, `- H1 (-5): ...` (or `P0`–`P3` for design) so `mi.py hint` can parse them.
- After editing a pack, run `lint` and `selftest` on it. `content/README.md` holds the pack index and counts — update it when adding packs.
- Runner tests use the fixture packs in `tests/fixtures/content/` as the built-in content, with temp project/data/home dirs.

## Docs

`docs/runner.md` and `docs/authoring.md` describe what exists. `docs/design.md` predates the code; its section 0 lists where the implementation differs — trust runner.md/authoring.md over design.md.
