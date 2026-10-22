"""One function per CLI command. Each returns a dict (the JSON result) or raises MiError."""
import datetime
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

from . import draw as drawmod
from . import packs, reference, score as scoremod, session as sess
from .packs import LEVELS, PackError
from .util import MiError, atomic_write, iso, now_utc, short

PACK_TYPES = ("live-coding", "system-design")


# ---------------------------------------------------------------- shared bits

def _rel(ctx, path):
    try:
        return os.path.relpath(path, ctx.project)
    except ValueError:
        return path


def _get_pack(index, pid):
    pack = index.packs.get(pid)
    if pack is None:
        raise MiError("no pack with id '%s'; use list to see ids" % pid, code="not_found")
    return pack


def _runnable(ctx, pack):
    """Raise MiError if the pack must not be used for a session."""
    if pack.type not in PACK_TYPES:
        raise MiError("pack '%s' is a %s pack; only live-coding and system-design packs can be practised"
                      % (pack.id, pack.type), code="bad_type")
    errors, _warnings = packs.lint_pack(pack)
    if errors:
        raise MiError("pack '%s' has lint errors: %s" % (pack.id, "; ".join(errors[:3])), code="bad_pack")


def _interview_hidden(session):
    return bool(session) and session.get("mode") == "interview" and session.get("state") in sess.ACTIVE


def _new_round(pack, reveal_title):
    return {"problem": pack.id, "type": pack.type, "time_minutes": pack.time_minutes,
            "title": pack.title if reveal_title else None, "started_at": None, "finished_at": None,
            "hints_used": [], "last_run": None, "result": None}


def _guard_new_session(ctx, existing, replace=False):
    if existing is None:
        return
    state = existing.get("state")
    if state in sess.ACTIVE:
        if existing.get("mode") == "interview" or not replace:
            raise MiError("a %s session is already %s; finish it or run abandon (abandoning is logged, "
                          "and there is no re-draw)" % (existing.get("mode"), state), code="session_active")
    elif state == "finished" and not replace:
        raise MiError("the last session is finished but not scored; run score, or abandon", code="unscored")


def _toolchain(a):
    """Session fields for the engineer's language and test command: free text, never run by the runner."""
    lang = " ".join((a.lang or "").split()) or "python"
    cmd = " ".join((a.test_cmd or "").split()) or None
    return {"language": lang, "test_command": cmd}


# ------------------------------------------------------------- list, show, status

def cmd_list(ctx, a):
    index = packs.build_index(ctx)
    needle = (a.search or "").strip().lower()
    items = []
    for pack in sorted(index.packs.values(), key=lambda p: (p.type or "", p.id)):
        if a.type and pack.type != a.type:
            continue
        if a.level and a.level not in pack.levels:
            continue
        if a.tag and a.tag not in pack.tags:
            continue
        hits = 0
        if needle:
            head = " ".join([pack.id or "", pack.title or ""] + [str(t) for t in pack.tags]).lower()
            hits = pack.raw_body.lower().count(needle) if pack.type == "knowledge" else 0
            if needle not in head and not hits:
                continue
        item = pack.summary()
        if not (a.verbose or a.roots):
            item.pop("path", None)
            item.pop("source", None)
        if needle and pack.type == "knowledge":
            item["body_hits"] = hits
        items.append(item)
    if needle:
        items.sort(key=lambda i: -i.get("body_hits", 0))
    out = {"ok": True, "count": len(items), "packs": items}
    if index.warnings:
        out["warnings"] = index.warnings
    if a.roots:
        out["roots"] = index.roots
        out["overrides"] = index.overrides
    return out


def cmd_show(ctx, a):
    session = sess.load(ctx, required=False)
    if _interview_hidden(session):
        raise MiError("problems are hidden while an interview round is in progress; read "
                      ".mockinterview/work/PROBLEM.md", code="hidden_during_interview")
    index = packs.build_index(ctx)
    pack = _get_pack(index, a.id)
    if a.full or pack.type == "knowledge":
        text = pack.raw_body.strip("\n")
    else:
        parts = [pack.sections[n] for n in ("statement", "self-check questions") if pack.sections.get(n)]
        text = "\n\n".join(parts)
    return {"ok": True, "id": pack.id, "title": pack.title, "type": pack.type, "level": pack.levels,
            "tags": pack.tags, "time_minutes": pack.time_minutes, "full": bool(a.full), "text": text}


