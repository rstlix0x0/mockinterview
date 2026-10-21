# Authoring packs

A **pack** is one Markdown file that describes one problem or one knowledge document. Anyone can add packs; no plugin code needs to change. Run `/mockinterview:add-problem` to be guided, or write the file by hand and check it with `python3 runner/mi.py lint FILE`.

## Where packs live

| Root | Path | When to use |
|---|---|---|
| Built-in | `content/` inside the plugin | Ships with the plugin |
| User | `~/.mockinterview/packs/` | Your own problems, available in every project |
| Project | `<project>/.mockinterview/packs/` | A team's problems, committed with the repository |
| Option | the `packs_dir` plugin option | Any other folder |

Each root is scanned recursively for `*.md` files. If two packs have the same `id`, the later root in the order above wins, and `mi.py list` reports the override. The user, project and option roots are **optional**; they exist only if you create them.

## Trust

A pack with `runs_code: true` contains Python (an oracle) that the runner executes on your machine. Packs from the built-in root are trusted. Packs from any other root are refused until you run `python3 runner/mi.py trust ROOT`. Treat a teammate's pack like a teammate's script: read it first.

## Frontmatter

```yaml
---
id: lc-c01-lru-cache        # unique, stable forever, [a-z0-9-], start with lc- sd- or kb-
title: LRU Cache
type: live-coding           # live-coding | system-design | knowledge
level: [mid, senior]        # junior | mid | senior | staff
tags: [design, hash-map, linked-list]
time_minutes: 30
languages: [python]         # live-coding only
entry: LRUCache             # live-coding: function or class the tests call
kind: ops                   # live-coding: func (one function call) | ops (class, list of method calls)
runs_code: true             # live-coding: must be true
source: adapted             # original | adapted | third-party
author: mockinterview
legacy_id: C1               # optional
---
```

Frontmatter is a small YAML subset: `key: value`, lists as `[a, b]`, booleans, integers, and `#` comments.

## Sections

Sections are level-2 headings (`## Name`). Names are case-insensitive. Headings inside code fences are ignored.

| Type | Section | Audience | Content |
|---|---|---|---|
| live-coding | `## Statement` | Engineer | The whole problem as the interviewer says it: description, signature, constraints, examples |
| live-coding | `## Stub` | Engineer | One fenced `python` block copied to `work/solution.py` at the start |
| live-coding | `## Tests` | Hidden | One fenced `json tests` block (see below) |
| live-coding | `## Oracle` | Hidden | One fenced `python oracle` block: the reference solution and generators |
| live-coding | `## Interviewer notes` | Hidden | Clarifying questions, hint ladder, follow-ups, traps |
| system-design | `## Statement` | Engineer | The prompt, with tier, time and topics |
| system-design | `## Self-check questions` | Engineer, after the session | Questions to answer afterwards |
| system-design | `## Interviewer notes` | Hidden | Clarifying answers, reference design, probes, failure injections, calibration, probe ladder |
| system-design | `## Reference estimate` | Hidden | One fenced `json estimate` block |
| knowledge | any | Engineer | Study material; no required sections |

"Hidden" sections are never printed by `mi.py show` during an interview round, and the mod's guard refuses to read pack files during an interview. This is friction against accidents, not security.

## Live-coding tests block

The `json tests` block is one JSON object:

```json
{"function": "two_sum", "kind": "func", "compare": "exact", "fuzz": 6,
 "perf": {"sizes": [20000, 100000, 200000], "limit_ms": 3000, "max_exponent": 1.4},
 "cases": [
   {"name": "example-1", "tags": ["visible"], "args": {"nums": [2, 7, 11, 15], "target": 9}},
   {"name": "edge-duplicates", "tags": ["edge"], "args": {"nums": [3, 3], "target": 6}},
   {"name": "hidden-large-values", "tags": ["hidden"], "args": {"nums": [1000000000, -1000000000, 5], "target": 0}}
 ]}
```

- `function` is the name the solution file must define (a function, or a class for `kind: ops`). It must equal `entry` in the frontmatter.
- `kind: func` calls `function(**args)`. `kind: ops` builds the class, then calls methods; `args` is `{"calls": [["ClassName", [ctor args]], ["method", [args]], ...]}` and the result is the list of return values (`null` for the constructor).
- `compare` is `exact` or `approx` (relative tolerance 1e-4 for numbers).
- Each case has exactly one tag from `visible`, `edge`, `hidden`. Expected values are **not** stored: they are computed by the oracle.
- `fuzz` is the number of random cases for the fuzz category; `perf` describes scaling checks (optional).

## Oracle block

Python that runs with `random`, `re`, `heapq`, `bisect`, `math`, `itertools`, `defaultdict`, `deque`, `Counter`, `OrderedDict`, `Fraction` and `rand_ops` already in scope.

- `kind: func`: define `solve(**args)` with the same parameter names as the tests.
- `kind: ops`: define the class named `function`.
- Define `gen_random(seed)` returning an `args` dict (used by fuzz) and, if `perf` exists, `gen_perf(n)`.

The oracle is also the reference solution the Teacher may show after an attempt.

## Hint ladder

Inside `## Interviewer notes` keep these exact line shapes so `mi.py hint` can read them:

```text
- H0 (free): a question that points at the gap
- H1 (-5): name the technique or the invariant
- H2 (-10): state the key idea
- H3 (-20): outline the algorithm in words, never code
```

System-design packs use `P0` to `P3` in the same shape. Rungs are given in order and each use costs the listed points.

## Check your pack

```bash
python3 runner/mi.py lint path/to/pack.md      # structure, JSON, headings
python3 runner/mi.py selftest lc-your-id       # the oracle must pass its own tests
python3 runner/mi.py list --roots              # roots, trust status, overrides
```

Run `selftest` before sharing a pack: it proves the oracle passes its own tests.
