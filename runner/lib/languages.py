"""Language files: how a candidate's solution is written, found and run. Standard library only.

One TOML file per language in `languages/` of the built-in, user and project roots; a later root wins on the
same id. Files outside the built-in root run commands, so they need `mi.py trust` like pack roots. The format
is in docs/languages.md.
"""
import os
import re
import subprocess
import sys
import tomllib

from . import glue, packs
from .signature import SignatureError
from .util import MiError

DEFAULT = "python"
DETECT_TIMEOUT = 15
REQUIRED = ("id", "name", "solution")
KNOWN = set(REQUIRED) | {"detect", "run", "shim", "pack_stub", "stub_func", "stub_ops", "stub_method", "naming",
                         "call", "time_factor", "env_pass", "env", "runtimes", "deps_check", "glue", "build", "bin",
                         "scaffold"}
PLANNED = {"batch"}  # not built yet
ARGV_VARS = {"python", "shim", "solution", "work", "result", "build", "bin"}
STUB_VARS = {"entry", "params", "methods"}
METHOD_VARS = {"name", "params"}
NAMINGS = ("snake", "camel")
CALLS = ("named", "positional")
DEPS_CHECKS = {"python", "npm", "go", "cargo"}
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
        if key not in data:
            if "runtimes" not in data:
                errors.append("%s is required unless runtimes are given" % key)
        elif not _str_list(data[key]):
            errors.append("%s must be a non-empty list of strings" % key)
        else:
            _check_vars(key, data[key], ARGV_VARS, errors)
    if "glue" in data and data["glue"] not in glue.GENERATORS:
        errors.append("glue must be one of: %s" % ", ".join(glue.GENERATORS))
    if "build" in data:
        if not _str_list(data["build"]):
            errors.append("build must be a non-empty list of strings")
        else:
            _check_vars("build", data["build"], ARGV_VARS - {"result", "solution", "shim"}, errors)
    if "bin" in data:
        if not isinstance(data["bin"], str) or not data["bin"]:
            errors.append("bin must be a path")
        else:
            _check_vars("bin", [data["bin"]], {"build", "work"}, errors)
    if "scaffold" in data:
        sc = data["scaffold"]
        if not (isinstance(sc, dict) and all(isinstance(v, str) for v in sc.values())):
            errors.append("scaffold must be a table of file name = content")
        elif any(os.path.isabs(k) or ".." in k.replace("\\", "/").split("/") for k in sc):
            errors.append("scaffold files must be paths inside work/")
    if not data.get("pack_stub") and "glue" not in data:
        for key in ("stub_func", "stub_ops"):
            if not isinstance(data.get(key), str):
                errors.append("%s is required unless pack_stub = true or glue is set" % key)
            else:
                _check_vars(key, [data[key]], STUB_VARS, errors)
    if "stub_method" in data:
        if not isinstance(data["stub_method"], str):
            errors.append("stub_method must be a string")
        else:
            _check_vars("stub_method", [data["stub_method"]], METHOD_VARS, errors)
    elif "{methods}" in str(data.get("stub_ops", "")):
        errors.append("stub_ops uses {methods}, which needs stub_method")
    for key, allowed in (("naming", NAMINGS), ("call", CALLS)):
        if key in data and data[key] not in allowed:
            errors.append("%s must be one of: %s" % (key, ", ".join(allowed)))
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
        self.naming = data.get("naming", "snake")
        self.call = data.get("call", "named")
        self.glue = data.get("glue")                               # generator name for typed languages
        self.build_argv = data.get("build")
        self.bin = data.get("bin", "{build}/solution")
        self.scaffold = data.get("scaffold") or {}
        if self.glue:
            self.call = "positional"                               # the glue reads arguments by position
        self.runtimes = data.get("runtimes") or []
        self.runtime = None                                        # chosen runtime id, set by select()
        self.run_argv = list(data.get("run") or self.runtimes[0]["run"])  # the chosen runtime's run command

    def summary(self):
        return {"id": self.id, "name": self.name, "solution": self.solution, "root": self.root_label,
                "path": self.path}

    def work_of(self, solution):
        """The work folder of a solution path (src/solution.rs lives one level down)."""
        depth = len([p for p in self.solution.replace("\\", "/").split("/") if p]) - 1
        work = os.path.dirname(solution)
        for _ in range(depth):
            work = os.path.dirname(work)
        return work

    def build_dir(self, work):
        """Where builds go: .mockinterview/build/<id>/, beside work/."""
        return os.path.join(os.path.dirname(work), "build", self.id)

    def _vars(self, solution="", result="", work=""):
        build = self.build_dir(work) if work else ""
        values = {"python": sys.executable, "shim": self.shim or "", "solution": solution, "result": result,
                  "work": work, "build": build}
        values["bin"] = VAR_RE.sub(lambda m: values[m.group(1)], self.bin) if work else ""
        return values

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

    def ident(self, name):
        """A pack name (snake_case, from the Python stub) as this language spells it."""
        if self.naming != "camel" or "_" not in name.strip("_"):
            return name
        head, *rest = name.strip("_").split("_")
        return head + "".join(w[:1].upper() + w[1:] for w in rest)

    def request(self, suite, args, params):
        """The stdin request for one test case. `params` is the order of the stub's parameters."""
        if suite["kind"] == "ops":
            calls = [[name if i == 0 else self.ident(name), a] for i, (name, a) in enumerate(args["calls"])]
            return {"function": suite["function"], "calls": calls}
        if self.call == "named":
            return {"function": self.ident(suite["function"]), "args": args}
        if sorted(args) != sorted(params):
            raise MiError("the test arguments %s do not match the stub's parameters %s"
                          % (sorted(args), params), code="bad_pack")
        return {"function": self.ident(suite["function"]), "args": [args[p] for p in params]}

    def generator(self, pack):
        """(glue generator, parsed signature) for a typed language; raises MiError when the pack cannot be offered."""
        try:
            sig = pack.signature()
        except SignatureError as exc:
            sig, why = None, "its signature does not parse: %s" % exc
        else:
            why = "it has no ## Signature"
        if sig is None:
            raise MiError("%s is not available in %s: %s" % (pack.id, self.name, why), code="language_unsupported",
                          language=self.id)
        gen = glue.get(self.glue)
        try:
            gen.check(sig)
        except glue.Unsupported as exc:
            raise MiError("%s is not available in %s: %s" % (pack.id, self.name, exc), code="language_unsupported",
                          language=self.id)
        return gen, sig

    def supports(self, pack):
        """True when this language can run the pack (always, unless the language needs glue)."""
        if not self.glue:
            return True
        try:
            self.generator(pack)
        except MiError:
            return False
        return True

    def glue_files(self, pack):
        """{path in work/: content} of the runner-owned glue, rewritten before every build."""
        if not self.glue:
            return {}
        gen, sig = self.generator(pack)
        return gen.files(sig, pack.meta.get("kind"), pack.id, self.ident)

    def params(self, pack):
        """Parameter names of the pack's entry function, in the order of its Python stub."""
        return packs.stub_signatures(pack.stub() or "", pack.suite()["function"])[0] or []

    def stub(self, pack):
        """The starting content of the solution file for a live-coding pack."""
        source = pack.stub() or ""
        if self.pack_stub:
            return source
        if self.glue:
            gen, sig = self.generator(pack)
            return gen.stub(sig, pack.meta.get("kind"))
        suite = pack.suite()
        params, methods = packs.stub_signatures(source, suite["function"])
        params = params or []

        def render(template, values):
            return VAR_RE.sub(lambda m: values[m.group(1)], template)

        def plist(names):
            return ", ".join(self.ident(p) for p in names)

        if suite["kind"] == "ops":
            body = "".join(render(self.data.get("stub_method", ""), {"name": self.ident(n), "params": plist(p)})
                           for n, p in methods)
            values = {"entry": suite["function"], "params": plist(params), "methods": body}
            return render(self.data["stub_ops"], values)
        values = {"entry": self.ident(suite["function"]), "params": plist(params), "methods": ""}
        return render(self.data["stub_func"], values)


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
