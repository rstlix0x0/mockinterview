# Solution languages

> **Status: planned, not implemented.** This is the agreed design for running solutions in languages other than Python. Until it lands, [runner.md](runner.md) describes what exists: Python only.

Other languages are for the **candidate's solution only**. The plugin itself (runner, oracles, expected values, scoring, tools) stays Python, standard library only. The one non-Python piece per language is a small **shim** that loads the solution and calls it inside the test subprocess.

```
┌──────────────── plugin: Python ─────────────────────┐
│ runner/mi.py · lib/*.py · oracle · scoring · tools  │
│ reads languages/*.toml (data, not code)             │
└───────────────┬─────────────────────────────────────┘
                │ subprocess per test case, JSON request on stdin
┌───────────────▼─── candidate side: chosen language ─┐
│ shim / generated glue ──calls──▶ the solution       │
│ writes the JSON result to {result}                  │
└─────────────────────────────────────────────────────┘
```

Pack authors keep writing oracles in Python, so one pack serves every language.

## Decisions

| # | Decision | Reason |
|---|---|---|
| A | One TOML file per language; the runner's minimum Python becomes **3.11** | `tomllib` is standard library from 3.11; TOML allows comments. Python 3.10 reached end of life in October 2026 |
| B | The shim writes its result to a file (`{result}`), not to stdout | A `print()` left in a solution no longer breaks the JSON parse; stdout and stderr stay the engineer's |
| C | One process per test case; an optional `batch = true` mode may come later | Clean per-case timeouts and limits. None of the first four languages has a startup cost that needs batching |
| D | Each language uses its standard toolchain from `PATH`; the runner never installs or downloads | Offline, no surprises. The engineer installs dependencies |
| E | `work/` is a normal project for the language (`go.mod`, `Cargo.toml`, optional `package.json`) | Editors (gopls, rust-analyzer) need the manifest; engineers know the layout |
| F | Third-party dependencies: allowed in practice and teach, **refused in interview mode** | Real interview rounds use the standard library; a package that solves the problem leaves nothing to score |

## First languages

| Language | Toolchain | Build | Minimum |
|---|---|---|---|
| Python | the runner's own interpreter | none | 3.11 |
| JavaScript | `bun`, else `node` (first found; `--runtime` to choose) | none | Node 18, Bun 1.0 |
| Go | `go` | `go build` in `work/`, `GOPROXY=off` | 1.21 |
| Rust | `cargo` | `cargo build --release --offline` | 1.70 |

Compiled languages build once per `run`, cached by a hash of the sources in `.mockinterview/build/`, not once per case.

## Language files

Discovered from the same roots as packs, under `languages/`. A later root wins on the same `id`, so a user file can replace a built-in one (for example to point at a specific `go`). Files outside the built-in root run commands, so they need `mi.py trust` like packs.

```
<plugin>/languages/python.toml           built-in, trusted
<plugin>/runner/shims/js_shim.js
~/.mockinterview/languages/*.toml         user     ┐ need `mi.py trust`
<project>/.mockinterview/languages/       project  ┘
```

| Field | Required | Example | Purpose |
|---|---|---|---|
| `id`, `name` | yes | `"go"`, `"Go 1.21+"` | Key and display name |
| `solution` | yes | `"solution.go"` | The file the engineer edits, relative to `work/` |
| `detect` | yes | `["go", "version"]` | Is the toolchain installed; its output is reported |
| `run` | yes | `["{bin}"]` | Runs one test case |
| `build` | no | `["go", "build", "-o", "{bin}", "."]` | Runs once per `run` |
| `shim` | no | `"shims/js_shim.js"` | Fixed adapter (dynamic languages) |
| `glue` | no | `"glue/go"` | Template for generated glue (typed languages) |
| `scaffold` | no | `{ "go.mod" = "module solution\n\ngo 1.21\n" }` | Extra files written on `begin` if absent |
| `stub_func`, `stub_ops` | yes | template text | Stubs for function and class problems |
| `naming` | no | `"camel"` | `two_sum` → `twoSum` (`snake` by default) |
| `time_factor` | no | `1.5` | Multiplies timeouts and perf limits |
| `env_pass` | no | `["GOPATH", "GOMODCACHE"]` | Extra environment variables passed through |
| `env` | no | `{ GOPROXY = "off" }` | Variables set for build and run |
| `runtimes` | no | `[{ id = "bun", detect = [...], run = [...] }, ...]` | Alternatives, first found wins |
| `deps_check` | no | `"cargo"` | Which manifest check interview mode runs |