def cmd_status(ctx, a):
    session = sess.load(ctx, required=False)
    if session is None:
        return {"ok": True, "state": "idle"}
    rnd = sess.current_round(session)
    out = {"ok": True, "session_id": session["session_id"], "state": session["state"], "mode": session["mode"],
           "level": session.get("level"), "round": session["round"] + 1, "round_number": session["round"] + 1,
           "rounds_total": session["rounds_total"], "type": rnd["type"], "time_minutes": rnd["time_minutes"],
           "title": rnd.get("title"), "started_at": rnd.get("started_at"),
           "hints_used": rnd.get("hints_used", []), "has_run": rnd.get("last_run") is not None,
           "language": session.get("language"), "test_command": session.get("test_command")}
    out.update(sess.timing(rnd))
    return out


# ----------------------------------------------------------------- draw and pick

def cmd_draw(ctx, a):
    if a.level not in LEVELS:
        raise MiError("level must be one of: %s" % ", ".join(LEVELS), code="bad_level")
    if a.type and a.type not in PACK_TYPES:
        raise MiError("type must be one of: %s" % ", ".join(PACK_TYPES), code="bad_type")
    _guard_new_session(ctx, sess.load(ctx, required=False))
    index = packs.build_index(ctx)
    skipped = []

    def eligible(pack):
        try:
            errors, _w = packs.lint_pack(pack)
        except Exception as exc:  # a broken pack never blocks a draw
            errors = [str(exc)]
        if errors:
            skipped.append("%s: %s" % (pack.id, errors[0]))
            return False
        return True

    seed = a.seed if a.seed is not None else random.SystemRandom().randrange(1, 2 ** 31)
    history = sess.history_read(ctx)
    chosen, warnings = drawmod.build_loop(index, a.level, history, seed, a.type, eligible)
    if not chosen:
        raise MiError("no problems are available for level '%s'. %s" % (a.level, "; ".join(warnings)),
                      code="empty_pool")
    if skipped:
        warnings.append("skipped %d invalid pack(s), for example: %s" % (len(skipped), skipped[0]))
    lang_fields = _toolchain(a)
    session = {
        "schema": sess.SCHEMA, "session_id": sess.new_session_id(), "mode": "interview", "level": a.level,
        "state": "drawn", "seed": seed, "round": 0, "rounds_total": len(chosen), **lang_fields,
        "loop": [_new_round(p, reveal_title=False) for p in chosen], "current": None, "scorecard": None,
        "created_at": iso(now_utc()),
    }
    os.makedirs(ctx.mi_dir, exist_ok=True)
    sess.save(ctx, session)
    out = {"ok": True, "session_id": session["session_id"], "mode": "interview", "level": a.level,
           "seed": seed, "rounds_total": len(chosen),
           "rounds": [{"round": i + 1, "type": r["type"], "time_minutes": r["time_minutes"]}
                      for i, r in enumerate(session["loop"])], "state": "drawn", **lang_fields}
    if warnings:
        out["warnings"] = warnings
    hint = sess.gitignore_hint(ctx)
    if hint:
        out["hint"] = hint
    return out


def cmd_pick(ctx, a):
    _guard_new_session(ctx, sess.load(ctx, required=False), replace=a.replace)
    index = packs.build_index(ctx)
    pack = _get_pack(index, a.id)
    _runnable(ctx, pack)
    lang_fields = _toolchain(a)
    session = {
        "schema": sess.SCHEMA, "session_id": sess.new_session_id(), "mode": "practice", "level": None,
        "state": "drawn", "seed": None, "round": 0, "rounds_total": 1, **lang_fields,
        "loop": [_new_round(pack, reveal_title=True)], "current": None, "scorecard": None,
        "created_at": iso(now_utc()),
    }
    os.makedirs(ctx.mi_dir, exist_ok=True)
    sess.save(ctx, session)
    out = {"ok": True, "session_id": session["session_id"], "mode": "practice", "problem": pack.id,
           "title": pack.title, "type": pack.type, "time_minutes": pack.time_minutes, "state": "drawn",
           **lang_fields}
    hint = sess.gitignore_hint(ctx)
    if hint:
        out["hint"] = hint
    return out


