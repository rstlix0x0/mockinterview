---
name: add-problem
description: Guide the engineer through writing a new mockinterview pack, a live-coding problem with tests and a reference solution, a system-design problem, or a knowledge document, then lint and self-test it. Use when the engineer wants to add, write, import or fix their own problem or study document, or a team wants custom content.
argument-hint: "[live-coding | system-design | knowledge] [title]"
---

# Pack author

You help the engineer write one pack file that the runner can draw, run and score. A pack is one Markdown file with frontmatter and fixed sections. The spec is `${CLAUDE_PLUGIN_ROOT}/docs/authoring.md`: read it with the Read tool before you draft anything, and follow it exactly. If it and this skill ever disagree, the spec wins.

## Calling the runner

Every action goes through the runner, with the Bash tool. Use exactly this prefix, then the command and its options:

```
python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" --data "${CLAUDE_PLUGIN_DATA}" COMMAND [options]
```

- Extra pack folder from the plugin options: `${user_config.packs_dir}`. If that is a real absolute path, add `--root "<that path>"` to every call. If it is empty or still looks like a placeholder, leave `--root` out.
- Every command prints one JSON object. Parse it. If `ok` is false, read `error` and `code` and fix the cause.
- Commands you use: `list`, `list --roots`, `lint`, `selftest`, `trust`.

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

- **Frontmatter**: all fields in the spec. `runs_code` must be `true`. `entry` is the function or class name; `kind` is `func` or `ops`.
- **`## Statement`**: the problem as an interviewer says it: description, a `Signature` line, `Constraints`, two or three `Examples` with input and output. Everything the engineer must see, nothing they must not.
- **`## Stub`**: one `python` fence: the function or class with the right signature, a docstring, and `pass`.
- **`## Tests`**: one `json tests` fence in the shape in the spec. Aim for at least 2 `visible` cases (the examples), 3 `edge` cases (empty, single, duplicates, limits) and 3 `hidden` cases (the traps), `fuzz` of 6 or more, and a `perf` block if the problem has a complexity target. Each case has exactly one tag. Expected values are not stored.
- **`## Oracle`**: one `python oracle` fence: a correct reference solution (`solve(**args)` for `func`; the class for `ops`), `gen_random(seed)` returning a small random `args`, and `gen_perf(n)` if `perf` exists. Keep the oracle simple and obviously right; speed matters less than clarity, except for the perf generator.
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

1. A pack outside the built-in root is untrusted until acknowledged. Explain in two sentences: "the oracle is Python that runs on your machine; you wrote it with me, so you can trust it, but a teammate's pack deserves a read first." Ask, then run `trust ROOT` with the root you chose.
2. Run `selftest ID`. It runs the oracle against its own tests. If something fails: a failing visible case usually means a wrong example in the statement; a failing hidden case usually means a wrong test; fix the pack, not the runner. Run it again until it ends with every case passing.
3. If the pack has a `perf` block, run `selftest ID --perf` once and check that the limits are realistic for a plain Python solution.
4. Optional but valuable: write a deliberately naive solution (the brute force) into `.mockinterview/work/solution.py` via `/mockinterview:practice` and confirm the right tests fail it: that proves the tests catch what they claim to catch.

## Step 5: finish

Tell the engineer, in a few lines: the file path, the id, that `list` shows it and that it can now be drawn in an interview for the levels they set (for packs with `level` lists), or picked in practice. If it is for a team, remind them to commit `.mockinterview/packs/`, and that `.mockinterview/work/` and `session.json` should not be committed (the plugin never edits `.gitignore`; suggest the line `.mockinterview/work/` and `.mockinterview/session.json`).

## Quality checklist (check before you say it is done)

- The statement can be solved without reading any hidden section.
- Examples in the statement are the `visible` cases and agree with the oracle.
- Hidden cases test something specific (an edge, a trap), not just bigger inputs.
- The hint ladder never contains code.
- The `source` field is honest.
- The id is unique and will not change later (history is keyed by it).
