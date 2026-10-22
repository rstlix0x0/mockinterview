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

## Running pack code

A session never runs pack code: the engineer's solution runs in their own toolchain, and the expected values are stored in the pack. Only `selftest` runs a pack's reference solution (Python), when an author asks for it. Read a teammate's pack before you run its `selftest`.

## Frontmatter

```yaml
---
id: lc-c01-lru-cache        # unique, stable forever, [a-z0-9-], start with lc- sd- or kb-
title: LRU Cache
type: live-coding           # live-coding | system-design | knowledge
level: [mid, senior]        # junior | mid | senior | staff
tags: [design, hash-map, linked-list]
time_minutes: 30
entry: LRUCache             # live-coding: function or class the tests call (snake_case functions)
kind: ops                   # live-coding: func (one function call) | ops (class, list of method calls)
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
| live-coding | `## Signature` | Engineer and agent | One fenced `signature` block: the language-neutral types of the inputs and outputs (see below). The agent writes the engineer's stub and test file from it, in their language |
| live-coding | `## Tests` | Hidden | One fenced `json tests` block with expected values (see below) |
| live-coding | `## Reference solution` | Hidden | One fenced `python reference` block: a correct, self-contained solution (see below) |
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
{"function":"two_sum","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[2,7,11,15],"target":9},"expected":[0,1]},
{"name":"edge-duplicates","tags":["edge"],"args":{"nums":[3,3],"target":6},"expected":[0,1]},
{"name":"hidden-large-values","tags":["hidden"],"args":{"nums":[1000000000,-1000000000,5],"target":0},"expected":[0,1]}
]}
```

- `function` is the entry the tests call (a function, or a class for `kind: ops`). It must equal `entry` in the frontmatter. The agent renames it to the engineer's language convention (`twoSum`).
- `kind: func` calls `function(args...)`; the `args` keys must be exactly the signature's parameters. `kind: ops` builds the class, then calls methods; `args` is `{"calls": [["ClassName", [ctor args]], ["method", [args]], ...]}` and `expected` is the list of return values, one per call (`null` for the constructor and for methods that return nothing).
- `compare` is `exact` or `approx` (relative tolerance 1e-4 for numbers).
- Each case has exactly one tag from `visible` (the examples; the engineer sees them), `edge` and `hidden` (counted but not shown during an interview). Name cases so a failing test name says something (`edge-duplicates`).
- Each case has an `expected` value. Write the cases without it, then `selftest ID --write-expected` fills it in from the reference solution. Keep cases small: there is no timing test, so a big input adds nothing; complexity is judged in the conversation (`Target complexity` in the notes).
- One case per line keeps diffs readable; `--write-expected` writes that layout.

## Signature block

The types of the entry's inputs and outputs, with the pack's (Python) names: one line for a `func` pack, and for an `ops` pack the constructor (no return type) followed by one line per method. Lines starting with `#` are comments.

````markdown
```signature
two_sum(nums: int[], target: int) -> int[]
```

```signature
LRUCache(capacity: int)
get(key: int) -> int
put(key: int, value: int) -> void
```
````

| Type | Meaning |
|---|---|
| `int`, `float`, `bool`, `string` | `int` is a signed 64-bit integer; `float` also accepts integers |
| `T[]` | list |
| `T?` | `T` or `null` (`int?[]` is a list of nullable ints, `int[]?` a nullable list) |
| `[A, B]` | tuple: a list of exactly these types, two or more |
| `{string: T}` | object used as a map |
| `record{a: T, b?: U}` | object with exactly these keys; `b?` may be absent (not `null` unless `U` is nullable) |
| `A \| B` | either; group with parentheses: `(int \| string)[]`. Awkward in typed languages; avoid it where one type works |
| `void` | a method's return type when it returns nothing |

`lint` checks that each line has the shape `name(param: type, ...) -> type`, that the first line declares the entry, and that each case's `args` are the first line's parameters. The types are documentation for the agent and the engineer; prefer the type the tests really use (`string` keys rather than `int | string`).

## Reference solution block

Self-contained Python with its own imports:

- `kind: func`: define `solve(...)` with the signature's parameter names.
- `kind: ops`: define the class named `function`.

It is the source of the expected values (`selftest --write-expected`), and the solution the Teacher walks through after an attempt (translated into the engineer's language when needed). Keep it simple and obviously right.

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
python3 runner/mi.py lint path/to/pack.md                      # structure, JSON, headings
python3 runner/mi.py selftest lc-your-id --write-expected      # fill in expected values from the reference
python3 runner/mi.py selftest lc-your-id                       # stored values agree with the reference
python3 runner/mi.py list --roots                              # roots and overrides
```

Run `selftest` before sharing a pack: it proves the stored expected values agree with the reference solution.