# ---------------------------------------------------------------------- begin

def _fresh_work_dir(ctx):
    """Move everything in work/ (but archive/) to work/archive/<time>/ so each round starts empty."""
    os.makedirs(ctx.work_dir, exist_ok=True)
    entries = sorted(e for e in os.listdir(ctx.work_dir) if e != "archive")
    if not entries:
        return None
    dest = os.path.join(ctx.work_dir, "archive", now_utc().strftime("%Y%m%dT%H%M%SZ"))
    n = 1
    while os.path.exists(dest):
        n += 1
        dest = os.path.join(ctx.work_dir, "archive", now_utc().strftime("%Y%m%dT%H%M%SZ") + "-%d" % n)
    os.makedirs(dest)
    for e in entries:
        shutil.move(os.path.join(ctx.work_dir, e), os.path.join(dest, e))
    return dest


def cmd_begin(ctx, a):
    session = sess.load(ctx)
    sess.require_state(session, "drawn")
    rnd = sess.current_round(session)
    index = packs.build_index(ctx)
    pack = _get_pack(index, rnd["problem"])
    _runnable(ctx, pack)
    statement = (pack.section("statement") or "").strip()
    now = now_utc()
    rnd["title"] = pack.title
    rnd["started_at"] = iso(now)
    session["state"] = "running"
    archived = _fresh_work_dir(ctx)
    files = {"work_dir": _rel(ctx, ctx.work_dir)}
    out_extra = {}
    if pack.type == "live-coding":
        signature = pack.signature() or ""
        out_extra = {"signature": signature, "language": session.get("language"),
                     "test_command": session.get("test_command")}
        statement += "\n\n**Types** (`int[]` is a list of ints, `T?` may be null; use your language's names):\n\n" \
                     "```\n%s\n```" % signature
        work_note = ("Language: %s. Write your solution and its tests in `%s`, with your own editor and toolchain. "
                     "The interviewer sets up the stub and a test file with the visible cases; ask them to run "
                     "your tests when you are ready." % (session.get("language") or "python", files["work_dir"]))
    else:
        with open(os.path.join(ctx.runner_dir, "templates", "design-template.md"), encoding="utf-8") as fh:
            template = fh.read()
        target = os.path.join(ctx.work_dir, "design.md")
        atomic_write(target, template)
        files["design"] = _rel(ctx, target)
        work_note = ("Work file: `%s` (optional written design). You can also talk it through. Put estimation "
                     "claims in `.mockinterview/work/estimate.json` if you want them checked." % files["design"])
    problem_md = "# %s\n\n_%s, %d minutes. Round %d of %d._\n\n%s\n\n---\n%s\n" % (
        pack.title, pack.type, pack.time_minutes, session["round"] + 1, session["rounds_total"],
        statement, work_note)
    atomic_write(os.path.join(ctx.work_dir, "PROBLEM.md"), problem_md)
    sess.save(ctx, session)
    out = {"ok": True, "problem": pack.id, "title": pack.title, "type": pack.type,
           "time_minutes": pack.time_minutes, "limit_seconds": pack.time_minutes * 60,
           "started_at": rnd["started_at"], "round_number": session["round"] + 1,
           "rounds_total": session["rounds_total"], "statement": pack.section("statement") or "", "files": files,
           "problem_file": _rel(ctx, os.path.join(ctx.work_dir, "PROBLEM.md")), "state": "running", **out_extra}
    if archived:
        out["archived_previous"] = _rel(ctx, archived)
    return out


# --------------------------------------------------------------- tests, record

SHOW_LIMIT = 3


