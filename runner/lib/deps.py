"""Interview-mode dependency checks: a solution may use only its language's standard library.

A cheap static look before `run`, friction in the same spirit as the mod's guard, not a sandbox: a dynamic
import gets past it. Each check returns the names it found that are not allowed.
"""
import ast
import json
import os
import re
import sys
import tomllib


def check_python(solution):
    with open(solution, encoding="utf-8") as fh:
        source = fh.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []  # the run itself reports the syntax error
    allowed = set(sys.stdlib_module_names) | {"__future__"}
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        else:
            continue
        for name in names:
            top = name.split(".")[0]
            if top not in allowed and top not in found:
                found.append(top)
    return found


NODE_BUILTINS = {
    "assert", "async_hooks", "buffer", "child_process", "cluster", "console", "constants", "crypto", "dgram",
    "diagnostics_channel", "dns", "domain", "events", "fs", "http", "http2", "https", "inspector", "module", "net",
    "os", "path", "perf_hooks", "process", "punycode", "querystring", "readline", "repl", "stream",
    "string_decoder", "sys", "timers", "tls", "trace_events", "tty", "url", "util", "v8", "vm", "wasi",
    "worker_threads", "zlib",
}
JS_COMMENT_RE = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
JS_IMPORT_RE = re.compile(r"""(?:\brequire\s*\(\s*|\bimport\s*\(\s*|\bfrom\s*|\bimport\s+)(["'`])([^"'`]+)\1""")
MANIFEST_KEYS = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")


def check_npm(solution):
    """package.json declares no packages, and every require/import is a Node or Bun builtin or a local file."""
    found = []
    manifest = os.path.join(os.path.dirname(solution), "package.json")
    try:
        with open(manifest, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        data = {}
    for key in MANIFEST_KEYS:
        section = data.get(key) if isinstance(data, dict) else None
        for name in section if isinstance(section, dict) else ():
            if name not in found:
                found.append(name)
    with open(solution, encoding="utf-8") as fh:
        source = JS_COMMENT_RE.sub("", fh.read())
    for _, spec in JS_IMPORT_RE.findall(source):
        if spec.startswith((".", "/", "node:", "bun:")):
            continue
        parts = spec.split("/")
        name = "/".join(parts[:2]) if spec.startswith("@") else parts[0]
        if name not in NODE_BUILTINS and name not in found:
            found.append(name)
    return found


GO_REQUIRE_RE = re.compile(r"^\s*require\s*(\(|\S+)", re.M)


def check_go(solution, work):
    """go.mod requires no modules."""
    try:
        with open(os.path.join(work, "go.mod"), encoding="utf-8") as fh:
            text = re.sub(r"//[^\n]*", "", fh.read())
    except OSError:
        return []
    found = []
    for m in GO_REQUIRE_RE.finditer(text):
        if m.group(1) != "(":
            names = [m.group(1)]
        else:
            block = text[m.end():text.find(")", m.end())]
            names = [ln.split()[0] for ln in block.splitlines() if ln.strip()]
        found += [n for n in names if n not in found]
    return found


CARGO_TABLES = ("dependencies", "dev-dependencies", "build-dependencies")


def check_cargo(solution, work):
    """Cargo.toml has no [dependencies], [dev-dependencies] or [build-dependencies], target ones included."""
    try:
        with open(os.path.join(work, "Cargo.toml"), "rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return []
    tables = [data] + [t for t in (data.get("target") or {}).values() if isinstance(t, dict)]
    found = []
    for table in tables:
        for key in CARGO_TABLES:
            for name in table.get(key) or {}:
                if name not in found:
                    found.append(name)
    return found


CHECKS = {"python": lambda s, w: check_python(s), "npm": lambda s, w: check_npm(s), "go": check_go,
          "cargo": check_cargo}


def check(kind, solution, work):
    return CHECKS[kind](solution, work)
