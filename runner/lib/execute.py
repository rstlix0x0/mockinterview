"""Run a solution file against a pack's tests. Standard library only.

Each case runs in its own Python subprocess (argv list, no shell) with a wall-clock timeout and, on POSIX,
CPU and address-space limits. Expected values come from the pack's oracle, which runs inside this process
(the oracle is trusted pack code; see Pack trust in docs/authoring.md).
"""
import bisect
import copy
import heapq
import itertools
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, OrderedDict, defaultdict, deque
from fractions import Fraction

from .util import MiError, atomic_write, short

try:  # POSIX only
    import resource
except ImportError:  # pragma: no cover
    resource = None

CASE_TIMEOUT = 10.0
MEMORY_BYTES = 2 * 1024 ** 3
SHOW_LIMIT = 3


def rand_ops(rnd, ctor, n, makers):
    """Random call sequence for class problems. makers: list of (weight, lambda rnd -> (method, *args))."""
    calls = [list(ctor[:1]) + [list(ctor[1:])]]
    weights = [w for w, _ in makers]
    for _ in range(n):
        _, mk = rnd.choices(makers, weights=weights)[0]
        c = mk(rnd)
        calls.append([c[0], list(c[1:])])
    return {"calls": calls}


def oracle_namespace():
    return dict(random=random, re=re, sys=sys, heapq=heapq, bisect=bisect, math=math, itertools=itertools,
                defaultdict=defaultdict, deque=deque, Counter=Counter, OrderedDict=OrderedDict,
                Fraction=Fraction, rand_ops=rand_ops)


def load_oracle(pack):
    src = pack.oracle_source()
    if not src:
        raise MiError("pack %s has no oracle" % pack.id, code="no_oracle")
    ns = oracle_namespace()
    exec(compile(src, "oracle_" + pack.id, "exec"), ns)
    return ns


def same(a, b, mode):
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


def oracle_expected(ns, suite, args):
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


def _limits(timeout):
    def apply():
        if resource is None:
            return
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (int(timeout) + 2, int(timeout) + 3))
        except (ValueError, OSError):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
        except (ValueError, OSError):
            pass  # macOS often refuses RLIMIT_AS; the timeout still applies
    return apply


def run_case(ctx, pyfile, suite, args, timeout):
    """Return (ok, value, error text, seconds)."""
    req = {"function": suite["function"]}
    req.update(args if suite["kind"] == "ops" else {"args": args})
    shim = os.path.join(ctx.runner_dir, "tools", "py_shim.py")
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "LC_ALL", "SYSTEMROOT", "TMPDIR")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    kwargs = {}
    if os.name == "posix" and getattr(ctx, "limits", True):
        kwargs["preexec_fn"] = _limits(timeout)
    t0 = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, shim, pyfile], input=json.dumps(req), capture_output=True,
                           text=True, timeout=timeout, env=env, cwd=os.path.dirname(pyfile) or None, **kwargs)
    except subprocess.TimeoutExpired:
        return False, None, "TIMEOUT after %.1fs" % timeout, time.perf_counter() - t0
    dt = time.perf_counter() - t0
    if p.returncode != 0:
        return False, None, "exit code %d: %s" % (p.returncode, (p.stderr or p.stdout).strip()[-400:]), dt
    try:
        return True, json.loads(p.stdout), "", dt
    except ValueError:
        return False, None, "stdout is not valid JSON: %r" % p.stdout[:200], dt


