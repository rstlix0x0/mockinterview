"""Language files: how a candidate's solution is written, found and run. Standard library only.

One TOML file per language in `languages/` of the built-in, user and project roots; a later root wins on the
same id. Files outside the built-in root run commands, so they need `mi.py trust` like pack roots. The format
is in docs/languages.md.
"""
import ast
import os
import re
import subprocess
import sys
import tomllib

from . import packs
from .util import MiError

DEFAULT = "python"
DETECT_TIMEOUT = 15
REQUIRED = ("id", "name", "solution", "detect", "run")
KNOWN = set(REQUIRED) | {"shim", "pack_stub", "stub_func", "stub_ops", "time_factor", "env_pass", "env",
                         "runtimes", "deps_check"}
PLANNED = {"build", "glue", "scaffold", "naming", "batch"}  # compiled and renamed languages, not built yet
ARGV_VARS = {"python", "shim", "solution", "work", "result"}
STUB_VARS = {"entry", "params"}
DEPS_CHECKS = {"python"}
BASE_ENV = ("PATH", "HOME", "LANG", "LC_ALL", "SYSTEMROOT", "TMPDIR")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VAR_RE = re.compile(r"\{([A-Za-z_]+)\}")


class LanguageError(Exception):
    pass


def _str_list(v):
    return isinstance(v, list) and bool(v) and all(isinstance(x, str) and x for x in v)


def _check_vars(where, texts, allowed, errors):
    for text in texts:
        for name in VAR_RE.findall(text):
            if name not in allowed:
                errors.append("%s: unknown placeholder {%s}" % (where, name))


def validate(data):
    """Error messages for a parsed language file; empty when it is usable."""
    errors = []
    for key in REQUIRED:
        if key not in data:
            errors.append("missing field '%s'" % key)
    for key in sorted(data):
        if key in PLANNED:
            errors.append("field '%s' is not supported yet (see docs/languages.md)" % key)
        elif key not in KNOWN:
            errors.append("unknown field '%s'" % key)
    if errors:
        return errors
    if not isinstance(data["id"], str) or not ID_RE.match(data["id"]):
        errors.append("id must be lower-case letters, digits and dashes")
    for key in ("name", "solution"):
        if not isinstance(data[key], str) or not data[key].strip():
            errors.append("%s must be a non-empty string" % key)
    sol = data.get("solution")
    if isinstance(sol, str) and (os.path.isabs(sol) or ".." in sol.replace("\\", "/").split("/")):
        errors.append("solution must be a path inside work/")
    for key in ("detect", "run"):
        if not _str_list(data[key]):
            errors.append("%s must be a non-empty list of strings" % key)
        else:
            _check_vars(key, data[key], ARGV_VARS, errors)
    if not data.get("pack_stub"):
        for key in ("stub_func", "stub_ops"):
            if not isinstance(data.get(key), str):
                errors.append("%s is required unless pack_stub = true" % key)
            else:
                _check_vars(key, [data[key]], STUB_VARS, errors)
    if "time_factor" in data and not (isinstance(data["time_factor"], (int, float))
                                      and not isinstance(data["time_factor"], bool) and data["time_factor"] > 0):
        errors.append("time_factor must be a positive number")
    if "env_pass" in data and not _str_list(data["env_pass"]):
        errors.append("env_pass must be a list of variable names")
    if "env" in data and not (isinstance(data["env"], dict) and all(isinstance(v, str) for v in data["env"].values())):
        errors.append("env must be a table of strings")
    if "deps_check" in data and data["deps_check"] not in DEPS_CHECKS:
        errors.append("deps_check must be one of: %s" % ", ".join(sorted(DEPS_CHECKS)))
    if "runtimes" in data:
        rts = data["runtimes"]
        if not (isinstance(rts, list) and rts):
            errors.append("runtimes must be a non-empty list of tables")
        else:
            for i, rt in enumerate(rts):
                where = "runtimes[%d]" % i
                if not isinstance(rt, dict) or not isinstance(rt.get("id"), str) or not ID_RE.match(rt["id"]):
                    errors.append("%s needs an id" % where)
                    continue
                for key in ("detect", "run"):
                    if not _str_list(rt.get(key)):
                        errors.append("%s.%s must be a non-empty list of strings" % (where, key))
                    else:
                        _check_vars("%s.%s" % (where, key), rt[key], ARGV_VARS, errors)
    return errors


