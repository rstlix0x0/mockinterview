"""Pack parsing, discovery and lint. Standard library only."""
import ast
import json
import os
import re

LEVELS = ["junior", "mid", "senior", "staff"]
TYPES = ["live-coding", "system-design", "knowledge"]
SOURCES = ["original", "adapted", "third-party"]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ID_PREFIX = {"live-coding": "lc-", "system-design": "sd-", "knowledge": "kb-"}
TAGS = ("visible", "edge", "hidden")
LADDER_RE = re.compile(r"^\s*[-*]\s*([HP])([0-3])\s*\((free|-?\d+)\)\s*:\s*(.+?)\s*$")

HIDDEN_SECTIONS = {"tests", "reference solution", "interviewer notes", "reference estimate"}
ENGINEER_SECTIONS = {"statement", "signature", "self-check questions"}


class PackError(Exception):
    pass


# ---------------------------------------------------------------- frontmatter

def _scalar(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    low = raw.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def _strip_comment(value):
    quote = None
    for i, ch in enumerate(value):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or value[i - 1] in " \t"):
            return value[:i].rstrip()
    return value


def parse_frontmatter(text):
    """Return (meta dict, body text). Raises PackError when there is no frontmatter."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise PackError("file does not start with '---' frontmatter")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise PackError("frontmatter is not closed with '---'")
    meta = {}
    for ln, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise PackError("frontmatter line %d has no ':'" % ln)
        key, _, value = line.partition(":")
        key = key.strip()
        value = _strip_comment(value.strip())
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [_scalar(x) for x in inner.split(",")] if inner else []
        else:
            meta[key] = _scalar(value)
    return meta, "\n".join(lines[end + 1:])


# ------------------------------------------------------------------- sections

def split_sections(body):
    """Return (preamble, {lowercase heading: text}), ignoring headings inside code fences."""
    preamble, sections, current, buf, in_fence = [], {}, None, [], False
    for line in body.split("\n"):
        if line.startswith("```"):
            if not in_fence:
                in_fence = True
            elif line.strip() == "```":
                in_fence = False
        if not in_fence and line.startswith("## ") and not line.startswith("### "):
            if current is not None:
                sections[current] = "\n".join(buf).strip("\n")
            current, buf = line[3:].strip().lower(), []
            continue
        (buf if current is not None else preamble).append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip("\n")
    return "\n".join(preamble).strip("\n"), sections


def fences(text):
    """All fenced blocks as [(info string, body)]."""
    out, in_fence, info, buf = [], False, "", []
    for line in text.split("\n"):
        if line.startswith("```"):
            if not in_fence:
                in_fence, info, buf = True, line[3:].strip(), []
            elif line.strip() == "```":
                out.append((info, "\n".join(buf)))
                in_fence = False
            else:
                buf.append(line)
        elif in_fence:
            buf.append(line)
    return out


def find_fence(text, info):
    """Body of the first fence whose info string equals `info` (word-wise)."""
    want = info.split()
    for got, body in fences(text):
        if got.split() == want:
            return body
    return None


# ----------------------------------------------------------------------- pack

class Pack:
    def __init__(self, path, root, root_label, meta, preamble, sections, raw_body):
        self.path = path
        self.root = root
        self.root_label = root_label
        self.meta = meta
        self.preamble = preamble
        self.sections = sections
        self.raw_body = raw_body

    @property
    def id(self):
        return self.meta.get("id")

    @property
    def type(self):
        return self.meta.get("type")

    @property
    def title(self):
        return self.meta.get("title") or self.id

    @property
    def levels(self):
        v = self.meta.get("level") or []
        return v if isinstance(v, list) else [v]

    @property
    def tags(self):
        v = self.meta.get("tags") or []
        return v if isinstance(v, list) else [v]

    @property
    def time_minutes(self):
        default = {"live-coding": 30, "system-design": 45}.get(self.type, 0)
        v = self.meta.get("time_minutes")
        return v if isinstance(v, int) and v > 0 else default

    def section(self, name):
        return self.sections.get(name)

    def summary(self):
        return {
            "id": self.id, "title": self.title, "type": self.type, "level": self.levels,
            "tags": self.tags, "time_minutes": self.time_minutes,
            "source": self.meta.get("source"), "root": self.root_label, "path": self.path,
        }

    # live-coding helpers
    def suite(self):
        raw = find_fence(self.sections.get("tests", ""), "json tests")
        if raw is None:
            raise PackError("no 'json tests' block under ## Tests")
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise PackError("tests block is not valid JSON: %s" % exc)

    def reference_source(self):
        return find_fence(self.sections.get("reference solution", ""), "python reference")

    def signature(self):
        """The text of the ```signature block, or None."""
        raw = find_fence(self.sections.get("signature", ""), "signature")
        return None if raw is None else raw.strip("\n")

    def reference_estimate(self):
        raw = find_fence(self.sections.get("reference estimate", ""), "json estimate")
        return json.loads(raw) if raw is not None else None

    def notes(self):
        return self.sections.get("interviewer notes", "")

    def ladder(self):
        """{rung index: (label, cost, text)} from the interviewer notes."""
        found = {}
        for line in self.notes().split("\n"):
            m = LADDER_RE.match(line)
            if m:
                idx = int(m.group(2))
                cost = 0 if m.group(3) == "free" else abs(int(m.group(3)))
                found.setdefault(idx, (m.group(1) + m.group(2), cost, m.group(4)))
        return found


def load_pack(path, root="", root_label=""):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    meta, body = parse_frontmatter(text)
    preamble, sections = split_sections(body)
    return Pack(path, root, root_label, meta, preamble, sections, body)


# ---------------------------------------------------------------------- index

class Index:
    def __init__(self):
        self.packs = {}        # id -> Pack (winners)
        self.overrides = []    # [{"id", "winner", "loser"}]
        self.warnings = []     # [{"path", "message"}]
        self.roots = []        # [{"label", "path", "exists", "count"}]


def build_index(ctx):
    index = Index()
    for label, root in ctx.all_roots():
        info = {"label": label, "path": root, "exists": os.path.isdir(root), "count": 0}
        index.roots.append(info)
        if not info["exists"]:
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for fn in sorted(filenames):
                if not fn.endswith(".md") or fn.upper() == "README.MD":
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    pack = load_pack(path, root, label)
                except PackError as exc:
                    index.warnings.append({"path": path, "message": str(exc)})
                    continue
                except OSError as exc:
                    index.warnings.append({"path": path, "message": str(exc)})
                    continue
                if not pack.id:
                    index.warnings.append({"path": path, "message": "frontmatter has no id"})
                    continue
                info["count"] += 1
                old = index.packs.get(pack.id)
                if old is not None:
                    index.overrides.append({"id": pack.id, "winner": path, "loser": old.path})
                index.packs[pack.id] = pack
    return index


# ----------------------------------------------------------------------- lint

def _list_of(meta, key):
    v = meta.get(key)
    return v if isinstance(v, list) else ([] if v is None else [v])


def lint_pack(pack, check_reference=True):
    """Return (errors, warnings) for one loaded pack."""
    errors, warnings = [], []
    meta = pack.meta

    def err(msg):
        errors.append(msg)

    def warn(msg):
        warnings.append(msg)

    for key in ("id", "title", "type", "level", "tags", "time_minutes"):
        if meta.get(key) in (None, "", []):
            err("frontmatter: missing '%s'" % key)
    ptype = meta.get("type")
    pid = meta.get("id") or ""
    if pid and not ID_RE.match(str(pid)):
        err("id '%s' must match [a-z0-9][a-z0-9-]*" % pid)
    if ptype and ptype not in TYPES:
        err("type must be one of %s" % ", ".join(TYPES))
    if ptype in ID_PREFIX and pid and not str(pid).startswith(ID_PREFIX[ptype]):
        warn("id '%s' should start with '%s'" % (pid, ID_PREFIX[ptype]))
    for lv in _list_of(meta, "level"):
        if lv not in LEVELS:
            err("level '%s' is not one of %s" % (lv, ", ".join(LEVELS)))
    if meta.get("source") not in (None,) + tuple(SOURCES):
        err("source must be one of %s" % ", ".join(SOURCES))
    if meta.get("time_minutes") is not None and not isinstance(meta.get("time_minutes"), int):
        err("time_minutes must be an integer")

    if ptype == "live-coding":
        _lint_live_coding(pack, err, warn, check_reference)
    elif ptype == "system-design":
        if not pack.section("statement"):
            err("missing section '## Statement'")
        if not pack.notes():
            err("missing section '## Interviewer notes'")
        elif len(pack.ladder()) < 4:
            warn("interviewer notes have fewer than four probe rungs (P0 to P3)")
        raw = find_fence(pack.sections.get("reference estimate", ""), "json estimate")
        if raw is not None:
            try:
                json.loads(raw)
            except ValueError as exc:
                err("reference estimate is not valid JSON: %s" % exc)
        else:
            warn("no '## Reference estimate' block; estimate-check will not work")
    elif ptype == "knowledge":
        if not pack.raw_body.strip():
            err("knowledge pack has no body")
    return errors, warnings


def _split_top(text):
    """Split on commas that are not inside (), [], {} or <>."""
    parts, depth, buf = [], 0, ""
    for ch in text:
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf)
    return [p.strip() for p in parts]


def signature_lines(text):
    """[(name, [param names])] of each declaration line in a signature block, comments left out."""
    out = []
    for line in text.split("\n"):
        line = line.split("#", 1)[0].strip()
        m = re.match(r"^([A-Za-z_]\w*)\s*\((.*)\)(?:\s*->.*)?$", line)
        if line and not m:
            return None
        if m:
            params = [p.split(":", 1)[0].strip() for p in _split_top(m.group(2))]
            out.append((m.group(1), params))
    return out


def _lint_live_coding(pack, err, warn, check_reference):
    meta = pack.meta
    for key in ("entry", "kind"):
        if not meta.get(key):
            err("frontmatter: missing '%s'" % key)
    if meta.get("kind") not in (None, "func", "ops"):
        err("kind must be 'func' or 'ops'")
    for name in ("statement", "signature", "tests", "reference solution"):
        if not pack.section(name):
            err("missing section '## %s'" % (name[0].upper() + name[1:]))
    if not pack.notes():
        warn("missing '## Interviewer notes'")
    elif len(pack.ladder()) < 4:
        warn("interviewer notes have fewer than four hint rungs (H0 to H3)")
    params = None
    if pack.section("signature"):
        sig = pack.signature()
        lines = signature_lines(sig) if sig is not None else None
        if not lines:
            err("## Signature needs one fenced 'signature' block of lines like name(param: type) -> type")
        elif lines[0][0] != meta.get("entry"):
            err("signature: the first line must declare the entry %s" % meta.get("entry"))
        else:
            params = lines[0][1]
    suite = None
    if pack.section("tests"):
        try:
            suite = pack.suite()
        except PackError as exc:
            err(str(exc))
    if suite is not None:
        if suite.get("function") != meta.get("entry"):
            err("tests 'function' (%r) must equal frontmatter 'entry' (%r)" % (suite.get("function"), meta.get("entry")))
        if suite.get("kind") != meta.get("kind"):
            err("tests 'kind' (%r) must equal frontmatter 'kind' (%r)" % (suite.get("kind"), meta.get("kind")))
        if suite.get("compare", "exact") not in ("exact", "approx"):
            err("tests 'compare' must be exact or approx")
        for key in ("fuzz", "perf"):
            if key in suite:
                warn("tests '%s' is no longer used; add the cases you want as hidden cases" % key)
        cases = suite.get("cases")
        if not isinstance(cases, list) or not cases:
            err("tests need a non-empty 'cases' list")
            cases = []
        names, tagcount = set(), {t: 0 for t in TAGS}
        for i, c in enumerate(cases):
            name = c.get("name")
            if not name or name in names:
                err("case %d has a missing or duplicate name" % i)
            names.add(name)
            tags = c.get("tags")
            if not (isinstance(tags, list) and len(tags) == 1 and tags[0] in TAGS):
                err("case '%s' must have exactly one tag from %s" % (name, ", ".join(TAGS)))
            else:
                tagcount[tags[0]] += 1
            if "expected" not in c:
                err("case '%s' needs an 'expected' value (selftest checks it against the reference)" % name)
            args = c.get("args")
            if suite.get("kind") == "ops":
                calls = args.get("calls") if isinstance(args, dict) else None
                if not (isinstance(calls, list) and calls and isinstance(calls[0], list)
                        and calls[0][0] == suite.get("function")):
                    err("ops case '%s' must start with a constructor call to %s" % (name, suite.get("function")))
                elif isinstance(c.get("expected"), list) and len(c["expected"]) != len(calls):
                    err("ops case '%s' needs one expected value per call (null for the constructor)" % name)
            elif not isinstance(args, dict):
                err("case '%s' needs an 'args' object" % name)
            elif params is not None and sorted(args) != sorted(params):
                err("case '%s' args %s must be the signature's parameters %s" % (name, sorted(args), params))
        if tagcount["visible"] == 0:
            err("at least one 'visible' case is required")
        if tagcount["hidden"] == 0:
            warn("no 'hidden' cases")
        if tagcount["edge"] == 0:
            warn("no 'edge' cases")
    src = pack.reference_source()
    if pack.section("reference solution") and not src:
        err("## Reference solution needs one fenced 'python reference' block")
    if src and check_reference:
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            err("reference solution does not compile: %s" % exc)
            return
        names = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        entry = meta.get("entry")
        if meta.get("kind") == "func" and "solve" not in names:
            err("reference solution must define solve(...)")
        if meta.get("kind") == "ops" and entry not in names:
            err("reference solution must define class %s" % entry)
