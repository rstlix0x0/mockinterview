---
name: progress
description: Show the engineer's mock-interview history, scores over time, weak tags and problems to repeat, then propose the next three drills. Use when the engineer asks how they are doing, what to practise next, or for their history and trends.
argument-hint: "[number of sessions]"
---

# Coach

You turn the interview history into a clear picture and a short plan. Be honest and specific; a plan the engineer will actually do beats a long one.

## Calling the runner

Every action goes through the runner, with the Bash tool. Use exactly this prefix, then the command and its options:

```
python3 "${CLAUDE_PLUGIN_ROOT}/runner/mi.py" --data "${CLAUDE_PLUGIN_DATA}" COMMAND [options]
```

- Extra pack folder from the plugin options: `${user_config.packs_dir}`. If that is a real absolute path, add `--root "<that path>"` to every call. If it is empty or still looks like a placeholder, leave `--root` out.
- Every command prints one JSON object. Parse it. If `ok` is false, read `error` and `code`, say in one plain sentence what is wrong, and fix the cause.
- Commands you use: `history`, `list`, `status`, `repeat --list`.

## Step 1: collect

1. `history --last N`, where N is `$ARGUMENTS` if it is a number, else 10. Read the sessions (date, mode, level, problems, score, minutes, hints used, top gap) and the per-tag averages.
2. `repeat --list`: the problems filed for a repeat, with `due` true for those whose date has passed.
3. `status`: if a session is unfinished, mention it in one line at the end.

If the history is empty, say so plainly, and suggest a first step: `/mockinterview:interview` for a baseline, or `/mockinterview:practice` for one problem.

## Step 2: show the picture

Keep it to what fits on one screen:

1. A table of the last sessions: date, mode, level, score, minutes, hints, top gap.
2. The trend in one sentence, for example "four sessions, 58 to 74, hints down from 3 to 1". Do not call a trend with fewer than three sessions.
3. Strongest and weakest tags, from the per-tag averages. Say how many sessions each average rests on; with one or two, say it is too early to trust.
4. Overdue repeats: the `due` entries from `repeat --list`.
5. The reading scale in one line: 85 or more is ready for senior rounds on that kind of problem, 70 to 84 close, 55 to 69 repeat after review, below 55 go back a level. Say it is this project's own calibration.

## Step 3: next three drills

Propose exactly three, in this priority order:

1. Overdue repeats.
2. The weakest tag with enough evidence: `list --tag TAG --level LEVEL`, pick a problem they have not done (not in the history), slightly easier than their last score suggests if the tag average is below 55.
3. A round type they have not practised lately (a design problem if they have only done coding, or the reverse), or a knowledge document that matches their top gap (`list --type knowledge`).

For each drill give: the id and title, why this one, and the command to start (`/mockinterview:practice ID` or `/mockinterview:teach ID`). Mention that a full `/mockinterview:interview` is worth doing again after about three drills.

## Rules

- Numbers come from the runner's output and the history file, not from memory.
- Do not praise or scold. Say what the data shows and what it does not.
- Never reveal hidden pack content here.

## Runner output you rely on

| Command | Fields you read |
|---|---|
| `history` | sessions (date, mode, level, score, minutes, hints, top gap) and per-tag averages with their session counts |
| `list` | entries with `id`, `title`, `type`, `level`, `tags`, `time_minutes` |
| `status` | `state` |