def _coding_round(ctx):
    session = sess.load(ctx)
    sess.require_state(session, "running")
    rnd = sess.current_round(session)
    if rnd["type"] != "live-coding":
        raise MiError("tests are for live-coding problems; use estimate-check or design-lint for design problems",
                      code="bad_type")
    pack = _get_pack(packs.build_index(ctx), rnd["problem"])
    return session, rnd, pack


def _case_set(suite, everything):
    wanted = {"visible", "edge", "hidden"} if everything else {"visible"}
    return [c for c in suite["cases"] if c["tags"][0] in wanted]


def cmd_tests(ctx, a):
    session, _rnd, pack = _coding_round(ctx)
    suite = pack.suite()
    cases = [{"name": c["name"], "category": c["tags"][0], "args": c["args"], "expected": c.get("expected")}
             for c in _case_set(suite, a.all)]
    out = {"ok": True, "problem": pack.id, "function": suite["function"], "kind": suite["kind"],
           "compare": suite.get("compare", "exact"), "signature": pack.signature(),
           "language": session.get("language"), "test_command": session.get("test_command"),
           "set": "all" if a.all else "visible", "count": len(cases), "cases": cases}
    if a.all and session["mode"] == "interview":
        out["policy"] = "interview: do not show edge or hidden cases to the engineer; report only their counts"
    return out


def _names(text):
    return [n.strip() for n in (text or "").split(",") if n.strip()]


def cmd_record(ctx, a):
    session, rnd, pack = _coding_round(ctx)
    suite = pack.suite()
    cases = _case_set(suite, a.mode == "all")
    by_name = {c["name"]: c for c in cases}
    failed = _names(a.failed)
    unknown = [n for n in failed if n not in by_name]
    if unknown:
        raise MiError("not a case of the %s set: %s" % (a.mode, ", ".join(unknown)), code="unknown_case",
                      cases=sorted(by_name))
    got = {}
    for item in a.got or []:
        name, sep, value = item.partition("=")
        if not sep or name.strip() not in by_name:
            raise MiError("--got needs NAME=VALUE with a case name of the %s set: %s" % (a.mode, item),
                          code="unknown_case")
        got[name.strip()] = value.strip()
    error = (a.error or "").strip() or None
    if error:
        failed = list(by_name)
    interview = session["mode"] == "interview"
    stats, failures = {}, []
    for c in cases:
        tag = c["tags"][0]
        s = stats.setdefault(tag, [0, 0])
        s[1] += 1
        if c["name"] not in failed:
            s[0] += 1
            continue
        shown = (not interview or tag == "visible") and sum(1 for f in failures if f["shown"]) < SHOW_LIMIT
        entry = {"name": c["name"], "category": tag, "shown": shown}
        if shown:
            entry.update(args=short(c["args"]), expected=short(c.get("expected")))
            if c["name"] in got:
                entry["got"] = got[c["name"]][:240]
        failures.append(entry)
    passed = sum(v[0] for v in stats.values())
    total = sum(v[1] for v in stats.values())
    result = {"problem": pack.id, "mode": a.mode, "passed": passed, "failed": total - passed, "total": total,
              "by_category": {k: "%d/%d" % (v[0], v[1]) for k, v in stats.items()}, "failures": failures,
              "details_policy": ("interview: only visible failures are shown" if interview
                                 else "practice: details for up to %d failing cases" % SHOW_LIMIT),
              "recorded_at": iso(now_utc())}
    if error:
        result["error"] = error[-2000:]
    rnd["last_run"] = result
    sess.save(ctx, session)
    out = {"ok": True, "pass": result["failed"] == 0, **result}
    out.update(sess.timing(rnd))
    return out


# ----------------------------------------------------------------------- hint