def run_suite(ctx, pack, pyfile, mode="all", perf=False, fuzz=None, seed=10000, factor=1.0,
              timeout=CASE_TIMEOUT, interview=False):
    """Run the tests of one live-coding pack. Returns the `run` result dict."""
    suite = pack.suite()
    ns = load_oracle(pack)
    cmode = suite.get("compare", "exact")
    wanted = {"visible"} if mode == "visible" else {"visible", "edge", "hidden"}
    stats = {}
    failures = []
    t_start = time.perf_counter()
    perf_info = {"ran": False}

    def note_failure(name, tag, args, expected, got_text):
        shown = (not interview) or tag == "visible"
        shown = shown and sum(1 for f in failures if f["shown"]) < SHOW_LIMIT
        entry = {"name": name, "category": tag, "shown": shown}
        if shown:
            entry.update(args=short(args), expected=short(expected), got=got_text)
        failures.append(entry)

    for case in suite["cases"]:
        tag = case["tags"][0]
        if tag not in wanted:
            continue
        expected = oracle_expected(ns, suite, case["args"])
        ok, got, err, _dt = run_case(ctx, pyfile, suite, case["args"], timeout * factor)
        good = ok and same(expected, got, cmode)
        s = stats.setdefault(tag, [0, 0])
        s[1] += 1
        s[0] += 1 if good else 0
        if not good:
            note_failure(case["name"], tag, case["args"], expected, short(got) if ok else err)

    n_fuzz = 0 if mode == "visible" else (suite.get("fuzz", 0) if fuzz is None else fuzz)
    if n_fuzz:
        s = stats.setdefault("fuzz", [0, 0])
        for sd in range(seed, seed + n_fuzz):
            args = ns["gen_random"](sd)
            expected = oracle_expected(ns, suite, args)
            ok, got, err, _dt = run_case(ctx, pyfile, suite, args, timeout * factor)
            good = ok and same(expected, got, cmode)
            s[1] += 1
            s[0] += 1 if good else 0
            if not good:
                note_failure("fuzz seed=%d" % sd, "fuzz", args, expected, short(got) if ok else err)
                break

    if perf and mode != "visible" and suite.get("perf"):
        perf_info = _run_perf(ctx, pack, pyfile, suite, ns, cmode, factor, timeout)
        s = stats.setdefault("perf", [0, 0])
        s[1] += 1
        s[0] += 1 if perf_info["ok"] else 0

    passed = sum(v[0] for v in stats.values())
    total = sum(v[1] for v in stats.values())
    return {
        "problem": pack.id, "passed": passed, "failed": total - passed, "total": total,
        "by_category": {k: "%d/%d" % (v[0], v[1]) for k, v in stats.items()},
        "perf": perf_info, "failures": failures,
        "details_policy": ("interview: only visible failures are shown" if interview
                           else "practice: details for up to %d failing cases" % SHOW_LIMIT),
        "elapsed_seconds": round(time.perf_counter() - t_start, 2),
    }


def _run_perf(ctx, pack, pyfile, suite, ns, cmode, factor, timeout):
    p = suite["perf"]
    os.makedirs(ctx.perf_cache, exist_ok=True)
    base_args = suite["cases"][0]["args"]
    base = min(run_case(ctx, pyfile, suite, base_args, timeout * factor)[3] for _ in range(3))
    times, lines, perf_ok = [], [], True
    for n in p["sizes"]:
        cache = os.path.join(ctx.perf_cache, "%s_%d.json" % (pack.id, n))
        cached = None
        if os.path.exists(cache):
            try:
                with open(cache, encoding="utf-8") as fh:
                    cached = json.load(fh)
            except (OSError, ValueError):
                cached = None
        if cached:
            args, exp = cached
        else:
            args = ns["gen_perf"](n)
            exp = oracle_expected(ns, suite, args)
            try:
                atomic_write(cache, json.dumps([args, exp]))
            except OSError:
                pass
        limit = p["limit_ms"] / 1000.0 * factor
        ok, got, err, dt = run_case(ctx, pyfile, suite, args, limit + base + 5)
        net = max(dt - base, 0.0)
        good = ok and same(exp, got, cmode)
        times.append(net)
        if good and net <= limit:
            status = "ok"
        elif ok and not good:
            status = "WRONG ANSWER"
        elif good:
            status = "TOO SLOW"
        else:
            status = err
        if status != "ok":
            perf_ok = False
        lines.append("n=%d %.0f ms (limit %d ms) %s" % (n, net * 1000, limit * 1000, status))
    me = p.get("max_exponent")
    if perf_ok and me and len(times) >= 2 and times[0] >= 0.05 and times[-1] > 0:
        e = math.log(times[-1] / times[0]) / math.log(p["sizes"][-1] / p["sizes"][0])
        lines.append("growth exponent ~ %.2f (allowed %.2f)" % (e, me))
        if e > me:
            perf_ok = False
            lines.append("the running time grows faster than the expected complexity class")
    return {"ran": True, "ok": perf_ok, "lines": lines}


_HEADER = (
    "import random, re, sys, heapq, bisect, math, itertools\n"
    "from collections import defaultdict, deque, Counter, OrderedDict\n"
    "from fractions import Fraction\n\n"
)


def selftest_pack(ctx, pack, fuzz=None, perf=False, factor=1.0):
    """Run the oracle as if it were the candidate's solution. Returns the run result."""
    src = pack.oracle_source()
    if not src:
        raise MiError("pack %s has no oracle" % pack.id, code="no_oracle")
    suite = pack.suite()
    body = _HEADER + src + "\n"
    if suite["kind"] == "func" and suite["function"] != "solve":
        body += "\n%s = solve\n" % suite["function"]
    with tempfile.TemporaryDirectory(prefix="mi-selftest-") as tmp:
        path = os.path.join(tmp, "solution.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        return run_suite(ctx, pack, path, mode="all", perf=perf, fuzz=fuzz, factor=factor)
