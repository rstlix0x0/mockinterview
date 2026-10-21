#!/usr/bin/env python3
"""Back-of-the-envelope calculator and estimate checker.

    python runner/tools/estimate.py calc  assumptions.json
    python runner/tools/estimate.py check REFERENCE.json work/estimate.json [--tol 1.5] [--band 10] [--show-reference]

assumptions.json (every key optional except the user count):
    {"dau": 100e6                      daily active users   (or "mau" and "dau_ratio")
     "writes_per_user_day": 0.1,       writes (creates) per active user per day
     "reads_per_user_day": 10,         reads per active user per day
     "bytes_per_write": 500,           bytes stored per write
     "bytes_per_read": 500,            bytes returned per read
     "peak_factor": 2,                 peak QPS = average QPS * peak_factor
     "retention_years": 5, "replication": 3,
     "new_data_fraction": 1.0,         share of written bytes that stay as NEW data (overwrites and compression lower it)
     "cache_fraction": 0.2,            share of the daily read volume kept hot in cache (an upper bound: repeat reads shrink it)
     "server_qps": 1000}               what one app server sustains (state this as an assumption)

check: the candidate file is {"assumptions": {...}, "claims": {"write_qps": 1200, ...}}
  1. consistency: each claim must match what the candidate's OWN assumptions give (within --tol, default 1.5x)
  2. plausibility: each claim is compared with the reference estimate (within --band, default 10x)
The reference numbers stay hidden unless --show-reference is given (use it in the debrief, not during the session).
Units are decimal (1 KB = 1000 bytes); interviews round, so do not chase the last digit.
"""
import json
import math
import sys

DAY = 86400.0
OUTPUTS = ["write_qps", "read_qps", "peak_write_qps", "peak_read_qps", "daily_write_bytes",
           "total_storage_bytes", "ingress_bytes_per_s", "egress_bytes_per_s", "cache_bytes", "servers"]


def calc(a):
    dau = a.get("dau")
    if dau is None:
        dau = a["mau"] * a.get("dau_ratio", 0.5)
    w, r = a.get("writes_per_user_day", 0.0), a.get("reads_per_user_day", 0.0)
    bw, br = a.get("bytes_per_write", 0.0), a.get("bytes_per_read", 0.0)
    pf = a.get("peak_factor", 2.0)
    years, repl = a.get("retention_years", 5.0), a.get("replication", 3.0)
    out = {}
    out["write_qps"] = dau * w / DAY
    out["read_qps"] = dau * r / DAY
    out["peak_write_qps"] = out["write_qps"] * pf
    out["peak_read_qps"] = out["read_qps"] * pf
    out["daily_write_bytes"] = dau * w * bw
    out["total_storage_bytes"] = out["daily_write_bytes"] * a.get("new_data_fraction", 1.0) * 365 * years * repl
    out["ingress_bytes_per_s"] = out["peak_write_qps"] * bw
    out["egress_bytes_per_s"] = out["peak_read_qps"] * br
    out["cache_bytes"] = a.get("cache_fraction", 0.2) * dau * r * br
    if a.get("server_qps"):
        out["servers"] = math.ceil((out["peak_write_qps"] + out["peak_read_qps"]) / a["server_qps"])
    return out


def human(name, v):
    if name.endswith("_bytes") or name.endswith("_bytes_per_s"):
        for unit, size in (("EB", 1e18), ("PB", 1e15), ("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
            if v >= size:
                return "%.3g %s%s" % (v / size, unit, "/s" if name.endswith("_per_s") else "")
        return "%.3g B%s" % (v, "/s" if name.endswith("_per_s") else "")
    if v >= 1e9:
        return "%.3g B" % (v / 1e9)
    if v >= 1e6:
        return "%.3g M" % (v / 1e6)
    if v >= 1e3:
        return "%.3g K" % (v / 1e3)
    return "%.3g" % v


def ratio(x, y):
    if x == y:
        return 1.0
    if x <= 0 or y <= 0:
        return float("inf")
    return max(x / y, y / x)


def check(ref_path, cand_path, tol=1.5, band=10.0, show_ref=False):
    ref = json.load(open(ref_path, encoding="utf-8"))
    cand = json.load(open(cand_path, encoding="utf-8"))
    ref_out = ref.get("expected") or calc(ref["assumptions"])
    own = calc(cand["assumptions"])
    claims = cand.get("claims", {})
    bad = 0
    head = ("quantity", "you claimed", "your inputs") + (("reference",) if show_ref else ())
    print(("%-22s %-12s %-12s " + "%-12s " * show_ref + " %s") % (head + ("verdict",)))
    for k in OUTPUTS:
        if k not in claims:
            continue
        c = float(claims[k])
        mine = own.get(k)
        r = ref_out.get(k)
        verdict = []
        if mine is None:
            verdict.append("CANNOT CHECK (missing assumption, for example server_qps)")
            bad += 1
        elif ratio(c, mine) > tol:
            verdict.append("ARITHMETIC: your inputs give %s, not %s" % (human(k, mine), human(k, c)))
            bad += 1
        if r is not None and ratio(c, r) > band:
            verdict.append("IMPLAUSIBLE: %.0fx away from the reference; re-check an assumption" % ratio(c, r))
        row = (k, human(k, c), human(k, mine) if mine is not None else "-") + \
            ((human(k, r) if r is not None else "-",) if show_ref else ())
        print(("%-22s %-12s %-12s " + "%-12s " * show_ref + " %s") % (row + ("; ".join(verdict) or "ok",)))
    missing = [k for k in ("write_qps", "read_qps", "total_storage_bytes") if k not in claims and ref_out.get(k)]
    if missing:
        print("note: no claim for " + ", ".join(missing))
    return 1 if bad else 0


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("calc", "check"):
        sys.exit(__doc__)
    if sys.argv[1] == "calc":
        a = json.load(open(sys.argv[2], encoding="utf-8"))
        if "assumptions" in a:
            a = a["assumptions"]
        for k, v in calc(a).items():
            print("%-22s %s" % (k, human(k, v)))
        return 0
    args = sys.argv[2:]
    show_ref = "--show-reference" in args
    args = [x for x in args if x != "--show-reference"]
    opts = {"--tol": 1.5, "--band": 10.0}
    pos = []
    i = 0
    while i < len(args):
        if args[i] in opts:
            opts[args[i]] = float(args[i + 1])
            i += 2
        else:
            pos.append(args[i])
            i += 1
    return check(pos[0], pos[1], opts["--tol"], opts["--band"], show_ref)


if __name__ == "__main__":
    sys.exit(main())