def cmd_hint(ctx, a):
    session = sess.load(ctx)
    sess.require_state(session, "running")
    rnd = sess.current_round(session)
    index = packs.build_index(ctx)
    pack = _get_pack(index, rnd["problem"])
    ladder = pack.ladder()
    used = rnd["hints_used"]
    idx = len(used)
    if idx > 3:
        raise MiError("all four rungs were already given", code="no_more_hints")
    if idx not in ladder:
        raise MiError("this problem has no rung %d in its notes" % idx, code="no_ladder")
    label, cost, text = ladder[idx]
    used.append({"rung": label, "cost": cost})
    sess.save(ctx, session)
    return {"ok": True, "rung": label, "cost": cost, "text": text,
            "penalty_total": scoremod.hint_penalty(rnd["type"], used), "rungs_left": 3 - idx}


# ---------------------------------------------------------------------- notes

_BLOCK_START = [
    re.compile(r"^#{3,6}\s+(.+?)\s*$"),
    re.compile(r"^[-*]\s+\*\*(.+?)\*\*"),
    re.compile(r"^\*\*(.+?)\*\*(?:\s*\(.*\))?\s*$"),
]
_CLASSES = [
    ("ladder", ("hint ladder", "probe ladder")),
    ("clarify", ("clarif",)),
    ("followups", ("follow-up", "followup", "follow up", "curveball", "deep-dive", "deep dive", "probe",
                   "failure inject", "failure injection")),
    ("traps", ("mistake", "trap", "calibration", "level")),
    ("reference", ("reference", "target complexity", "scaling check", "estimate")),
]


def _classify(title):
    low = title.lower()
    for name, keys in _CLASSES:
        if any(k in low for k in keys):
            return name
    return "other"


def _note_blocks(notes):
    blocks, current = [], None
    in_fence = False
    for line in notes.split("\n"):
        is_fence = line.startswith("```")
        if is_fence:
            in_fence = not in_fence
        title = None
        if not in_fence and not is_fence:
            for rx in _BLOCK_START:
                m = rx.match(line)
                if m:
                    title = m.group(1)
                    break
        if title is not None:
            current = {"title": title, "class": _classify(title), "lines": [line]}
            blocks.append(current)
        elif current is not None:
            current["lines"].append(line)
        else:
            if not blocks:
                current = {"title": "intro", "class": "other", "lines": [line]}
                blocks.append(current)
    # unclassified blocks (for example the lead-in paragraphs of a reference design) belong to the block before
    for i in range(1, len(blocks)):
        if blocks[i]["class"] == "other" and blocks[i - 1]["title"] != "intro":
            blocks[i]["class"] = blocks[i - 1]["class"]
    return blocks


def cmd_notes(ctx, a):
    session = sess.load(ctx)
    state = session["state"]
    if a.problem:
        entries = [(i, r) for i, r in enumerate(session["loop"]) if r["problem"] == a.problem]
        if not entries:
            raise MiError("problem '%s' is not part of this session" % a.problem, code="not_found")
        i, rnd = entries[0]
        allowed = (rnd.get("finished_at") is not None or state in ("finished", "scored")
                   or (i == session["round"] and state == "running"))
        if not allowed:
            raise MiError("notes for a round that has not started are not available", code="bad_state")
    else:
        sess.require_state(session, "drawn", "running", "finished", "scored")
        if session["mode"] == "interview" and state == "drawn":
            raise MiError("notes open after begin", code="bad_state")
        rnd = sess.current_round(session)
    index = packs.build_index(ctx)
    pack = _get_pack(index, rnd["problem"])
    blocks = _note_blocks(pack.notes())
    want = a.section
    chosen = [b for b in blocks if b["class"] != "ladder" and (want == "all" or b["class"] == want)]
    text = "\n".join("\n".join(b["lines"]).strip("\n") + "\n" for b in chosen).strip("\n")
    if want in ("reference", "all") and pack.type == "live-coding":
        src = pack.reference_source()
        if src:
            text += "\n\nReference solution (Python):\n\n```python\n%s\n```" % src
    out = {"ok": True, "problem": pack.id, "section": want, "text": text,
           "blocks": [b["title"] for b in chosen]}
    if not text.strip():
        out["warnings"] = ["no '%s' notes were found for this problem" % want]
    return out


# --------------------------------------------------------------------- finish

