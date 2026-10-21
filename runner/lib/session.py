"""Session file, history and state helpers."""
import json
import os
import random

from .util import MiError, atomic_write, iso, now_utc, parse_iso

SCHEMA = 1
ACTIVE = ("drawn", "running")


def new_session_id():
    return "%s-%04x" % (now_utc().strftime("%Y%m%dT%H%M%SZ"), random.SystemRandom().randrange(0x10000))


def load(ctx, required=True):
    try:
        with open(ctx.session_path, encoding="utf-8") as fh:
            session = json.load(fh)
    except FileNotFoundError:
        if required:
            raise MiError("no session in this project; start one with draw (interview) or pick (practice)",
                          code="no_session")
        return None
    except ValueError as exc:
        raise MiError("session.json is not valid JSON: %s" % exc, code="bad_session", exit_code=2)
    return session


def save(ctx, session):
    sync_current(session)
    atomic_write(ctx.session_path, json.dumps(session, indent=2, ensure_ascii=False) + "\n")


def sync_current(session):
    if not session.get("loop"):
        session["current"] = None
        return
    r = session["loop"][min(session["round"], len(session["loop"]) - 1)]
    session["current"] = {
        "problem": r["problem"], "type": r["type"], "time_minutes": r["time_minutes"],
        "limit_seconds": r["time_minutes"] * 60, "title": r.get("title"),
        "started_at": r.get("started_at"), "hints_used": r.get("hints_used", []),
        "last_run": r.get("last_run"),
    }


def current_round(session):
    return session["loop"][min(session["round"], len(session["loop"]) - 1)]


def require_state(session, *states):
    if session["state"] not in states:
        raise MiError("this command needs session state %s, but the state is '%s'"
                      % (" or ".join(states), session["state"]), code="bad_state", state=session["state"])


def timing(round_entry, now=None):
    """Elapsed and remaining seconds of a started round (None before begin)."""
    if not round_entry.get("started_at"):
        return {"elapsed_seconds": None, "remaining_seconds": None, "over_time": False}
    now = now or now_utc()
    start = parse_iso(round_entry["started_at"])
    end = parse_iso(round_entry["finished_at"]) if round_entry.get("finished_at") else now
    elapsed = int((end - start).total_seconds())
    limit = round_entry["time_minutes"] * 60
    return {"elapsed_seconds": elapsed, "remaining_seconds": limit - elapsed, "over_time": elapsed > limit}


# -------------------------------------------------------------------- history

def history_read(ctx):
    out = []
    try:
        with open(ctx.history_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        continue  # a damaged line never blocks a session
    except FileNotFoundError:
        pass
    return out


def history_append(ctx, entry):
    os.makedirs(ctx.data, exist_ok=True)
    with open(ctx.history_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def gitignore_hint(ctx):
    path = os.path.join(ctx.project, ".gitignore")
    try:
        with open(path, encoding="utf-8") as fh:
            if ".mockinterview" in fh.read():
                return None
    except OSError:
        pass
    return "Add '.mockinterview/' to this project's .gitignore so practice files are not committed."
