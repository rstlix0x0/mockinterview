#!/usr/bin/env python3
"""mockinterview runner: sessions, problem selection, test results and scoring.

    python3 runner/mi.py [--project DIR] [--data DIR] [--root DIR] [--pretty] COMMAND [options]

Every command prints one JSON object. See docs/runner.md for the contract.
Exit codes: 0 success, 1 user/state error or a failing test, 2 internal error.
"""
import sys

if sys.version_info < (3, 11):  # before any other import
    sys.stdout.write('{"ok": false, "error": "Python 3.11 or newer is required", "code": "python_version"}\n')
    sys.exit(2)

import argparse  # noqa: E402
import os  # noqa: E402
import traceback  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib import commands  # noqa: E402
from lib.util import Ctx, MiError, emit  # noqa: E402


def add_globals(p, suppress=False):
    d = argparse.SUPPRESS if suppress else None
    p.add_argument("--project", default=d, help="project folder (default: current directory)")
    p.add_argument("--data", default=d, help="data folder (default: $CLAUDE_PLUGIN_DATA or ~/.mockinterview/data)")
    p.add_argument("--root", action="append", default=d, help="extra pack root (repeatable)")
    p.add_argument("--plugin-root", default=d, help="plugin root (default: parent of runner/)")
    p.add_argument("--pretty", action="store_true", default=d, help="indented JSON")


def add_toolchain(p):
    p.add_argument("--lang", help="the engineer's solution language, free text (default: python)")
    p.add_argument("--test-cmd", help="the command that runs the engineer's tests, e.g. 'go test ./...'")


def build_parser():
    ap = argparse.ArgumentParser(prog="mi.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_globals(ap)
    sub = ap.add_subparsers(dest="command", required=True)

    def cmd(name, fn, help_text):
        p = sub.add_parser(name, help=help_text)
        add_globals(p, suppress=True)
        p.set_defaults(fn=fn)
        return p

    p = cmd("list", commands.cmd_list, "list packs")
    p.add_argument("--type")
    p.add_argument("--level")
    p.add_argument("--tag")
    p.add_argument("--roots", action="store_true", help="also show roots, trust and overrides")
    p.add_argument("--search", help="word to look for in ids, titles and tags (and in the text of knowledge docs)")
    p.add_argument("--verbose", action="store_true", help="include path and source")

    p = cmd("show", commands.cmd_show, "print the engineer-facing text of a pack")
    p.add_argument("id")
    p.add_argument("--full", action="store_true", help="all sections (refused during an interview round)")

    cmd("status", commands.cmd_status, "session state and time")

    p = cmd("draw", commands.cmd_draw, "start an interview: draw a loop for a level")
    p.add_argument("--level", required=True)
    p.add_argument("--type")
    p.add_argument("--seed", type=int)
    add_toolchain(p)

    p = cmd("pick", commands.cmd_pick, "start a practice session on one problem")
    p.add_argument("id")
    p.add_argument("--replace", action="store_true", help="replace an unfinished practice session")
    add_toolchain(p)

    cmd("begin", commands.cmd_begin, "start the clock and reveal the statement")

    p = cmd("tests", commands.cmd_tests, "the current round's test cases with expected values, as JSON")
    p.add_argument("--all", action="store_true", help="also the edge and hidden cases (default: visible only)")

    p = cmd("record", commands.cmd_record, "record the result of running the engineer's tests")
    p.add_argument("--mode", choices=("visible", "all"), default="all", help="which case set was run")
    p.add_argument("--failed", default="", help="comma-separated names of the failing cases (empty: all passed)")
    p.add_argument("--got", action="append", help="NAME=VALUE: what a failing case returned (repeatable)")
    p.add_argument("--error", help="the build or run failed before any case ran: its output (all cases fail)")

    cmd("hint", commands.cmd_hint, "give the next hint rung and record its cost")

    p = cmd("notes", commands.cmd_notes, "interviewer notes for the current round")
    p.add_argument("--section", choices=("clarify", "followups", "traps", "reference", "all"), default="all")
    p.add_argument("--problem", help="a problem id of this session (default: the current round)")

    cmd("finish", commands.cmd_finish, "finish the current round")

    p = cmd("score", commands.cmd_score, "score a finished session from a ratings file")
    p.add_argument("--ratings", required=True, help="ratings JSON file, or - for stdin")

    cmd("abandon", commands.cmd_abandon, "end the session without scoring (logged)")

    p = cmd("history", commands.cmd_history, "past sessions and per-tag averages")
    p.add_argument("--last", type=int, default=10)

    p = cmd("repeat", commands.cmd_repeat, "mark a problem to repeat, or list the marks")
    p.add_argument("id", nargs="?")
    p.add_argument("--reason")
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--list", action="store_true", help="list marked problems and which are due")

    p = cmd("lint", commands.cmd_lint, "validate pack files")
    p.add_argument("paths", nargs="*")
    p.add_argument("--all", action="store_true")

    p = cmd("selftest", commands.cmd_selftest, "check each pack's expected values against its reference solution")
    p.add_argument("ids", nargs="*")
    p.add_argument("--all", action="store_true")
    p.add_argument("--write-expected", action="store_true",
                   help="first set every case's expected value from the reference solution (rewrites the pack)")
    p.add_argument("--verbose", action="store_true")

    p = cmd("estimate-check", commands.cmd_estimate_check, "check work/estimate.json against the reference")
    p.add_argument("--tol", type=float, default=1.5)
    p.add_argument("--band", type=float, default=10.0)
    p.add_argument("--show-reference", action="store_true")

    cmd("design-lint", commands.cmd_design_lint, "structure check of work/design.md")
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    pretty = bool(getattr(args, "pretty", False))
    try:
        ctx = Ctx(project=getattr(args, "project", None), data=getattr(args, "data", None),
                  roots=getattr(args, "root", None), plugin_root=getattr(args, "plugin_root", None))
        result = args.fn(ctx, args)
    except MiError as exc:
        out = {"ok": False, "error": exc.message, "code": exc.code}
        out.update(exc.extra)
        emit(out, pretty)
        return exc.exit_code
    except Exception as exc:  # internal error: never a stack trace on stdout
        detail = traceback.format_exc() if os.environ.get("MI_DEBUG") else None
        emit({"ok": False, "error": "internal error: %s: %s" % (type(exc).__name__, exc), "code": "internal",
              **({"traceback": detail} if detail else {})}, pretty)
        return 2
    emit(result, pretty)
    if result.get("ok") and result.get("pass") is False and args.command in ("selftest", "lint"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