def cmd_finish(ctx, a):
    session = sess.load(ctx)
    sess.require_state(session, "running")
    rnd = sess.current_round(session)
    now = now_utc()
    rnd["finished_at"] = iso(now)
    tm = sess.timing(rnd, now)
    rnd["result"] = {"elapsed_seconds": tm["elapsed_seconds"], "over_time": tm["over_time"],
                     "hints_used": list(rnd["hints_used"]), "last_run": rnd["last_run"]}
    warnings = []
    if rnd["type"] == "live-coding" and rnd["last_run"] is None:
        warnings.append("no test result was recorded for this round; the implementation rating will be 0")
    finished_round = session["round"] + 1
    out = {"ok": True, "problem": rnd["problem"], "title": rnd.get("title"), "round_number": finished_round,
           "rounds_total": session["rounds_total"], "result": rnd["result"]}
    if session["round"] + 1 < session["rounds_total"]:
        session["round"] += 1
        session["state"] = "drawn"
        nxt = sess.current_round(session)
        out["next"] = {"round_number": session["round"] + 1, "type": nxt["type"],
                       "time_minutes": nxt["time_minutes"]}
    else:
        session["state"] = "finished"
        out["next"] = None
    out["state"] = session["state"]
    if warnings:
        out["warnings"] = warnings
    sess.save(ctx, session)
    return out


# ---------------------------------------------------------------------- score

