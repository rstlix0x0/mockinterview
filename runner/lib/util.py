"""Shared helpers: errors, time, JSON output, atomic writes, path context."""
import datetime
import json
import os
import sys

UTC = datetime.timezone.utc


class MiError(Exception):
    """A user or state error: printed as JSON, exit code 1 (or 2 for internal)."""

    def __init__(self, message, code="error", exit_code=1, **extra):
        super().__init__(message)
        self.message = message
        self.code = code
        self.exit_code = exit_code
        self.extra = extra


def now_utc():
    return datetime.datetime.now(UTC)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(text):
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def emit(obj, pretty=False):
    sys.stdout.write(json.dumps(obj, indent=2 if pretty else None, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()


def atomic_write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp-%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default
    except ValueError as exc:
        raise MiError("%s is not valid JSON: %s" % (path, exc), code="bad_json")


def short(value, limit=240):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit] + "...(%d chars)" % len(text)


def slug(text):
    out = []
    for ch in text.lower():
        out.append(ch if ch.isalnum() else "-")
    s = "".join(out)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


class Ctx:
    """Resolved paths and options for one invocation."""

    def __init__(self, project=None, data=None, roots=None, plugin_root=None):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # runner/
        self.plugin_root = os.path.abspath(plugin_root) if plugin_root else os.path.dirname(here)
        self.runner_dir = here
        self.project = os.path.abspath(project or os.getcwd())
        self.mi_dir = os.path.join(self.project, ".mockinterview")
        self.work_dir = os.path.join(self.mi_dir, "work")
        self.session_path = os.path.join(self.mi_dir, "session.json")
        self.data = self._resolve_data(data)
        self.history_path = os.path.join(self.data, "history.jsonl")
        self.trust_path = os.path.join(self.data, "trust.json")
        self.perf_cache = os.path.join(self.data, "perf_cache")
        self.builtin_root = os.path.join(self.plugin_root, "content")
        home = os.path.expanduser("~")
        self.extra_roots = [
            ("user", os.path.join(home, ".mockinterview", "packs")),
            ("project", os.path.join(self.mi_dir, "packs")),
        ] + [("option", os.path.abspath(os.path.expanduser(r))) for r in (roots or []) if r and "${" not in r]
        self.home = home

    @staticmethod
    def _resolve_data(data):
        for candidate in (data, os.environ.get("CLAUDE_PLUGIN_DATA")):
            if candidate and "${" not in candidate:
                return os.path.abspath(os.path.expanduser(candidate))
        return os.path.join(os.path.expanduser("~"), ".mockinterview", "data")

    def all_roots(self):
        """[(label, path)] in precedence order, later wins."""
        return [("built-in", self.builtin_root)] + self.extra_roots

    def language_roots(self):
        """[(label, path)] of language-file folders, later wins."""
        return [("built-in", os.path.join(self.plugin_root, "languages")),
                ("user", os.path.join(self.home, ".mockinterview", "languages")),
                ("project", os.path.join(self.mi_dir, "languages"))]