Placeholders: `{python} {shim} {solution} {work} {build} {bin} {result} {entry} {params}`.

Python becomes an ordinary language file:

```toml
id       = "python"
name     = "Python 3.11+"
solution = "solution.py"
shim     = "shims/py_shim.py"
detect   = ["{python}", "--version"]
run      = ["{python}", "{shim}", "{solution}", "{result}"]
stub_func = "def {entry}({params}):\n    raise NotImplementedError\n"
```

## Lifecycle

```
pick/draw --lang go
   ├─ detect ──✗──▶ {"ok": false, "code": "toolchain_missing"}
   ▼
begin ─▶ write the stub and scaffold into work/      (session.json records language and solution)
   ▼
run ─▶ interview mode? dependency check ──✗──▶ {"ok": false, "code": "dependencies_not_allowed"}
   ─▶ build if needed (cached by source hash)
   ─▶ per case: run ─stdin {"function", "args" | "calls"}─▶ shim/glue ─▶ solution
                     ◀── result JSON in {result} ─────────────┘
   ─▶ oracle (Python) computes the expected value, compares, scores
```

## work/ layout

```
Python   solution.py
JS       solution.js  [package.json, node_modules/]        engineer runs npm/bun install
Go       go.mod · solution.go · mi_main.go                  engineer runs go get
Rust     Cargo.toml · src/solution.rs · src/main.rs         engineer runs cargo add
                                     └─ runner-owned glue, rewritten on every run
```

The Rust glue carries its own small JSON parser, so a project without dependencies builds offline on the first try. Go uses `encoding/json`.

## Dependencies in interview mode

A cheap check before `run`, friction in the same spirit as the mod's guard, not a sandbox:

| Language | Check |
|---|---|
| Python | every import of the solution is in `sys.stdlib_module_names` |
| JavaScript | `package.json` has no `dependencies`; every `require`/`import` is a `node:` builtin |
| Go | `go.mod` has no `require` |
| Rust | `Cargo.toml` `[dependencies]` is empty |

On failure: `{"ok": false, "code": "dependencies_not_allowed", "error": "interview rounds use the standard library only: found 'lru'"}`.

## Signatures (typed languages)

Go and Rust cannot call a function by name at run time, so they need glue generated for each problem from a strict signature. Each live-coding pack gains a `## Signature` section; lint checks its grammar and `selftest` checks that the oracle's real inputs and outputs conform.

```
int · float · bool · string · T[] · T? (nullable) · [A, B] (tuple) · {string: T} (map) · record{a: T, ...}
```

| Type | Go | Rust | JavaScript |
|---|---|---|---|
| `int` | `int` | `i64` | `number` (exact to 2^53) |
| `string` | `string` | `String` | `string` |
| `T[]` | `[]T` (a nil slice is written as `[]`) | `Vec<T>` | `Array` |
| `T?` | `*T` | `Option<T>` | `T \| null` |
| `[A, B]` | generated struct, encoded as an array | `(A, B)` | `Array` |
| `{string: T}` | `map[string]T` | `HashMap<String, T>` | `Object` |

Today the types live only in the Python stub docstrings: about 47 packs are clean and about 10 are loose or untyped (`lc-c02`, `lc-c03`, `lc-c07`, `lc-c08`, `lc-c11`, `object` returns, unions such as `int | 'ERROR'`). A pack whose signature does not map to a language is offered in Python and JavaScript only; `draw --lang go` skips it.

## Commands and session

| Change | Detail |
|---|---|
| `mi.py langs` | Lists languages, the toolchain found and its version |
| `pick`, `draw` | `--lang ID` (and `--runtime ID`); default from a new `default_language` plugin option, else `python` |
| `session.json` | Adds `language` and `solution`; skills, the scorer and the mod read the file name from here instead of assuming `solution.py` |

## Phases

| Phase | Scope |
|---|---|
| P1 Foundation | Python 3.11 floor, TOML loader, `langs`, `--lang`, session fields, result file (B), `python.toml` with no behaviour change, dependency check for Python; skills, scorer, mod and docs follow the session's solution file |
| P2 JavaScript | One shim for Bun and Node, camelCase stubs, `package.json` dependency check. All live-coding packs work: no types needed |
| P3 Signatures | `## Signature` in every live-coding pack (converted from the docstrings by script, the loose ones by hand); lint and selftest checks; authoring.md updated |
| P4 Go and Rust | Type mapping, generated glue, scaffold, cached builds, manifest checks, the language filter in `draw` |

Each phase ends with the runner tests, mod tests, `lint --all` and `selftest --all` passing, and its docs updated.