class Language:
    def __init__(self, data, path, root, root_label):
        self.data = data
        self.path = path
        self.root = root
        self.root_label = root_label
        self.id = data["id"]
        self.name = data["name"]
        self.solution = data["solution"]
        base = os.path.dirname(path)
        self.shim = os.path.join(base, data["shim"]) if data.get("shim") else None
        self.pack_stub = bool(data.get("pack_stub"))
        self.time_factor = float(data.get("time_factor", 1.0))
        self.deps_check = data.get("deps_check")
        self.runtimes = data.get("runtimes") or []
        self.runtime = None                  # chosen runtime id, set by select()
        self.run_argv = list(data["run"])    # the chosen runtime's run command

    def summary(self):
        return {"id": self.id, "name": self.name, "solution": self.solution, "root": self.root_label,
                "path": self.path}

    def _vars(self, solution="", result="", work=""):
        return {"python": sys.executable, "shim": self.shim or "", "solution": solution, "result": result,
                "work": work}

    def argv(self, template, solution="", result="", work=""):
        values = self._vars(solution, result, work)
        return [VAR_RE.sub(lambda m: values[m.group(1)], part) for part in template]

    def environment(self):
        keep = set(BASE_ENV) | set(self.data.get("env_pass", []))
        env = {k: v for k, v in os.environ.items() if k in keep}
        env.update(self.data.get("env", {}))
        return env

    def _detect(self, template):
        """(available, version text) for one detect command."""
        try:
            p = subprocess.run(self.argv(template), capture_output=True, text=True, timeout=DETECT_TIMEOUT,
                               env=self.environment())
        except (OSError, subprocess.TimeoutExpired):
            return False, None
        lines = [ln.strip() for ln in (p.stdout + "\n" + p.stderr).splitlines() if ln.strip()]
        return p.returncode == 0, (lines[0][:120] if lines else None)

    def probe(self):
        """Every runtime with its availability, for `langs`."""
        if not self.runtimes:
            ok, version = self._detect(self.data["detect"])
            return [{"id": None, "available": ok, "version": version}]
        out = []
        for rt in self.runtimes:
            ok, version = self._detect(rt["detect"])
            out.append({"id": rt["id"], "available": ok, "version": version})
        return out

    def select(self, runtime=None):
        """Choose the runtime (the requested one, else the first found) and check the toolchain is there."""
        if runtime and not self.runtimes:
            raise MiError("language '%s' has no runtimes to choose from" % self.id, code="unknown_runtime")
        if self.runtimes:
            ids = [rt["id"] for rt in self.runtimes]
            if runtime and runtime not in ids:
                raise MiError("language '%s' has no runtime '%s'; it has: %s" % (self.id, runtime, ", ".join(ids)),
                              code="unknown_runtime")
            for rt in self.runtimes:
                if runtime and rt["id"] != runtime:
                    continue
                ok, version = self._detect(rt["detect"])
                if ok:
                    self.runtime, self.run_argv = rt["id"], list(rt["run"])
                    return version
            raise MiError("no toolchain for %s was found on PATH (tried: %s)"
                          % (self.name, runtime or ", ".join(ids)), code="toolchain_missing", language=self.id)
        ok, version = self._detect(self.data["detect"])
        if not ok:
            raise MiError("no toolchain for %s was found: %s failed" % (self.name, " ".join(self.data["detect"])),
                          code="toolchain_missing", language=self.id)
        return version

    def use(self, runtime):
        """Re-apply a runtime stored in the session, without detecting again."""
        for rt in self.runtimes:
            if rt["id"] == runtime:
                self.runtime, self.run_argv = rt["id"], list(rt["run"])
                return
        if runtime:
            raise MiError("language '%s' no longer has runtime '%s'" % (self.id, runtime), code="unknown_runtime")

    def stub(self, pack):
        """The starting content of the solution file for a live-coding pack."""
        source = pack.stub() or ""
        if self.pack_stub:
            return source
        suite = pack.suite()
        template = self.data["stub_ops"] if suite["kind"] == "ops" else self.data["stub_func"]
        values = {"entry": suite["function"], "params": ", ".join(_stub_params(source, suite["function"]))}
        return VAR_RE.sub(lambda m: values[m.group(1)], template)


def _stub_params(source, name):
    """Parameter names of the function `name` in the pack's Python stub."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return [a.arg for a in node.args.args]
    return []


# ----------------------------------------------------------------- discovery

class Catalog:
    def __init__(self):
        self.languages = {}   # id -> Language (winners)
        self.overrides = []   # [{"id", "winner", "loser"}]
        self.warnings = []    # [{"path", "message"}]


def load_file(path, root="", root_label=""):
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise LanguageError("not valid TOML: %s" % exc)
    errors = validate(data)
    if errors:
        raise LanguageError("; ".join(errors))
    return Language(data, path, root, root_label)


def load_catalog(ctx, builtin_only=False):
    cat = Catalog()
    roots = ctx.language_roots()
    for label, root in roots[:1] if builtin_only else roots:
        if not os.path.isdir(root):
            continue
        for fn in sorted(os.listdir(root)):
            if not fn.endswith(".toml"):
                continue
            path = os.path.join(root, fn)
            try:
                lang = load_file(path, root, label)
            except (LanguageError, OSError) as exc:
                cat.warnings.append({"path": path, "message": str(exc)})
                continue
            old = cat.languages.get(lang.id)
            if old is not None:
                cat.overrides.append({"id": lang.id, "winner": path, "loser": old.path})
            cat.languages[lang.id] = lang
    return cat


def get(ctx, lang_id=None, builtin_only=False):
    """The language with this id (default: python), trusted; raises MiError otherwise."""
    lang_id = lang_id or DEFAULT
    cat = load_catalog(ctx, builtin_only)
    lang = cat.languages.get(lang_id)
    if lang is None:
        bad = [w for w in cat.warnings if os.path.basename(w["path"]) == lang_id + ".toml"]
        detail = "; %s: %s" % (bad[0]["path"], bad[0]["message"]) if bad else ""
        raise MiError("no language '%s'; available: %s%s" % (lang_id, ", ".join(sorted(cat.languages)) or "none",
                                                              detail), code="unknown_language")
    if not packs.is_trusted(ctx, lang.root_label, lang.root):
        raise MiError("language root '%s' is not trusted; read %s, then run: mi.py trust \"%s\""
                      % (lang.root, lang.path, lang.root), code="untrusted", root=lang.root)
    return lang
