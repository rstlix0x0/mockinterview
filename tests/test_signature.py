"""Signature grammar and value check (runner/lib/signature.py), imported directly."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runner"))

from lib.signature import SignatureError, check, check_call, fmt, parse  # noqa: E402


def ty(text):
    return parse("f(x: %s) -> int" % text, "func").params[0][1]


class SignatureTest(unittest.TestCase):
    def test_types_parse_and_print_back(self):
        for text in ("int", "float", "bool", "string", "int[][]", "int?[]", "string[]?", "[string, int][]",
                     "{string: int | string}", "(int | string)[]", "(int | string)?",
                     "record{id: string, deps: string[], error?: string}"):
            self.assertEqual(fmt(ty(text)), text)

    def test_func_and_ops_declarations(self):
        sig = parse("two_sum(nums: int[], target: int) -> int[]", "func")
        self.assertEqual((sig.name, [n for n, _t in sig.params], fmt(sig.returns)), ("two_sum", ["nums", "target"], "int[]"))
        sig = parse("# comment\nMinStack()\n\npush(x: int) -> void\nget_min() -> int\n", "ops")
        self.assertEqual(sig.name, "MinStack")
        self.assertEqual([m.name for m in sig.methods], ["push", "get_min"])
        self.assertEqual(sig.method("push").returns, ("void",))

    def test_grammar_errors(self):
        for text, kind, message in [
                ("f(x: int)", "func", "f needs a return type"),
                ("f(x: int) -> void", "func", "f needs a return type"),
                ("f() -> int\ng() -> int", "func", "one declaration, found 2"),
                ("C() -> int", "ops", "constructor and has no return type"),
                ("C()\nm()", "ops", "method m needs a return type"),
                ("C()\nm() -> int\nm() -> int", "ops", "method m appears twice"),
                ("f(x: int, x: int) -> int", "func", "parameter 'x' appears twice"),
                ("f(x: [int]) -> int", "func", "a tuple has two or more types"),
                ("f(x: {int: int}) -> int", "func", "map keys are strings"),
                ("f(x: void) -> int", "func", "void is only a method's return type"),
                ("f(x: int??) -> int", "func", "'??' is the same as '?'"),
                ("f(x: int) -> int extra", "func", "unexpected 'extra'"),
                ("f(x: int[) -> int", "func", "line 1: expected ',', found '['"),
                ("f(x: int", "func", "expected ')', found the end"),
                ("", "func", "the block is empty")]:
            with self.assertRaises(SignatureError) as cm:
                parse(text, kind)
            self.assertIn(message, str(cm.exception), text)

    def test_check_values(self):
        good = [(1, "int"), (2 ** 63 - 1, "int"), (1, "float"), (1.5, "float"), (None, "int?"), ([], "int[]"),
                ([1, None], "int?[]"), (["a", 1], "[string, int]"), ({"a": 1, "b": "x"}, "{string: int | string}"),
                ({"error": "x"}, "record{makespan?: int, error?: string}")]
        for value, text in good:
            self.assertIsNone(check(value, ty(text)), (value, text))
        bad = [(True, "int", "value: expected int, got bool true"),
               (2 ** 63, "int", "value: 9223372036854775808 does not fit a 64-bit int"),
               (True, "float", "value: expected float, got bool true"),
               ([1, "a"], "int[]", "value[1]: expected int, got string 'a'"),
               (["a"], "[string, int]", "value: expected 2 items, got 1"),
               ({"a": None}, "{string: int}", "value['a']: expected int, got null"),
               ({"x": 1}, "record{y?: int}", "value: key 'x' is not in record{y?: int}"),
               ({}, "record{y: int}", "value: key 'y' is missing"),
               ([1.5], "(int | string)[]", "value[0]: expected int | string, got float 1.5")]
        for value, text, message in bad:
            self.assertEqual(check(value, ty(text)), message)

    def test_check_call(self):
        sig = parse("f(a: int, b: string[]) -> bool", "func")
        self.assertIsNone(check_call(sig, "func", {"a": 1, "b": []}, True, "case 'x'"))
        self.assertEqual(check_call(sig, "func", {"a": 1}, True, "case 'x'"), "case 'x': argument 'b' is missing")
        self.assertEqual(check_call(sig, "func", {"a": 1, "b": [], "c": 0}, True, "case 'x'"),
                         "case 'x': argument 'c' is not in the signature")
        self.assertEqual(check_call(sig, "func", {"a": 1, "b": []}, 1, "case 'x'"),
                         "case 'x' result: expected bool, got int 1")
        sig = parse("C(n: int)\nput(k: string) -> void\nget(k: string) -> int?", "ops")
        calls = {"calls": [["C", [1]], ["put", ["a"]], ["get", ["a"]]]}
        self.assertIsNone(check_call(sig, "ops", calls, [None, None, 3], "case 'x'"))
        self.assertEqual(check_call(sig, "ops", calls, [None, 1, 3], "case 'x'"),
                         "case 'x' call 1 put() result: expected void, got int 1")
        self.assertEqual(check_call(sig, "ops", {"calls": [["C", [1]], ["pop", []]]}, [None, 1], "case 'x'"),
                         "case 'x' call 1: pop is not a method in the signature")
        self.assertEqual(check_call(sig, "ops", {"calls": [["C", ["1"]]]}, [None], "case 'x'"),
                         "case 'x' call 0 C(n): expected int, got string '1'")


if __name__ == "__main__":
    unittest.main()