def _read_ratings(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise MiError("ratings file is not valid JSON: %s" % exc, code="bad_ratings")
    if not isinstance(data, dict) or not isinstance(data.get("ratings"), dict):
        raise MiError("ratings JSON needs a 'ratings' object keyed by problem id", code="bad_ratings")
    return data


def cmd_score(ctx, a):
    session = sess.load(ctx)
    sess.require_state(session, "finished")
    data = _read_ratings(a.ratings)
    index = packs.build_index(ctx)
    rounds, scores = [], []
    for rnd in session["loop"]:
        pid = rnd["problem"]
        if pid not in data["ratings"]:
            raise MiError("no ratings for round problem '%s'" % pid, code="bad_ratings", problem=pid)
        result = rnd.get("result") or {}
        penalty = scoremod.hint_penalty(rnd["type"], rnd.get("hints_used", []))
        entry = scoremod.score_round(rnd["type"], data["ratings"][pid], penalty, result.get("last_run"),
                                     (data.get("evidence") or {}).get(pid))
        entry.update(problem=pid, title=rnd.get("title"), type=rnd["type"],
                     minutes=round((result.get("elapsed_seconds") or 0) / 60.0, 1),
                     over_time=bool(result.get("over_time")))
        rounds.append(entry)
        scores.append(entry["score"])
    total = round(sum(scores) / len(scores), 1)
    scorecard = {"total": total, "reading": scoremod.reading(total), "rounds": rounds,
                 "top_gap": data.get("top_gap")}
    session["scorecard"] = scorecard
    session["state"] = "scored"
    sess.save(ctx, session)
    hist_rounds = []
    for i, entry in enumerate(rounds):
        pack = index.packs.get(entry["problem"])
        item = {"problem": entry["problem"], "type": entry["type"], "title": entry["title"],
                "tags": pack.tags if pack else [], "score": entry["score"], "minutes": entry["minutes"],
                "hints": [h["rung"] for h in session["loop"][i]["hints_used"]]}
        if entry["score"] < 70:
            item["repeat_by"] = (now_utc() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        hist_rounds.append(item)
    sess.history_append(ctx, {"session_id": session["session_id"], "date": iso(now_utc()),
                              "mode": session["mode"], "level": session.get("level"), "state": "scored",
                              "total": total, "top_gap": data.get("top_gap"), "rounds": hist_rounds})
    return {"ok": True, "state": "scored", "scorecard": scorecard}


def cmd_abandon(ctx, a):
    session = sess.load(ctx)
    if session["state"] in ("scored", "abandoned"):
        raise MiError("the session is already %s" % session["state"], code="bad_state")
    index = packs.build_index(ctx)
    rounds = []
    for rnd in session["loop"]:
        pack = index.packs.get(rnd["problem"])
        rounds.append({"problem": rnd["problem"], "type": rnd["type"], "tags": pack.tags if pack else [],
                       "started": rnd.get("started_at") is not None})
    session["state"] = "abandoned"
    sess.save(ctx, session)
    sess.history_append(ctx, {"session_id": session["session_id"], "date": iso(now_utc()),
                              "mode": session["mode"], "level": session.get("level"), "state": "abandoned",
                              "rounds": rounds})
    return {"ok": True, "state": "abandoned"}


# -------------------------------------------------------------------- history

def cmd_history(ctx, a):
    entries = sess.history_read(ctx)
    tags = {}
    for entry in entries:
        if entry.get("state") != "scored":
            continue
        for r in entry.get("rounds", []):
            if "score" in r:
                for t in r.get("tags", []):
                    tags.setdefault(t, []).append(r["score"])
    summary = {t: {"avg": round(sum(v) / len(v), 1), "n": len(v)} for t, v in tags.items()}
    weak = sorted(summary, key=lambda t: summary[t]["avg"])[:5]
    due = []
    for entry in entries:
        for r in entry.get("rounds", []):
            if r.get("repeat_by"):
                due.append({"problem": r["problem"], "repeat_by": r["repeat_by"], "score": r.get("score")})
    last = entries[-a.last:] if a.last else entries
    return {"ok": True, "sessions": len(entries), "last": last, "tags": summary, "weak_tags": weak,
            "repeat": due[-10:]}


# ---------------------------------------------------------------- lint, selftest

def _collect_paths(paths):
    out = []
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.isdir(p):
            for dirpath, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                out += [os.path.join(dirpath, f) for f in sorted(files)
                        if f.endswith(".md") and f.upper() != "README.MD"]
        else:
            out.append(p)
    return out


def cmd_lint(ctx, a):
    if a.all:
        index = packs.build_index(ctx)
        targets = [(p.path, p) for p in index.packs.values()]
        results = [{"path": w["path"], "id": None, "ok": False, "errors": [w["message"]], "warnings": []}
                   for w in index.warnings]
    else:
        if not a.paths:
            raise MiError("give PATH... or --all", code="usage")
        targets, results = [], []
        for path in _collect_paths(a.paths):
            try:
                targets.append((path, packs.load_pack(path, os.path.dirname(path), "path")))
            except (PackError, OSError) as exc:
                results.append({"path": path, "id": None, "ok": False, "errors": [str(exc)], "warnings": []})
    for path, pack in sorted(targets, key=lambda t: t[0]):
        errors, warnings = packs.lint_pack(pack)
        results.append({"path": path, "id": pack.id, "ok": not errors, "errors": errors, "warnings": warnings})
    bad = [r for r in results if not r["ok"]]
    return {"ok": True, "checked": len(results), "failed": len(bad), "pass": not bad, "results": results}


def cmd_selftest(ctx, a):
    index = packs.build_index(ctx)
    if a.all or not a.ids:
        targets = [p for p in index.packs.values() if p.type == "live-coding"]
    else:
        targets = [_get_pack(index, i) for i in a.ids]
    targets.sort(key=lambda p: p.id)
    results = []
    for pack in targets:
        item = {"id": pack.id}
        results.append(item)
        if pack.type != "live-coding":
            item.update(skipped="no tests to check")
            continue
        if a.write_expected:
            try:
                item["written"] = reference.write_expected(pack)
            except (PackError, ValueError, OSError) as exc:
                item["pass"] = False
                item.update(errors=["cannot write expected values: %s" % exc])
                continue
            except Exception as exc:
                item["pass"] = False
                item.update(errors=["the reference solution crashed: %s: %s" % (type(exc).__name__, exc)])
                continue
            pack = packs.load_pack(pack.path, pack.root, pack.root_label)
        errors, _w = packs.lint_pack(pack)
        if errors:
            item.update(errors=errors)
            item["pass"] = False
            continue
        try:
            res = reference.selftest(pack)
        except Exception as exc:
            item["pass"] = False
            item.update(errors=["the reference solution crashed: %s: %s" % (type(exc).__name__, exc)])
            continue
        item["pass"] = not res["failures"]
        item.update(passed=res["passed"], total=res["total"])
        if res["failures"]:
            item["failures"] = res["failures"][:3]
    failed = [r for r in results if r.get("pass") is False]
    return {"ok": True, "checked": len(results), "failed": len(failed), "pass": not failed,
            "results": results if (failed or len(results) <= 5 or a.verbose) else
            [{"id": r["id"], "pass": r.get("pass"), "skipped": r.get("skipped")} for r in results]}


# --------------------------------------------------------------- design tools

def _design_session(ctx):
    session = sess.load(ctx)
    rnd = sess.current_round(session)
    if rnd["type"] != "system-design":
        raise MiError("this command is for system-design problems", code="bad_type")
    return session, rnd


def _run_tool(ctx, script, args):
    p = subprocess.run([sys.executable, os.path.join(ctx.runner_dir, "tools", script)] + args,
                       capture_output=True, text=True, timeout=60)
    return p.returncode, (p.stdout + p.stderr).strip()


def cmd_estimate_check(ctx, a):
    session, rnd = _design_session(ctx)
    index = packs.build_index(ctx)
    pack = _get_pack(index, rnd["problem"])
    ref = pack.reference_estimate()
    if ref is None:
        raise MiError("this problem has no reference estimate", code="no_reference")
    cand = os.path.join(ctx.work_dir, "estimate.json")
    if not os.path.exists(cand):
        raise MiError("write your claims to %s first" % _rel(ctx, cand), code="no_estimate")
    if a.show_reference and session["state"] == "running" and session["mode"] == "interview":
        raise MiError("the reference is shown only after the round", code="hidden_during_interview")
    with tempfile.TemporaryDirectory(prefix="mi-est-") as tmp:
        refpath = os.path.join(tmp, "reference.json")
        with open(refpath, "w", encoding="utf-8") as fh:
            json.dump(ref if "assumptions" in ref or "expected" in ref else {"assumptions": ref}, fh)
        args = ["check", refpath, cand, "--tol", str(a.tol), "--band", str(a.band)]
        if a.show_reference:
            args.append("--show-reference")
        code, output = _run_tool(ctx, "estimate.py", args)
    return {"ok": True, "pass": code == 0, "output": output}


def cmd_design_lint(ctx, a):
    _design_session(ctx)
    target = os.path.join(ctx.work_dir, "design.md")
    if not os.path.exists(target):
        raise MiError("no design file at %s" % _rel(ctx, target), code="no_design")
    code, output = _run_tool(ctx, "designlint.py", [target])
    return {"ok": True, "pass": code == 0, "output": output}


# ---------------------------------------------------------------------- repeat

def _repeat_path(ctx):
    return os.path.join(ctx.mi_dir, "repeat.md")


def cmd_repeat(ctx, a):
    path = _repeat_path(ctx)
    today = now_utc().strftime("%Y-%m-%d")
    if a.list:
        entries = []
        try:
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    parts = [x.strip() for x in line.strip().split("|")]
                    if len(parts) == 4 and parts[3].startswith("repeat after "):
                        after = parts[3][len("repeat after "):]
                        entries.append({"date": parts[0], "problem": parts[1], "reason": parts[2],
                                        "after": after, "due": after <= today})
        except FileNotFoundError:
            pass
        return {"ok": True, "today": today, "entries": entries, "due": [e for e in entries if e["due"]]}
    if not a.id or not a.reason:
        raise MiError("give a problem id and --reason, or --list", code="usage")
    index = packs.build_index(ctx)
    pack = _get_pack(index, a.id)
    after = (now_utc() + datetime.timedelta(days=a.days)).strftime("%Y-%m-%d")
    reason = " ".join(a.reason.replace("|", "/").split())
    os.makedirs(ctx.mi_dir, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("%s | %s | %s | repeat after %s\n" % (today, pack.id, reason, after))
    return {"ok": True, "problem": pack.id, "repeat_after": after, "file": _rel(ctx, path)}
