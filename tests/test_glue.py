"""Typed-language glue (runner/lib/glue) and the Go and Cargo manifest checks, imported directly.

These need no toolchain; the runner tests build and run real Go and Rust solutions when `go` or `cargo` is there.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runner"))

from lib import deps, glue, languages  # noqa: E402
from lib.signature import parse  # noqa: E402

TWO_SUM = parse("two_sum(nums: int[], target: int) -> int[]", "func")
COUNTER = parse("MiniCounter()\nadd(x: int) -> void\ntotal() -> int", "ops")
SCHEDULE = parse("schedule_tasks(tasks: record{id: string, deps: string[]}[], workers: int)"
                 " -> record{makespan?: int, error?: string}", "func")


class GlueTest(unittest.TestCase):
    def test_go_stubs(self):
        go = glue.get("go")
        self.assertEqual(go.stub(TWO_SUM, "func"),
                         "package main\n\nfunc twoSum(nums []int, target int) []int {\n\tpanic(\"not implemented\")\n}\n")
        stub = go.stub(COUNTER, "ops")
        self.assertIn("type MiniCounter struct {\n}\n\nfunc NewMiniCounter() *MiniCounter {\n\treturn &MiniCounter{}\n}\n",
                      stub)
        self.assertIn("func (m *MiniCounter) Add(x int) {\n", stub)
        self.assertIn("func (m *MiniCounter) Total() int {\n", stub)
        stub = go.stub(SCHEDULE, "func")
        self.assertIn("// ScheduleTasksResult, Task: defined in mi_main.go", stub)
        self.assertIn("func scheduleTasks(tasks []Task, workers int) ScheduleTasksResult {", stub)
        main = go.files(SCHEDULE, "func", "lc-x", lambda n: n)["mi_main.go"]
        self.assertIn("type ScheduleTasksResult struct {\n\tMakespan *int\n\tError    *string\n}", main)
        self.assertIn("type Task struct {\n\tId   string\n\tDeps []string\n}", main)

    def test_rust_stubs(self):
        rust = glue.get("rust")
        self.assertEqual(rust.stub(TWO_SUM, "func"),
                         "pub fn two_sum(nums: Vec<i64>, target: i64) -> Vec<i64> {\n    todo!()\n}\n")
        stub = rust.stub(COUNTER, "ops")
        self.assertIn("pub struct MiniCounter {\n}\n\nimpl MiniCounter {\n    pub fn new() -> Self {\n", stub)
        self.assertIn("    pub fn add(&mut self, x: i64) {\n        todo!()\n    }\n", stub)
        self.assertIn("    pub fn total(&mut self) -> i64 {\n", stub)
        stub = rust.stub(SCHEDULE, "func")
        self.assertIn("use crate::mi_types::*; // ScheduleTasksResult, Task", stub)
        types = rust.files(SCHEDULE, "func", "lc-x", lambda n: n)["src/mi_types.rs"]
        self.assertIn("pub struct ScheduleTasksResult {\n    pub makespan: Option<i64>,\n    pub error: Option<String>,\n}",
                      types)

    def test_structural_names_and_keywords(self):
        sig = parse("f(type: string, pairs: [string, int][]) -> {string: int | string}", "func")
        self.assertIn("func f(type_ string, pairs []TupleStringInt) map[string]any {", glue.get("go").stub(sig, "func"))
        self.assertIn("pub fn f(r#type: String, pairs: Vec<(String, i64)>) -> HashMap<String, IntOrString> {",
                      glue.get("rust").stub(sig, "func"))

    def test_unsupported_signatures(self):
        cases = [("go", "f() -> int[] | string", "unions of int, float, bool and string only"),
                 ("rust", "f() -> int[] | string[]", "members of different JSON kinds"),
                 ("rust", "f() -> int? | string", "write a nullable union as (A | B)?"),
                 ("go", "f() -> record{a?: int?}", "absent field from a null one"),
                 ("rust", "f() -> record{a?: int?}", "absent field from a null one"),
                 ("rust", "f() -> [int, int, int, int, int]", "tuples of up to 4 items")]
        for gen, text, message in cases:
            with self.assertRaises(glue.Unsupported) as cm:
                glue.get(gen).check(parse(text, "func"))
            self.assertIn(message, str(cm.exception), (gen, text))
        glue.get("go").check(parse("f() -> (int | string)?", "func"))
        glue.get("rust").check(parse("f() -> (int | string)?", "func"))

    def test_language_file_fields(self):
        base = {"id": "x", "name": "X", "solution": "x.go", "detect": ["go"], "run": ["{bin}", "{result}"]}
        self.assertEqual(languages.validate(dict(base, glue="go", build=["go", "build", "-o", "{bin}"])), [])
        self.assertIn("glue must be one of: go, rust", languages.validate(dict(base, glue="zig")))
        self.assertIn("build: unknown placeholder {result}",
                      languages.validate(dict(base, glue="go", build=["go", "{result}"])))
        self.assertIn("scaffold files must be paths inside work/",
                      languages.validate(dict(base, glue="go", scaffold={"../go.mod": ""})))
        self.assertIn("stub_func is required unless pack_stub = true or glue is set", languages.validate(base))


class ManifestTest(unittest.TestCase):
    def write(self, name, text):
        work = tempfile.mkdtemp(prefix="mi-glue-")
        self.addCleanup(lambda: __import__("shutil").rmtree(work, ignore_errors=True))
        with open(os.path.join(work, name), "w", encoding="utf-8") as fh:
            fh.write(text)
        return work

    def test_go_mod_requires(self):
        work = self.write("go.mod", "module solution\n\ngo 1.21\n\nrequire github.com/a/b v1.0.0 // indirect\n"
                                    "require (\n\tgolang.org/x/exp v0.1.0\n\t// comment\n\tgithub.com/c/d v2.0.0\n)\n")
        self.assertEqual(deps.check("go", "", work), ["github.com/a/b", "golang.org/x/exp", "github.com/c/d"])
        self.assertEqual(deps.check("go", "", self.write("go.mod", "module solution\n\ngo 1.21\n")), [])

    def test_cargo_dependencies(self):
        work = self.write("Cargo.toml", '[package]\nname = "mi_solution"\n\n[dependencies]\nitertools = "0.12"\n'
                                        '[dev-dependencies]\nrand = "0.8"\n'
                                        '[target.\'cfg(unix)\'.dependencies]\nlibc = "0.2"\n')
        self.assertEqual(deps.check("cargo", "", work), ["itertools", "rand", "libc"])
        self.assertEqual(deps.check("cargo", "", self.write("Cargo.toml", "[package]\nname = \"x\"\n[dependencies]\n")), [])


if __name__ == "__main__":
    unittest.main()
