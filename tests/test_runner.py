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

class Env:
    def __init__(self, with_fixtures=True):
        self.tmp = tempfile.mkdtemp(prefix="mi-test-")
        self.plugin = os.path.join(self.tmp, "plugin")
        self.project = os.path.join(self.tmp, "project")
        self.data = os.path.join(self.tmp, "data")
        os.makedirs(self.project)
        os.makedirs(self.plugin)
        shutil.copytree(os.path.join(REPO, "runner"), os.path.join(self.plugin, "runner"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        if with_fixtures:
            shutil.copytree(os.path.join(HERE, "fixtures", "content"), os.path.join(self.plugin, "content"))
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.home)

    def mi(self, *args, expect_ok=True, stdin=None):
        cmd = [sys.executable, os.path.join(self.plugin, "runner", "mi.py"), "--project", self.project,
               "--data", self.data] + list(args)
        env = dict(os.environ, HOME=self.home)
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

    def test_lint_and_selftest_pass(self):
        out, code = self.env.mi("lint", "--all")
        self.assertTrue(out["pass"], out)
        self.assertEqual(code, 0)
        self.assertEqual([r for r in out["results"] if r.get("warnings")], [])
        out, code = self.env.mi("selftest", "--all")
        self.assertTrue(out["pass"], out)
        self.assertEqual(out["checked"], 2)

    def test_lint_catches_broken_pack(self):
        bad = os.path.join(self.env.tmp, "bad.md")
        with open(bad, "w") as fh:
            fh.write("---\nid: lc-bad\ntitle: Bad\ntype: live-coding\nlevel: [expert]\ntags: [x]\n"
                     "time_minutes: 5\nentry: f\nkind: func\n---\n"
                     "# Bad\n\n## Statement\n\nx\n\n## Signature\n\n```signature\nf(a: int, b: int) -> int\n```\n\n"
                     "## Tests\n\n```json tests\n{\"function\": \"f\", \"kind\": \"func\", \"fuzz\": 3, \"cases\": [\n"
                     "{\"name\": \"v\", \"tags\": [\"visible\"], \"args\": {\"a\": 1, \"c\": 2}}]}\n```\n")
        out, code = self.env.mi("lint", bad)
        self.assertFalse(out["pass"])
        self.assertEqual(code, 1)
        result = out["results"][0]
        errors = " ".join(result["errors"])
        self.assertIn("level 'expert'", errors)
        self.assertIn("missing section '## Reference solution'", errors)
        self.assertIn("case 'v' needs an 'expected' value", errors)
        self.assertIn("case 'v' args ['a', 'c'] must be the signature's parameters ['a', 'b']", errors)
        self.assertIn("tests 'fuzz' is no longer used", " ".join(result["warnings"]))

    def test_lint_checks_signature_entry_and_ops_lengths(self):
        src = os.path.join(self.env.plugin, "content", "live-coding", "lc-fx-counter.md")
        with open(src, encoding="utf-8") as fh:
            text = fh.read()
        bad = os.path.join(self.env.tmp, "sig.md")
        for old, new, message in [("MiniCounter()\n", "Counter()\n", "signature: the first line must declare"),
                                  ("MiniCounter()\n", "MiniCounter(\n", "needs one fenced 'signature' block"),
                                  ('"expected":[null,', '"expected":[', "one expected value per call")]:
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write(text.replace(old, new, 1))
            out, code = self.env.mi("lint", bad)
            self.assertEqual(code, 1, message)
            self.assertIn(message, " ".join(out["results"][0]["errors"]))

    def test_selftest_checks_expected_values_against_the_reference(self):
        path = os.path.join(self.env.plugin, "content", "live-coding", "lc-fx-two-sum.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace('"expected":[0,1]', '"expected":[1,0]', 1))
        out, code = self.env.mi("selftest", "lc-fx-two-sum")
        self.assertEqual(code, 1)
        result = out["results"][0]
        self.assertFalse(result["pass"])
        self.assertEqual(result["passed"], result["total"] - 1)
        self.assertEqual((result["failures"][0]["expected"], result["failures"][0]["got"]), ("[1, 0]", "[0, 1]"))
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace(',"expected":[0,1]', "", 1))
        out, code = self.env.mi("selftest", "lc-fx-two-sum", "--write-expected")
        self.assertEqual((code, out["results"][0]["written"]), (0, result["total"]))
        with open(path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), text)

    def test_project_pack_overrides_builtin(self):
        src = os.path.join(self.env.plugin, "content", "live-coding", "lc-fx-two-sum.md")
        with open(src, encoding="utf-8") as fh:
            text = fh.read().replace("Two Sum (fixture)", "Two Sum (team copy)")
        self.env.write(".mockinterview/packs/lc-fx-two-sum.md", text)
        out, _ = self.env.mi("list", "--roots")
        self.assertEqual(out["overrides"][0]["id"], "lc-fx-two-sum")
        title = [p["title"] for p in out["packs"] if p["id"] == "lc-fx-two-sum"][0]
        self.assertEqual(title, "Two Sum (team copy)")
        ok, _ = self.env.mi("pick", "lc-fx-two-sum")
        self.assertEqual(ok["title"], "Two Sum (team copy)")

    # ------------------------------------------------------------ interview
    def test_draw_is_reproducible_hidden_and_not_rerollable(self):
        a, _ = self.env.mi("draw", "--level", "senior", "--seed", "7")
        self.assertNotIn("title", json.dumps(a))
        self.assertNotIn("fx-", json.dumps(a["rounds"]))
        self.assertEqual(a["rounds_total"], 3)
        first = self.env.session()
        again, code = self.env.mi("draw", "--level", "senior", "--seed", "7", expect_ok=False)
        self.assertEqual(again["code"], "session_active")
        self.env.mi("abandon")
        self.env.mi("draw", "--level", "senior", "--seed", "7")
        second = self.env.session()
        self.assertEqual([r["problem"] for r in first["loop"]], [r["problem"] for r in second["loop"]])
        self.assertIsNone(first["loop"][0]["title"])

    def test_bad_level(self):
        out, code = self.env.mi("draw", "--level", "wizard", expect_ok=False)
        self.assertEqual(out["code"], "bad_level")
        self.assertEqual(code, 1)

    def test_full_interview_flow(self):
        env = self.env
        env.mi("draw", "--level", "senior", "--seed", "7", "--lang", "Go", "--test-cmd", "go  test ./...")
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
        self.assertEqual((begin["language"], begin["test_command"]), ("Go", "go test ./..."))
        self.assertIn("MiniCounter()", begin["signature"])
        visible, _ = env.mi("tests")
        self.assertEqual([c["category"] for c in visible["cases"]], ["visible"])
        self.assertEqual(visible["cases"][0]["expected"][0], None)
        everything, _ = env.mi("tests", "--all")
        self.assertIn("policy", everything)
        hidden_name = [c["name"] for c in everything["cases"] if c["category"] == "hidden"][0]
        # a failing hidden case is counted but its details are not shown in interview mode
        out, code = env.mi("record", "--failed", "example-1," + hidden_name, "--got", "example-1=[null,null,3]")
        self.assertEqual(code, 0)
        self.assertFalse(out["pass"])
        shown = {f["name"]: f for f in out["failures"]}
        self.assertTrue(shown["example-1"]["shown"] and shown["example-1"]["got"] == "[null,null,3]")
        self.assertTrue(not shown[hidden_name]["shown"] and "expected" not in shown[hidden_name])
        env.write(".mockinterview/work/counter.go", "package main\n")
        out, _ = env.mi("record")
        self.assertEqual((out["passed"], out["total"]), (everything["count"], everything["count"]))
        fin, _ = env.mi("finish")
        self.assertEqual(fin["state"], "drawn")
        self.assertEqual(fin["next"]["round_number"], 2)
        st, _ = env.mi("status")
        self.assertIsNone(st["title"])
        # round 2 starts with an empty work folder; round 1's files are archived
        b2, _ = env.mi("begin")
        self.assertIn("archived_previous", b2)
        self.assertTrue(os.path.exists(os.path.join(env.project, b2["archived_previous"], "counter.go")))
        self.assertEqual(sorted(os.listdir(os.path.join(env.project, ".mockinterview", "work"))), ["PROBLEM.md", "archive"])
        env.mi("record", "--error", "two_sum.go:3: undefined: seen")
        env.mi("record", "--mode", "all")
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
        self.assertIn("## Reference solution", shown["text"])

    def test_abandon_is_logged_and_not_scored(self):
        self.env.mi("draw", "--level", "mid", "--seed", "1")
        self.env.mi("abandon")
        hist, _ = self.env.mi("history")
        self.assertEqual(hist["last"][0]["state"], "abandoned")
        self.assertEqual(hist["tags"], {})

    # ------------------------------------------------------------- practice
    def test_practice_shows_edge_details_and_allows_replace(self):
        env = self.env
        out, _ = env.mi("pick", "lc-fx-two-sum")
        self.assertEqual((out["language"], out["test_command"]), ("python", None))
        env.mi("begin")
        out, code = env.mi("record", "--failed", "edge-duplicates")
        self.assertEqual(code, 0)
        edge = out["failures"][0]
        self.assertTrue(edge["shown"] and edge["expected"] == "[0, 1]")
        blocked, _ = env.mi("pick", "lc-fx-counter", expect_ok=False)
        self.assertEqual(blocked["code"], "session_active")
        env.mi("pick", "lc-fx-counter", "--replace")

    def test_record_checks_case_names_and_error_fails_all(self):
        env = self.env
        env.mi("pick", "lc-fx-two-sum")
        env.mi("begin")
        out, _ = env.mi("record", "--mode", "visible")
        self.assertEqual(out["by_category"], {"visible": "1/1"})
        bad, code = env.mi("record", "--mode", "visible", "--failed", "edge-duplicates", expect_ok=False)
        self.assertEqual((bad["code"], code), ("unknown_case", 1))
        bad, _ = env.mi("record", "--got", "nope=1", expect_ok=False)
        self.assertEqual(bad["code"], "unknown_case")
        out, _ = env.mi("record", "--error", "SyntaxError: invalid syntax")
        self.assertEqual((out["passed"], out["error"]), (0, "SyntaxError: invalid syntax"))
        self.assertEqual(env.session()["current"]["last_run"]["failed"], out["total"])

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
        out, code = self.env.mi("tests", expect_ok=False)
        self.assertEqual((out["code"], code), ("no_session", 1))
        st, _ = self.env.mi("status")
        self.assertEqual(st["state"], "idle")

    def test_called_inside_work_folder_finds_the_project(self):
        self.env.mi("pick", "lc-fx-two-sum")
        self.env.mi("begin")
        work = os.path.join(self.env.project, ".mockinterview", "work")
        p = subprocess.run([sys.executable, os.path.join(self.env.plugin, "runner", "mi.py"), "--data", self.env.data,
                            "status"], capture_output=True, text=True, cwd=work, env=dict(os.environ, HOME=self.env.home))
        self.assertEqual(json.loads(p.stdout)["state"], "running")

    def test_data_value_with_unexpanded_variable_is_ignored(self):
        cmd = [sys.executable, MI, "--project", self.env.project, "--data", "${CLAUDE_PLUGIN_DATA}", "history"]
        p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, HOME=self.env.home))
        self.assertTrue(json.loads(p.stdout)["ok"])
        self.assertFalse(os.path.exists(os.path.join(self.env.project, "${CLAUDE_PLUGIN_DATA}")))


if __name__ == "__main__":
    unittest.main()
