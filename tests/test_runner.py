"""Runner tests. Run from the repository root:  python3 -m unittest discover -s tests -v

Uses small fixture packs in tests/fixtures/content as the plugin's built-in content and temporary
project and data folders, so nothing on the machine is touched.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MI = os.path.join(REPO, "runner", "mi.py")

GOOD_COUNTER = (
    "class MiniCounter:\n"
    "    def __init__(self):\n        self.t = 0\n"
    "    def add(self, x):\n        self.t += x\n"
    "    def total(self):\n        return self.t\n"
)
GOOD_TWO_SUM = (
    "def two_sum(nums, target):\n"
    "    seen = {}\n"
    "    for j, x in enumerate(nums):\n"
    "        if target - x in seen:\n            return [seen[target - x], j]\n"
    "        seen[x] = j\n"
)
BAD_TWO_SUM = "def two_sum(nums, target):\n    return [0, 0]\n"
JS_TWO_SUM = (
    "function twoSum(nums, target) {\n"
    "  console.log('debugging');\n"
    "  const seen = new Map();\n"
    "  for (let j = 0; j < nums.length; j++) {\n"
    "    if (seen.has(target - nums[j])) return [seen.get(target - nums[j]), j];\n"
    "    seen.set(nums[j], j);\n"
    "  }\n"
    "}\n\nmodule.exports = { twoSum };\n"
)
JS_COUNTER = (
    "export class MiniCounter {\n"
    "  constructor() { this.t = 0; }\n"
    "  add(x) { this.t += x; }\n"
    "  total() { return BigInt(this.t); }\n"
    "}\n"
)
JS_RUNTIMES = [r for r in ("bun", "node") if shutil.which(r)]


def _toolchain_env():
    """The tests run with a temporary HOME; keep finding toolchains that live under the real one (rustup's
    toolchains, a `go` wrapper that resolves its SDK from HOME)."""
    extra = {}
    if shutil.which("go"):
        p = subprocess.run(["go", "env", "GOROOT"], capture_output=True, text=True)
        root = p.stdout.strip()
        if p.returncode == 0 and root:
            extra["PATH"] = os.path.join(root, "bin") + os.pathsep + os.environ.get("PATH", "")
    for var, default in (("RUSTUP_HOME", "~/.rustup"), ("CARGO_HOME", "~/.cargo")):
        value = os.environ.get(var) or os.path.expanduser(default)
        if os.path.isdir(value):
            extra[var] = value
    return extra


TOOLCHAIN_ENV = _toolchain_env()
TYPED = {
    "go": {
        "tool": "go", "solution": "solution.go", "panic": "panic: not implemented at solution.go:",
        "stub": "package main\n\nfunc twoSum(nums []int, target int) []int {\n\tpanic(\"not implemented\")\n}\n",
        "two_sum": ("package main\n\nimport \"fmt\"\n\nfunc twoSum(nums []int, target int) []int {\n"
                    "\tfmt.Println(\"debugging\")\n\tseen := map[int]int{}\n\tfor j, x := range nums {\n"
                    "\t\tif i, ok := seen[target-x]; ok {\n\t\t\treturn []int{i, j}\n\t\t}\n\t\tseen[x] = j\n"
                    "\t}\n\treturn nil\n}\n"),
        "counter": ("package main\n\ntype MiniCounter struct{ t int }\n\n"
                    "func NewMiniCounter() *MiniCounter { return &MiniCounter{} }\n\n"
                    "func (m *MiniCounter) Add(x int) { m.t += x }\n\nfunc (m *MiniCounter) Total() int { return m.t }\n"),
        "manifest": ("go.mod", "module solution\n\ngo 1.21\n\nrequire golang.org/x/exp v0.1.0\n"),
        "found": ["golang.org/x/exp"],
    },
    "rust": {
        "tool": "cargo", "solution": os.path.join("src", "solution.rs"), "panic": "not yet implemented",
        "stub": "pub fn two_sum(nums: Vec<i64>, target: i64) -> Vec<i64> {\n    todo!()\n}\n",
        "two_sum": ("use std::collections::HashMap;\n\npub fn two_sum(nums: Vec<i64>, target: i64) -> Vec<i64> {\n"
                    "    println!(\"debugging\");\n    let mut seen = HashMap::new();\n"
                    "    for (j, &x) in nums.iter().enumerate() {\n"
                    "        if let Some(&i) = seen.get(&(target - x)) {\n            return vec![i as i64, j as i64];\n"
                    "        }\n        seen.insert(x, j);\n    }\n    vec![]\n}\n"),
        "counter": ("pub struct MiniCounter {\n    t: i64,\n}\n\nimpl MiniCounter {\n"
                    "    pub fn new() -> Self {\n        MiniCounter { t: 0 }\n    }\n"
                    "    pub fn add(&mut self, x: i64) {\n        self.t += x;\n    }\n"
                    "    pub fn total(&mut self) -> i64 {\n        self.t\n    }\n}\n"),
        "manifest": ("Cargo.toml", '[package]\nname = "mi_solution"\nversion = "0.1.0"\nedition = "2021"\n\n'
                                   '[dependencies]\nitertools = "0.12"\n'),
        "found": ["itertools"],
    },
}


class Env:
    def __init__(self, with_fixtures=True):
        self.tmp = tempfile.mkdtemp(prefix="mi-test-")
        self.plugin = os.path.join(self.tmp, "plugin")
        self.project = os.path.join(self.tmp, "project")
        self.data = os.path.join(self.tmp, "data")
        os.makedirs(self.project)
        os.makedirs(self.plugin)
        for part in ("runner", "languages"):
            shutil.copytree(os.path.join(REPO, part), os.path.join(self.plugin, part),
                            ignore=shutil.ignore_patterns("__pycache__"))
        if with_fixtures:
            shutil.copytree(os.path.join(HERE, "fixtures", "content"), os.path.join(self.plugin, "content"))
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.home)

    def mi(self, *args, expect_ok=True, stdin=None):
        cmd = [sys.executable, os.path.join(self.plugin, "runner", "mi.py"), "--project", self.project,
               "--data", self.data] + list(args)
        env = dict(os.environ, HOME=self.home, **TOOLCHAIN_ENV)
        p = subprocess.run(cmd, capture_output=True, text=True, input=stdin, env=env, timeout=120)
        try:
            out = json.loads(p.stdout)
        except ValueError:
            raise AssertionError("not JSON: %r %r" % (p.stdout, p.stderr))
        if expect_ok:
            assert out.get("ok") is True, out
        return out, p.returncode

    def write(self, rel, text):
        path = os.path.join(self.project, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path

    def solution(self, text):
        return self.write(".mockinterview/work/solution.py", text)

    def session(self):
        with open(os.path.join(self.project, ".mockinterview", "session.json"), encoding="utf-8") as fh:
            return json.load(fh)

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()
        self.addCleanup(self.env.cleanup)

    # ---------------------------------------------------------------- packs
    def test_list_filters_and_roots(self):
        out, _ = self.env.mi("list", "--type", "live-coding", "--level", "senior", "--roots")
        self.assertEqual([p["id"] for p in out["packs"]], ["lc-fx-counter"])
        self.assertEqual(out["roots"][0]["label"], "built-in")
        self.assertTrue(out["roots"][0]["trusted"])

    def test_lint_and_selftest_pass(self):
        out, code = self.env.mi("lint", "--all")
        self.assertTrue(out["pass"], out)
        self.assertEqual(code, 0)
        self.assertEqual([r for r in out["results"] if r.get("warnings")], [])
        out, code = self.env.mi("selftest", "--all", "--perf")
        self.assertTrue(out["pass"], out)
        self.assertEqual(out["checked"], 2)

    def test_lint_catches_broken_pack(self):
        bad = os.path.join(self.env.tmp, "bad.md")
        with open(bad, "w") as fh:
            fh.write("---\nid: lc-bad\ntitle: Bad\ntype: live-coding\nlevel: [expert]\ntags: [x]\n"
                     "time_minutes: 5\nentry: f\nkind: func\nruns_code: true\nlanguages: [python]\n---\n"
                     "# Bad\n\n## Statement\n\nx\n\n## Stub\n\n```python\ndef f(a, b):\n    pass\n```\n\n"
                     "## Tests\n\n```json tests\n{\"function\": \"f\", \"kind\": \"func\", \"cases\": [\n"
                     "{\"name\": \"v\", \"tags\": [\"visible\"], \"args\": {\"a\": 1, \"c\": 2}}]}\n```\n")
        out, code = self.env.mi("lint", bad)
        self.assertFalse(out["pass"])
        self.assertEqual(code, 1)
        errors = " ".join(out["results"][0]["errors"])
        self.assertIn("level 'expert'", errors)
        self.assertIn("missing section", errors)
        self.assertIn("case 'v' args ['a', 'c'] must be the stub's parameters ['a', 'b']", errors)

    def test_lint_checks_signature_against_stub(self):
        src = os.path.join(self.env.plugin, "content", "live-coding", "lc-fx-counter.md")
        with open(src, encoding="utf-8") as fh:
            text = fh.read()
        cases = [("add(x: int) -> void", "add(y: int) -> void", "add(y) must have the stub's parameters (x)"),
                 ("total() -> int", "", "the stub's method total is missing"),
                 ("total() -> int", "total() -> int\nreset() -> void", "method reset is not in the stub"),
                 ("total() -> int", "total()", "method total needs a return type (void when it returns nothing)"),
                 ("add(x: int)", "add(x: integer)", "line 2: unknown type 'integer'")]
        for old, new, message in cases:
            bad = os.path.join(self.env.tmp, "sig.md")
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write(text.replace(old, new, 1))
            out, code = self.env.mi("lint", bad)
            self.assertEqual(code, 1, message)
            self.assertIn("signature: " + message, out["results"][0]["errors"])
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write(text.split("## Signature")[0] + "## Tests" + text.split("## Tests")[1])
        out, _ = self.env.mi("lint", bad)
        self.assertTrue(out["pass"])
        self.assertIn("no '## Signature'", out["results"][0]["warnings"][0])
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write(text.replace("total() -> int", "total() -> int[] | string[]", 1))
        out, _ = self.env.mi("lint", bad)
        self.assertTrue(out["pass"])
        self.assertEqual([w.split(":")[1] for w in out["results"][0]["warnings"]], [" not offered in Go", " not offered in Rust"])

    def test_selftest_checks_oracle_values_against_signature(self):
        path = os.path.join(self.env.plugin, "content", "live-coding", "lc-fx-two-sum.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace("target: int) -> int[]", "target: int) -> [int, string]"))
        out, code = self.env.mi("selftest", "lc-fx-two-sum")
        self.assertEqual(code, 1)
        result = out["results"][0]
        self.assertFalse(result["pass"])
        self.assertEqual(result["passed"], result["total"])
        self.assertRegex(result["signature_errors"][0], r"^case '.+' result\[1\]: expected string, got int \d+$")

    def test_project_pack_overrides_builtin_and_needs_trust(self):
        src = os.path.join(self.env.plugin, "content", "live-coding", "lc-fx-two-sum.md")
        with open(src, encoding="utf-8") as fh:
            text = fh.read().replace("Two Sum (fixture)", "Two Sum (team copy)")
        self.env.write(".mockinterview/packs/lc-fx-two-sum.md", text)
        out, _ = self.env.mi("list", "--roots")
        self.assertEqual(out["overrides"][0]["id"], "lc-fx-two-sum")
        title = [p["title"] for p in out["packs"] if p["id"] == "lc-fx-two-sum"][0]
        self.assertEqual(title, "Two Sum (team copy)")
        refused, code = self.env.mi("pick", "lc-fx-two-sum", expect_ok=False)
        self.assertEqual(refused["code"], "untrusted")
        self.assertEqual(code, 1)
        self.env.mi("trust", os.path.join(self.env.project, ".mockinterview", "packs"))
        ok, _ = self.env.mi("pick", "lc-fx-two-sum")
        self.assertEqual(ok["title"], "Two Sum (team copy)")

    # ------------------------------------------------------------ interview
    def test_draw_is_reproducible_hidden_and_not_rerollable(self):
        a, _ = self.env.mi("draw", "--level", "senior", "--seed", "7")
        self.assertNotIn("title", json.dumps(a))
        self.assertNotIn("fx-", json.dumps(a["rounds"]))
        self.assertEqual(a["rounds_total"], 3)
        first = json.load(open(os.path.join(self.env.project, ".mockinterview", "session.json")))
        again, code = self.env.mi("draw", "--level", "senior", "--seed", "7", expect_ok=False)
        self.assertEqual(again["code"], "session_active")
        self.env.mi("abandon")
        self.env.mi("draw", "--level", "senior", "--seed", "7")
        second = json.load(open(os.path.join(self.env.project, ".mockinterview", "session.json")))
        self.assertEqual([r["problem"] for r in first["loop"]], [r["problem"] for r in second["loop"]])
        self.assertIsNone(first["loop"][0]["title"])

    def test_bad_level(self):
        out, code = self.env.mi("draw", "--level", "wizard", expect_ok=False)
        self.assertEqual(out["code"], "bad_level")
        self.assertEqual(code, 1)

    def test_full_interview_flow(self):
        env = self.env
        env.mi("draw", "--level", "senior", "--seed", "7")
        refused, _ = env.mi("show", "lc-fx-two-sum", expect_ok=False)
        self.assertEqual(refused["code"], "hidden_during_interview")
        early, _ = env.mi("notes", expect_ok=False)
        self.assertEqual(early["code"], "bad_state")
        begin, _ = env.mi("begin")
        self.assertEqual(begin["state"], "running")
        self.assertEqual(begin["limit_seconds"], 600)
        self.assertTrue(os.path.exists(os.path.join(env.project, ".mockinterview", "work", "PROBLEM.md")))
        # hint ladder in order with costs
        h0, _ = env.mi("hint")
        h1, _ = env.mi("hint")
        self.assertEqual((h0["rung"], h0["cost"], h1["rung"], h1["cost"]), ("H0", 0, "H1", 5))
        # stub fails; hidden details are not shown in interview mode
        env.solution(open(os.path.join(env.project, ".mockinterview", "work", "solution.py")).read())
        out, code = env.mi("run")
        self.assertEqual(code, 1)
        self.assertFalse(out["pass"])
        hidden = [f for f in out["failures"] if f["category"] != "visible"]
        self.assertTrue(hidden and all(not f["shown"] and "expected" not in f for f in hidden))
        # fix it and finish round 1
        env.solution(GOOD_COUNTER)
        out, code = env.mi("run")
        self.assertEqual((code, out["passed"], out["total"]), (0, 6, 6))
        fin, _ = env.mi("finish")
        self.assertEqual(fin["state"], "drawn")
        self.assertEqual(fin["next"]["round_number"], 2)
        st, _ = env.mi("status")
        self.assertIsNone(st["title"])
        # round 2 archives the earlier solution instead of overwriting it
        b2, _ = env.mi("begin")
        self.assertIn("archived_previous", b2)
        self.assertTrue(os.path.exists(os.path.join(env.project, b2["archived_previous"])))
        env.solution(GOOD_TWO_SUM)
        env.mi("run", "--perf")
        env.mi("finish")
        # round 3, the design round
        b3, _ = env.mi("begin")
        self.assertEqual(b3["type"], "system-design")
        self.assertTrue(os.path.exists(os.path.join(env.project, ".mockinterview", "work", "design.md")))
        env.write(".mockinterview/work/estimate.json", json.dumps({
            "assumptions": {"dau": 3330000, "writes_per_user_day": 1, "reads_per_user_day": 100,
                            "bytes_per_write": 500, "bytes_per_read": 500, "peak_factor": 2,
                            "retention_years": 5, "replication": 3, "server_qps": 2000},
            "claims": {"write_qps": 40, "read_qps": 3900}}))
        est, _ = env.mi("estimate-check")
        self.assertTrue(est["pass"], est)
        p0, _ = env.mi("hint")
        self.assertEqual(p0["rung"], "P0")
        notes, _ = env.mi("notes", "--section", "reference")
        self.assertIn("key-value store", notes["text"])
        fin, _ = env.mi("finish")
        self.assertEqual(fin["state"], "finished")
        # scoring: incomplete ratings are refused, then accepted
        bad, code = env.mi("score", "--ratings", "-", stdin=json.dumps({"ratings": {}}), expect_ok=False)
        self.assertEqual(bad["code"], "bad_ratings")
        ratings = {
            "ratings": {
                "lc-fx-counter": dict(framing=3, approach=3, quality=3, testing=2, communication=3, adaptability=3),
                "lc-fx-two-sum": dict(framing=4, approach=4, quality=3, testing=3, communication=3, adaptability=3),
                "sd-fx-shortener": dict(scoping=3, estimation=2, architecture=3, deep_dives=2, reliability=2,
                                        communication=3),
            },
            "top_gap": "testing",
        }
        scored, _ = env.mi("score", "--ratings", "-", stdin=json.dumps(ratings))
        card = scored["scorecard"]
        by = {r["problem"]: r for r in card["rounds"]}
        # implementation 4/4 from a full pass: 25 weight is added in full
        self.assertEqual(by["lc-fx-counter"]["ratings"]["implementation"], 4.0)
        self.assertEqual(by["lc-fx-counter"]["penalty"], 5)
        self.assertEqual(by["lc-fx-counter"]["score"], 72.5)
        self.assertEqual(by["sd-fx-shortener"]["penalty"], 0)
        self.assertAlmostEqual(card["total"], round(sum(r["score"] for r in card["rounds"]) / 3, 1))
        again, _ = env.mi("score", "--ratings", "-", stdin=json.dumps(ratings), expect_ok=False)
        self.assertEqual(again["code"], "bad_state")
        hist, _ = env.mi("history")
        self.assertEqual(hist["sessions"], 1)
        self.assertIn("hash-map", hist["tags"])
        # after the interview the hidden material may be read again
        shown, _ = env.mi("show", "lc-fx-two-sum", "--full")
        self.assertIn("## Oracle", shown["text"])

    def test_abandon_is_logged_and_not_scored(self):
        self.env.mi("draw", "--level", "mid", "--seed", "1")
        self.env.mi("abandon")
        hist, _ = self.env.mi("history")
        self.assertEqual(hist["last"][0]["state"], "abandoned")
        self.assertEqual(hist["tags"], {})

    # ------------------------------------------------------------- practice
    def test_practice_shows_edge_details_and_allows_replace(self):
        env = self.env
        env.mi("pick", "lc-fx-two-sum")
        env.mi("begin")
        env.solution(BAD_TWO_SUM)
        out, code = env.mi("run", "--mode", "all")
        self.assertEqual(code, 1)
        edge = [f for f in out["failures"] if f["category"] == "edge"]
        self.assertTrue(edge and edge[0]["shown"] and "expected" in edge[0])
        blocked, _ = env.mi("pick", "lc-fx-counter", expect_ok=False)
        self.assertEqual(blocked["code"], "session_active")
        env.mi("pick", "lc-fx-counter", "--replace")

    def test_visible_mode_runs_only_visible(self):
        env = self.env
        env.mi("pick", "lc-fx-two-sum")
        env.mi("begin")
        env.solution(GOOD_TWO_SUM)
        out, _ = env.mi("run", "--mode", "visible")
        self.assertEqual(out["by_category"], {"visible": "1/1"})

    def test_perf_flag_catches_slow_solution(self):
        env = self.env
        env.mi("pick", "lc-fx-two-sum")
        env.mi("begin")
        env.solution("def two_sum(nums, target):\n"
                     "    import time\n    time.sleep(4)\n    return [0, 1]\n")
        out, _ = env.mi("run", "--mode", "all", "--perf", "--timeout", "2")
        self.assertFalse(out["pass"])

    def test_repeat_marks_and_lists(self):
        out, _ = self.env.mi("repeat", "lc-fx-two-sum", "--reason", "had | to give the idea", "--days", "0")
        self.assertEqual(out["file"], os.path.join(".mockinterview", "repeat.md"))
        listing, _ = self.env.mi("repeat", "--list")
        self.assertEqual(listing["entries"][0]["problem"], "lc-fx-two-sum")
        self.assertEqual(listing["entries"][0]["reason"], "had / to give the idea")
        self.assertTrue(listing["entries"][0]["due"])
        bad, code = self.env.mi("repeat", "no-such-pack", "--reason", "x", expect_ok=False)
        self.assertEqual((bad["code"], code), ("not_found", 1))

    def test_notes_by_problem_and_inherited_blocks(self):
        env = self.env
        env.mi("pick", "sd-fx-shortener")
        env.mi("begin")
        text = env.mi("notes", "--section", "followups")[0]["text"]
        self.assertIn("cache disappears", text)
        ref = env.mi("notes", "--section", "reference")[0]["text"]
        self.assertIn("key-value store", ref)
        other, _ = env.mi("notes", "--problem", "lc-fx-two-sum", expect_ok=False)
        self.assertEqual(other["code"], "not_found")

    def test_commands_need_a_session(self):
        out, code = self.env.mi("run", expect_ok=False)
        self.assertEqual((out["code"], code), ("no_session", 1))
        st, _ = self.env.mi("status")
        self.assertEqual(st["state"], "idle")

    def test_data_value_with_unexpanded_variable_is_ignored(self):
        cmd = [sys.executable, MI, "--project", self.env.project, "--data", "${CLAUDE_PLUGIN_DATA}", "history"]
        p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, HOME=self.env.home))
        self.assertTrue(json.loads(p.stdout)["ok"])
        self.assertFalse(os.path.exists(os.path.join(self.env.project, "${CLAUDE_PLUGIN_DATA}")))


class LanguageTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()
        self.addCleanup(self.env.cleanup)

    def user_language(self, text):
        path = os.path.join(self.env.home, ".mockinterview", "languages", "py2.toml")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return os.path.dirname(path)

    def test_langs_lists_python(self):
        out, _ = self.env.mi("langs")
        py = [x for x in out["languages"] if x["id"] == "python"][0]
        self.assertEqual(out["default"], "python")
        self.assertTrue(py["available"] and py["trusted"])
        self.assertEqual(py["solution"], "solution.py")
        self.assertTrue(py["version"].startswith("Python 3."))

    def test_session_records_language_and_print_is_harmless(self):
        env = self.env
        picked, _ = env.mi("pick", "lc-fx-two-sum")
        self.assertEqual(picked["language"], "python")
        session = env.session()
        self.assertEqual((session["language"], session["runtime"]), ("python", None))
        self.assertEqual(session["solution"], os.path.join(".mockinterview", "work", "solution.py"))
        env.mi("begin")
        env.solution("print('debugging')\n" + GOOD_TWO_SUM.replace("    seen = {}\n", "    seen = {}\n    print(nums)\n"))
        out, code = env.mi("run")
        self.assertEqual((code, out["failed"]), (0, 0), out)
        st, _ = env.mi("status")
        self.assertEqual((st["language"], st["solution"]), ("python", session["solution"]))

    def test_design_session_has_no_language(self):
        out, _ = self.env.mi("pick", "sd-fx-shortener", "--lang", "python")
        self.assertNotIn("language", out)
        self.assertIsNone(self.env.session()["language"])

    def test_unknown_language_and_runtime(self):
        out, code = self.env.mi("pick", "lc-fx-two-sum", "--lang", "cobol", expect_ok=False)
        self.assertEqual((out["code"], code), ("unknown_language", 1))
        self.assertIn("python", out["error"])
        out, _ = self.env.mi("pick", "lc-fx-two-sum", "--runtime", "pypy", expect_ok=False)
        self.assertEqual(out["code"], "unknown_runtime")
        self.assertFalse(os.path.exists(os.path.join(self.env.project, ".mockinterview", "session.json")))

    def test_interview_refuses_third_party_imports_practice_allows_them(self):
        env = self.env
        env.mi("draw", "--level", "senior", "--seed", "7")
        env.mi("begin")
        env.solution("import os, collections.abc\nimport numpy as np\nfrom requests import get\n" + GOOD_COUNTER)
        out, code = env.mi("run", expect_ok=False)
        self.assertEqual((out["code"], code, out["found"]), ("dependencies_not_allowed", 1, ["numpy", "requests"]))
        self.assertIn("standard library only", out["error"])
        env.mi("abandon")
        env.mi("pick", "lc-fx-two-sum")
        env.mi("begin")
        env.solution("import mi_no_such_package\n" + GOOD_TWO_SUM)
        out, code = env.mi("run")
        self.assertEqual(code, 1)
        self.assertIn("mi_no_such_package", json.dumps(out["failures"]))

    def test_user_language_needs_trust_and_picks_the_first_runtime_found(self):
        env = self.env
        shim = os.path.join(env.plugin, "languages", "shims", "py_shim.py")
        root = self.user_language(
            'id = "py2"\nname = "Python, renamed"\nsolution = "answer.py"\nshim = %s\n'
            'detect = ["{python}", "--version"]\nrun = ["{python}", "{shim}", "{solution}", "{result}"]\n'
            'stub_func = "def {entry}({params}):\\n    return None\\n"\nstub_ops = "class {entry}:\\n    pass\\n"\n'
            'time_factor = 2\n'
            '[[runtimes]]\nid = "missing"\ndetect = ["mi-no-such-binary"]\nrun = ["mi-no-such-binary"]\n'
            '[[runtimes]]\nid = "here"\ndetect = ["{python}", "--version"]\n'
            'run = ["{python}", "{shim}", "{solution}", "{result}"]\n' % json.dumps(shim))
        out, _ = env.mi("pick", "lc-fx-two-sum", "--lang", "py2", expect_ok=False)
        self.assertEqual(out["code"], "untrusted")
        env.mi("trust", root)
        out, _ = env.mi("pick", "lc-fx-two-sum", "--lang", "py2", "--runtime", "missing", expect_ok=False)
        self.assertEqual(out["code"], "toolchain_missing")
        out, _ = env.mi("pick", "lc-fx-two-sum", "--lang", "py2")
        self.assertEqual(out["runtime"], "here")
        begin, _ = env.mi("begin")
        self.assertEqual(begin["files"]["solution"], os.path.join(".mockinterview", "work", "answer.py"))
        with open(os.path.join(env.project, begin["files"]["solution"]), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "def two_sum(nums, target):\n    return None\n")
        env.write(".mockinterview/work/answer.py", GOOD_TWO_SUM)
        out, code = env.mi("run")
        self.assertEqual((code, out["failed"]), (0, 0), out)
        langs, _ = env.mi("langs")
        py2 = [x for x in langs["languages"] if x["id"] == "py2"][0]
        self.assertEqual((py2["root"], py2["runtime"]), ("user", "here"))
        self.assertEqual([r["available"] for r in py2["runtimes"]], [False, True])

    @unittest.skipUnless(JS_RUNTIMES, "neither bun nor node is on PATH")
    def test_javascript_stubs_and_runs_on_each_runtime_found(self):
        env = self.env
        for runtime in JS_RUNTIMES:
            with self.subTest(runtime=runtime):
                out, _ = env.mi("pick", "lc-fx-two-sum", "--lang", "javascript", "--runtime", runtime)
                self.assertEqual((out["language"], out["runtime"]), ("javascript", runtime))
                begin, _ = env.mi("begin")
                self.assertEqual(begin["files"]["solution"], os.path.join(".mockinterview", "work", "solution.js"))
                with open(os.path.join(env.project, begin["files"]["solution"]), encoding="utf-8") as fh:
                    self.assertEqual(fh.read(), "function twoSum(nums, target) {\n}\n\nmodule.exports = { twoSum };\n")
                out, code = env.mi("run")
                self.assertEqual((code, out["failed"] > 0), (1, True))
                env.write(".mockinterview/work/solution.js", JS_TWO_SUM)
                out, code = env.mi("run")
                self.assertEqual((code, out["failed"]), (0, 0), out)
                env.mi("abandon")
                env.mi("pick", "lc-fx-counter", "--lang", "javascript", "--runtime", runtime)
                env.mi("begin")
                with open(os.path.join(env.project, ".mockinterview", "work", "solution.js"), encoding="utf-8") as fh:
                    stub = fh.read()
                self.assertIn("class MiniCounter {\n  constructor() {\n  }\n\n  add(x) {\n  }\n", stub)
                env.write(".mockinterview/work/solution.js", JS_COUNTER.replace("this.t += x", "this.t -= x"))
                out, code = env.mi("run")
                self.assertEqual(code, 1)
                self.assertIn('["add", [1]]', out["failures"][0]["args"])
                env.write(".mockinterview/work/solution.js", JS_COUNTER)
                out, code = env.mi("run")
                self.assertEqual((code, out["failed"]), (0, 0), out)
                env.mi("abandon")

    @unittest.skipUnless(JS_RUNTIMES, "neither bun nor node is on PATH")
    def test_javascript_interview_refuses_packages(self):
        env = self.env
        env.mi("draw", "--level", "senior", "--seed", "7", "--lang", "javascript")
        env.mi("begin")
        allowed = ("const fs = require('node:fs');\nconst p = require(\"fs/promises\");\n"
                   "import { x } from './helper.js';\n// require('commented-out')\n")
        env.write(".mockinterview/work/solution.js", allowed + "import _ from 'lodash';\n"
                  "const z = await import(\"@scope/pkg/sub\");\n" + JS_COUNTER)
        env.write(".mockinterview/work/package.json", '{"devDependencies": {"jest": "1"}}')
        out, code = env.mi("run", expect_ok=False)
        self.assertEqual((out["code"], code), ("dependencies_not_allowed", 1))
        self.assertEqual(out["found"], ["jest", "lodash", "@scope/pkg"])
        env.write(".mockinterview/work/package.json", '{"name": "work"}')
        env.write(".mockinterview/work/solution.js", JS_COUNTER.replace("export class", "const fs = require('fs');\nclass")
                  + "module.exports = { MiniCounter };\n")
        out, code = env.mi("run")
        self.assertEqual((code, out["failed"]), (0, 0), out)

    def test_broken_language_file_is_reported_not_loaded(self):
        self.user_language('id = "py2"\nname = "x"\nsolution = "a.go"\ndetect = ["go"]\nrun = ["{bin}"]\n'
                           'batch = true\npack_stub = true\n')
        out, _ = self.env.mi("langs")
        self.assertEqual([x["id"] for x in out["languages"]], ["go", "javascript", "python", "rust"])
        message = out["warnings"][0]["message"]
        self.assertIn("'batch' is not supported yet", message)

    def test_typed_languages_need_a_signature(self):
        env = self.env
        path = os.path.join(env.plugin, "content", "live-coding", "lc-fx-two-sum.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.split("## Signature")[0] + "## Tests" + text.split("## Tests")[1])
        for lang in ("go", "rust"):
            out, code = env.mi("pick", "lc-fx-two-sum", "--lang", lang, expect_ok=False)
            self.assertEqual((out["code"], code), ("language_unsupported", 1))
            self.assertIn("it has no ## Signature", out["error"])
        self.assertFalse(os.path.exists(os.path.join(env.project, ".mockinterview", "session.json")))

    def check_typed_language(self, lang):
        env, t = self.env, TYPED[lang]
        work = os.path.join(".mockinterview", "work")
        env.mi("pick", "lc-fx-two-sum", "--lang", lang)
        begin, _ = env.mi("begin")
        self.assertEqual(begin["files"]["solution"], os.path.join(work, t["solution"]))
        self.assertIn(os.path.join(work, t["manifest"][0]), begin["files"]["project"])
        with open(os.path.join(env.project, begin["files"]["solution"]), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), t["stub"])
        out, code = env.mi("run", "--mode", "visible")
        self.assertEqual((code, out["build"]["built"], out["failed"] > 0), (1, True, True), out)
        self.assertIn(t["panic"], out["failures"][0]["got"])
        env.write(os.path.join(work, t["solution"]), t["two_sum"])
        out, code = env.mi("run", "--perf")
        self.assertEqual((code, out["failed"], out["build"]["built"]), (0, 0, True), out)
        out, _ = env.mi("run", "--mode", "visible")
        self.assertFalse(out["build"]["built"])
        env.write(os.path.join(work, t["solution"]), t["two_sum"] + "\nfn func broken(\n")
        out, code = env.mi("run", expect_ok=False)
        self.assertEqual((out["code"], code), ("build_failed", 1))
        self.assertIn("solution", out["output"])
        env.mi("abandon")
        env.mi("draw", "--level", "senior", "--seed", "7", "--lang", lang)
        env.mi("begin")
        env.write(os.path.join(work, t["solution"]), t["counter"])
        out, code = env.mi("run")
        self.assertEqual((code, out["failed"]), (0, 0), out)
        env.write(os.path.join(work, t["manifest"][0]), t["manifest"][1])
        out, code = env.mi("run", expect_ok=False)
        self.assertEqual((out["code"], out["found"]), ("dependencies_not_allowed", t["found"]))

    @unittest.skipUnless(shutil.which("go"), "go is not on PATH")
    def test_go_builds_and_runs(self):
        self.check_typed_language("go")

    @unittest.skipUnless(shutil.which("cargo"), "cargo is not on PATH")
    def test_rust_builds_and_runs(self):
        self.check_typed_language("rust")


if __name__ == "__main__":
    unittest.main()
