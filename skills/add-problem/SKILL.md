---
name: add-problem
description: Guide the engineer through writing a new mockinterview pack, a live-coding problem with tests and a reference solution, a system-design problem, or a knowledge document, then lint and self-test it. Use when the engineer wants to add, write, import or fix their own problem or study document, or a team wants custom content.
argument-hint: "[live-coding | system-design | knowledge] [title]"
---

# Pack author

You help the engineer write one pack file that the runner can draw and score, and the interviewer can test in any language. A pack is one Markdown file with frontmatter and fixed sections. The spec is `${CLAUDE_PLUGIN_ROOT}/docs/authoring.md`: read it with the Read tool before you draft anything, and follow it exactly. If it and this skill ever disagree, the spec wins.

## Calling the runner

Every action goes through the runner, with the Bash tool. Use exactly this prefix, then the command and its options:

```
python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" --data "${CLAUDE_PLUGIN_DATA}" COMMAND [options]
```

- Extra pack folder from the plugin options: `${user_config.packs_dir}`. If that is a real absolute path, add `--root "<that path>"` to every call. If it is empty or still looks like a placeholder, leave `--root` out.
- Every command prints one JSON object. Parse it. If `ok` is false, read `error` and `code` and fix the cause.
- Commands you use: `list`, `list --roots`, `lint`, `selftest`.

## Step 1: what and where

Ask, in one short message (use the arguments if they gave any):

1. **Type**: live-coding, system-design, or knowledge.
2. **Title, levels** (junior, mid, senior, staff; one or more), **tags**, **time in minutes**, and **source**: `original`, `adapted` or `third-party`. If it comes from a company or a platform, ask them to describe the pattern in their own words; do not copy someone else's text into a pack, and never include a company's real interview questions.
3. **Where to save it**: run `list --roots` and show the roots.

| Root | Path | Use it for |
|---|---|---|
| User | `~/.mockinterview/packs/` | Your own problems, in every project |
| Project | `<project>/.mockinterview/packs/` | A team's problems, committed with the repository |
| Option | the `packs_dir` plugin option, if set | Any other folder |
| Built-in | the plugin's `content/` folder | Only when you are contributing to the plugin repository itself |

Create the folder if it does not exist. Default to the user root unless the engineer says it is for a team.

Choose an id: `lc-` or `sd-` or `kb-` plus a short kebab-case name. Run `list` and check that the id is not taken. An existing id in an earlier root will be overridden by the new pack; tell them if that is what they want.

## Step 2: draft by type

Write the whole file with the Write tool, then show them a short summary (not the full file) and ask if anything should change.

### Live coding

- **Frontmatter**: all fields in the spec. `entry` is the function or class name (snake_case for functions); `kind` is `func` or `ops`.
- **`## Statement`**: the problem as an interviewer says it: description, a `Signature` line, `Constraints`, two or three `Examples` with input and output. Everything the engineer must see, nothing they must not.
- **`## Signature`**: one `signature` fence with the language-neutral types of the inputs and outputs: `name(param: type, ...) -> type` for `func`; for `ops` the constructor line `ClassName(param: type)` then one line per method (`-> void` when it returns nothing). Types: `int`, `float`, `bool`, `string`, `T[]`, `T?`, `[A, B]`, `{string: T}`, `record{a: T, b?: U}`, `A | B` (notation in the authoring spec). The interviewer writes each engineer's stub from it, so use the types the tests really use and avoid `|` where a single type works.
- **`## Tests`**: one `json tests` fence in the shape in the spec. Aim for at least 2 `visible` cases (the examples), 3 `edge` cases (empty, single, duplicates, limits) and 4 or more `hidden` cases (the traps, plus a few random small inputs). Each case has exactly one tag and an `expected` value; leave `expected` out while drafting, `selftest --write-expected` fills it in from the reference solution.
- **`## Reference solution`**: one `python reference` fence: a correct, self-contained solution (`solve(**args)` for `func`; the class for `ops`) with its own imports. Keep it simple and obviously right; it is what teach mode and the debrief walk through, and what the expected values come from.
- **`## Interviewer notes`**: use these `###` headings so the runner can slice them: `### Clarifying questions` (question and answer pairs), `### Hint ladder` (lines in the exact shape `- H0 (free): ...`, `- H1 (-5): ...`, `- H2 (-10): ...`, `- H3 (-20): ...`), `### Follow-ups`, `### Traps` (the mistakes the tests are built to catch).

### System design

- **`## Statement`**: the prompt, with tier, time and topics, then the one-paragraph request.
- **`## Self-check questions`**: five questions to answer after the session.
- **`## Interviewer notes`** with these `###` headings: `### Clarifying questions` (a table of question and answer), `### Reference design` (a short written design and a Mermaid diagram), `### Deep dives` (each with what a strong answer contains), `### Curveballs and failure injections`, `### Common mistakes`, `### Level calibration`, `### Probe ladder` (lines `- P0 (free): ...`, `- P1 (-5): ...`, `- P2 (-10): ...`, `- P3 (-20): ...`).
- **`## Reference estimate`**: one `json estimate` fence with the assumptions (`dau`, `writes_per_user_day`, `reads_per_user_day`, `bytes_per_write`, `bytes_per_read`, `peak_factor`, `retention_years`, `replication`, `server_qps`). Check the arithmetic yourself with the estimator in the runner's `tools/` folder (replace `mi.py` in the runner path by `tools/estimate.py`, command `calc`) and show them the numbers.

### Knowledge

Frontmatter with `type: knowledge`, then plain study material: short sections, examples, a Mermaid diagram where it helps, and a short "check yourself" list at the end. No tests, no hidden sections. Cite real sources with links you have opened.

## Step 3: lint

Run `lint PATH` with the path of the new file. Fix every error, then run it again until it passes. Warnings: fix them or tell the engineer why you left them.

## Step 4: self-test (live coding only)

`selftest` runs the reference solution (Python, on this machine) against the stored expected values. It is the only time pack code runs; a session never runs it. A teammate's pack deserves a read before you run its selftest.

1. Run `selftest ID --write-expected`. It sets every case's `expected` from the reference solution and rewrites the tests block.
2. Check the visible cases against the examples in the statement by eye: they must agree. A disagreement means a wrong example or a wrong reference; fix the pack, then run step 1 again.
3. Run `selftest ID` and confirm every case passes.
4. Optional but valuable: run `/mockinterview:practice ID`, write a deliberately naive solution (the brute force) and confirm the right tests fail it: that proves the tests catch what they claim to catch.

## Step 5: finish

Tell the engineer, in a few lines: the file path, the id, that `list` shows it and that it can now be drawn in an interview for the levels they set (for packs with `level` lists), or picked in practice. If it is for a team, remind them to commit `.mockinterview/packs/`, and that `.mockinterview/work/` and `session.json` should not be committed (the plugin never edits `.gitignore`; suggest the line `.mockinterview/work/` and `.mockinterview/session.json`).

## Quality checklist (check before you say it is done)

- The statement can be solved without reading any hidden section.
- Examples in the statement are the `visible` cases and agree with the reference solution.
- Hidden cases test something specific (an edge, a trap), not just bigger inputs. Keep each case small enough to read: there is no timing test, so a large input adds nothing.
- The hint ladder never contains code.
- The `source` field is honest.
- The id is unique and will not change later (history is keyed by it).
