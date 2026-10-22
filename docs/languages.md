# Solution languages

> **Status: P1 (foundation), P2 (JavaScript) and P3 (signatures) are implemented; Go and Rust are planned.** Language files, `langs`, `--lang`, the session fields, the result file and the dependency checks exist today, with Python and JavaScript built in. Fields and placeholders marked *planned* are refused by the loader until their phase lands.

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
<plugin>/languages/javascript.toml       built-in, trusted
<plugin>/languages/shims/                py_shim.py, js_shim.mjs: shims sit beside the language files
~/.mockinterview/languages/*.toml         user     ┐ need `mi.py trust <folder>`
<project>/.mockinterview/languages/       project  ┘
```

A file that does not load (bad TOML, a missing or unknown field, an unknown placeholder) is skipped and reported in the `warnings` of `mi.py langs`.

| Field | Required | Example | Purpose |
|---|---|---|---|
| `id`, `name` | yes | `"go"`, `"Go 1.21+"` | Key and display name |
| `solution` | yes | `"solution.go"` | The file the engineer edits, relative to `work/` |
| `detect` | unless `runtimes` | `["go", "version"]` | Is the toolchain installed; the first line of its output is reported as the version |
| `run` | unless `runtimes` | `["{python}", "{shim}", "{solution}", "{result}"]` | Runs one test case |
| `shim` | no | `"shims/js_shim.js"` | Fixed adapter (dynamic languages), relative to the language file |
| `pack_stub` | no | `true` | Write the pack's `## Stub` (Python) as it is; only for Python-compatible languages |
| `stub_func`, `stub_ops` | unless `pack_stub` | `"def {entry}({params}):\n    pass\n"` | Stubs for function and class problems |
| `stub_method` | if `stub_ops` has `{methods}` | `"\n  {name}({params}) {\n  }\n"` | One method of a class stub, repeated for each method of the pack's stub |
| `naming` | no | `"camel"` | `two_sum` → `twoSum` for functions, methods and parameters; class names stay (`snake`, the default, keeps every name) |
| `call` | no | `"positional"` | How a function gets its arguments: `named` (the default; by the stub's parameter names) or `positional` (in the stub's order) |
| `time_factor` | no | `1.5` | Multiplies timeouts and perf limits |
| `env_pass` | no | `["GOPATH", "GOMODCACHE"]` | Extra environment variables passed through |
| `env` | no | `{ GOPROXY = "off" }` | Variables set for build and run |
| `runtimes` | no | `[{ id = "bun", detect = [...], run = [...] }, ...]` | Alternatives, first found wins; each replaces `detect` and `run` |
| `deps_check` | no | `"npm"` | Which check interview mode runs: `python` or `npm` today, `go` and `cargo` planned |
| `build` | *planned* (P4) | `["go", "build", "-o", "{bin}", "."]` | Runs once per `run` |
| `glue` | *planned* (P4) | `"glue/go"` | Template for generated glue (typed languages) |
| `scaffold` | *planned* (P4) | `{ "go.mod" = "module solution\n\ngo 1.21\n" }` | Extra files written on `begin` if absent |

Placeholders in `detect` and `run`: `{python}` (the runner's interpreter), `{shim}`, `{solution}`, `{work}`, `{result}`; *planned*: `{build}`, `{bin}`. In `stub_func` and `stub_ops`: `{entry}` (the pack's function or class), `{params}` (the parameter names of the pack's Python stub; for a class, its constructor's) and `{methods}` (the class's methods, each rendered with `stub_method`, whose placeholders are `{name}` and `{params}`). Names are spelled per `naming`. Other text in braces, such as a code block `{ }`, is left alone.

Python becomes an ordinary language file:

```toml
id         = "python"
name       = "Python 3.11+"
solution   = "solution.py"
shim       = "shims/py_shim.py"
pack_stub  = true                     # the pack's ## Stub section is already Python
detect     = ["{python}", "--version"]
run        = ["{python}", "{shim}", "{solution}", "{result}"]
env        = { PYTHONDONTWRITEBYTECODE = "1" }
deps_check = "python"
```

JavaScript is a built-in file too, with two runtimes:

```toml
id          = "javascript"
name        = "JavaScript (Bun or Node 18+)"
solution    = "solution.js"
shim        = "shims/js_shim.mjs"
naming      = "camel"                 # two_sum -> twoSum, get_min -> getMin
call        = "positional"            # arguments in the order of the pack's stub
deps_check  = "npm"
stub_func   = ...                     # function, then module.exports = { name }
stub_ops    = ...                     # class with constructor and {methods}
stub_method = ...

[[runtimes]]
id     = "bun"
detect = ["bun", "--version"]
run    = ["bun", "--no-install", "{shim}", "{solution}", "{result}"]

[[runtimes]]
id     = "node"
detect = ["node", "--version"]
run    = ["node", "{shim}", "{solution}", "{result}"]
```

## JavaScript

| Topic | Rule |
|---|---|
| Module | The stub is CommonJS (`module.exports = { twoSum }`) and runs on every runtime. ES modules (`export function twoSum`) work on Bun, on Node 22 or newer, and on any Node when `work/package.json` has `"type": "module"`. The shim loads the file with `import()` and looks the name up in the exports, then in `default` |
| Names | Functions, methods and parameters are camelCase; classes keep their name. The statement still shows the Python names, so the stub in the work file is the reference |
| Arguments | Positional, in the order of the pack's Python stub |
| Values | `undefined` is written as `null`. Numbers are exact up to 2^53: return a `BigInt` for a larger integer (lc-b29 decode ways), and the shim writes it as a plain JSON integer |
| Output | `console.log` is harmless: the value goes to the result file |
| Bun | Runs with `--no-install`, so a missing package fails instead of being downloaded (decision D) |

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
                     (args: an object for call = named, an array for positional)
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
| JavaScript | `work/package.json` lists no packages (`dependencies`, `devDependencies`, `optionalDependencies`, `peerDependencies`); every `require`/`import` is a Node builtin (`fs`, `node:fs`, `fs/promises`), a `bun:` module or a local file (`./helper.js`) |
| Go | `go.mod` has no `require` |
| Rust | `Cargo.toml` `[dependencies]` is empty |

On failure: `{"ok": false, "code": "dependencies_not_allowed", "error": "interview rounds use the standard library only: found 'lru'"}`.

## Signatures (typed languages)

Go and Rust cannot call a function by name at run time, so they need glue generated for each problem from a strict signature. Every built-in live-coding pack has a `## Signature` section (`runner/lib/signature.py`; grammar in [authoring.md](authoring.md#signature-block)); lint checks its grammar and that it names exactly the stub's parameters and methods, and `selftest` checks that the oracle's real inputs and outputs conform, perf inputs included with `--perf`.

```
int (64-bit) · float · bool · string · T[] · T? (nullable) · [A, B] (tuple) · {string: T} (map)
record{a: T, b?: U} (b may be absent) · A | B (union) · void (method returns only)
```

| Type | Go | Rust | JavaScript |
|---|---|---|---|
| `int` | `int` | `i64` | `number` (exact to 2^53) |
| `string` | `string` | `String` | `string` |
| `T[]` | `[]T` (a nil slice is written as `[]`) | `Vec<T>` | `Array` |
| `T?` | `*T` | `Option<T>` | `T \| null` |
| `[A, B]` | generated struct, encoded as an array | `(A, B)` | `Array` |
| `{string: T}` | `map[string]T` | `HashMap<String, T>` | `Object` |

The signatures were converted from the stub docstrings by script and the loose ones written by hand. Fixed lengths such as `int[2]` became plain lists. Two packs need a union, `lc-c06` (`int | string`) and `lc-c09` (`{string: int | string}`); `lc-c04` and `lc-c08` return records with optional keys. A pack whose signature does not map to a language is offered in Python and JavaScript only; `draw --lang go` skips it. A pack without a signature (an older user pack) gets a lint warning and is treated the same way.

## Commands and session

| Change | Detail |
|---|---|
| `mi.py langs` | Lists languages, the toolchain found and its version |
| `pick`, `draw` | `--lang ID` (and `--runtime ID`); the skills pass the `default_language` plugin option, else the runner uses `python` |
| `session.json` | Adds `language`, `runtime` and `solution`; the skills and the mod read the file name from here instead of assuming `solution.py` |

## Phases

| Phase | Scope |
|---|---|
| P1 Foundation (**done**) | Python 3.11 floor, TOML loader, `langs`, `--lang`, session fields, result file (B), `python.toml` with no behaviour change, dependency check for Python; skills, scorer, mod and docs follow the session's solution file |
| P2 JavaScript (**done**) | One shim for Bun and Node, camelCase stubs, `package.json` dependency check. All live-coding packs work: no types needed |
| P3 Signatures (**done**) | `## Signature` in every live-coding pack (converted from the docstrings by script, the loose ones by hand); lint and selftest checks; authoring.md updated |
| P4 Go and Rust | Type mapping, generated glue, scaffold, cached builds, manifest checks, the language filter in `draw` |

Each phase ends with the runner tests, mod tests, `lint --all` and `selftest --all` passing, and its docs updated.
