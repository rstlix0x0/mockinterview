"""Check a pack's stored expected values against its reference solution (`selftest`). Standard library only.

This is the only place the runner executes pack code, and only when an author asks for it: a session never
runs the reference, and the engineer's code runs in their own toolchain, started by the agent.
"""
import copy
import json

from .util import MiError, short


def same(a, b, mode):
    """Compare two JSON values. `approx` allows a relative error of 1e-4 on numbers."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if mode == "approx":
            return abs(a - b) <= 1e-4 * max(1.0, abs(a), abs(b))
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y, mode) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k], mode) for k in a)
    return a == b


def load(pack):
    src = pack.reference_source()
    if not src:
        raise MiError("pack %s has no reference solution" % pack.id, code="no_reference")
    ns = {"__name__": "reference_" + pack.id.replace("-", "_")}
    exec(compile(src, "reference_" + pack.id, "exec"), ns)
    return ns


def call(ns, suite, args):
    """The reference's answer for one case, as JSON."""
    args = copy.deepcopy(args)
    if suite["kind"] == "func":
        out = ns["solve"](**args)
    else:
        obj, out = None, []
        for i, (name, a) in enumerate(args["calls"]):
            if i == 0:
                obj = ns[suite["function"]](*a)
                out.append(None)
            else:
                out.append(getattr(obj, name)(*a))
    return json.loads(json.dumps(out))


def selftest(pack):
    """{"passed", "total", "failures": [{"name", "expected", "got"}]} for every case of the pack."""
    suite = pack.suite()
    ns = load(pack)
    mode = suite.get("compare", "exact")
    failures, passed = [], 0
    for case in suite["cases"]:
        try:
            got = call(ns, suite, case["args"])
        except Exception as exc:  # the reference is the thing under test here
            failures.append({"name": case["name"], "error": "%s: %s" % (type(exc).__name__, exc)})
            continue
        if same(case.get("expected"), got, mode):
            passed += 1
        else:
            failures.append({"name": case["name"], "expected": short(case.get("expected")), "got": short(got)})
    return {"passed": passed, "total": len(suite["cases"]), "failures": failures}


def tests_block(suite):
    """The ```json tests fence for a suite: the header on the first line, then one case per line."""
    head = {k: suite[k] for k in ("function", "kind", "compare") if k in suite}
    lines = [json.dumps(c, separators=(",", ":"), ensure_ascii=False) for c in suite["cases"]]
    return "```json tests\n%s,\"cases\":[\n%s\n]}\n```" % (json.dumps(head, separators=(",", ":"))[:-1],
                                                          ",\n".join(lines))


def write_expected(pack):
    """Set every case's `expected` to the reference's answer and rewrite the pack file. Returns the count."""
    suite = pack.suite()
    ns = load(pack)
    for case in suite["cases"]:
        value = call(ns, suite, case["args"])
        case.pop("expected", None)
        case["expected"] = value
    with open(pack.path, encoding="utf-8") as fh:
        text = fh.read()
    start = text.index("```json tests")
    end = text.index("\n```", start) + 4
    with open(pack.path, "w", encoding="utf-8") as fh:
        fh.write(text[:start] + tests_block(suite) + text[end:])
    return len(suite["cases"])
