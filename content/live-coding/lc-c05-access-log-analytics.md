---
id: lc-c05-access-log-analytics
title: Access-Log Analytics
type: live-coding
level: [mid, senior]
tags: [parsing, hash-map, percentiles]
time_minutes: 40
entry: analyze_logs
kind: func
source: adapted
author: mockinterview
legacy_id: C5
---

# Access-Log Analytics

## Statement

Each valid log line has exactly this shape (single spaces, nothing else before or after):

```
<YYYY-MM-DDTHH:MM:SSZ> <METHOD> <path> <status> <latency>ms
```

`METHOD` is one of `GET POST PUT DELETE PATCH`; `path` starts with `/` and has no spaces; `status` is a three-digit code from 100 to 599; `latency` is a non-negative integer. The timestamp is only checked for shape, not for calendar validity. Any other line is **malformed** and must be counted, not crash the program.

Return an object with:
- `valid`, `malformed`: counts of each kind of line
- `status`: map from status class (`"2xx"`, `"4xx"`, ...) to the number of valid lines in it; classes that never occur are omitted
- `slowest`: up to three `[path, latency]` pairs - the paths with the highest p-th percentile latency, ordered by latency descending then path ascending

Percentile uses the **nearest-rank** method: for `n` latencies sorted ascending, the p-th percentile is the value at 1-based rank `ceil(p * n / 100)`.

**Signature:** `analyze_logs(lines: string[], p: int) -> {valid, malformed, status, slowest}`

**Constraints:**
- 0 <= len(lines) <= 300000
- 1 <= p <= 100

**Examples:**

- **Example 1** - input: `{"lines":["2026-03-01T10:00:00Z GET /a 200 120ms","2026-03-01T10:00:01Z GET /a 500 300ms","oops","2026-03-01T10:00:02Z POST /b 201 40ms"],"p":100}`  
  output: `{"valid":3,"malformed":1,"status":{"2xx":2,"5xx":1},"slowest":[["/a",300],["/b",40]]}`

## Signature

```signature
analyze_logs(lines: string[], p: int) -> record{valid: int, malformed: int, status: {string: int}, slowest: [string, int][]}
```

## Tests

```json tests
{"function":"analyze_logs","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"lines":["2026-03-01T10:00:00Z GET /a 200 120ms","2026-03-01T10:00:01Z GET /a 500 300ms","oops","2026-03-01T10:00:02Z POST /b 201 40ms"],"p":100},"expected":{"valid":3,"malformed":1,"status":{"2xx":2,"5xx":1},"slowest":[["/a",300],["/b",40]]}},
{"name":"edge-empty","tags":["edge"],"args":{"lines":[],"p":50},"expected":{"valid":0,"malformed":0,"status":{},"slowest":[]}},
{"name":"edge-all-malformed","tags":["edge"],"args":{"lines":["","x","GET /a 200 1ms"],"p":50},"expected":{"valid":0,"malformed":3,"status":{},"slowest":[]}},
{"name":"hidden-nearest-rank","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /a 200 10ms","2026-03-01T10:00:00Z GET /a 200 20ms","2026-03-01T10:00:00Z GET /a 200 30ms","2026-03-01T10:00:00Z GET /a 200 40ms"],"p":50},"expected":{"valid":4,"malformed":0,"status":{"2xx":4},"slowest":[["/a",20]]}},
{"name":"hidden-tie-by-path","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /b 200 5ms","2026-03-01T10:00:00Z GET /a 200 5ms"],"p":100},"expected":{"valid":2,"malformed":0,"status":{"2xx":2},"slowest":[["/a",5],["/b",5]]}},
{"name":"hidden-more-than-three-paths","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /p0 200 0ms","2026-03-01T10:00:00Z GET /p1 200 10ms","2026-03-01T10:00:00Z GET /p2 200 20ms","2026-03-01T10:00:00Z GET /p3 200 30ms","2026-03-01T10:00:00Z GET /p4 200 40ms","2026-03-01T10:00:00Z GET /p5 200 50ms"],"p":99},"expected":{"valid":6,"malformed":0,"status":{"2xx":6},"slowest":[["/p5",50],["/p4",40],["/p3",30]]}},
{"name":"hidden-trailing-space","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /a 200 5ms "],"p":50},"expected":{"valid":0,"malformed":1,"status":{},"slowest":[]}},
{"name":"random-1","tags":["hidden"],"args":{"lines":["garbage","","2026-03-08T10:22:00Z PUT / 301 91ms extra","2026-03-02T10:31:00Z GET a 404 284ms","2026-03-08T10:46:00Z PUT /e 200 122ms","2026-03-05T10:50:00Z PUT /e 200 782ms"],"p":90},"expected":{"valid":2,"malformed":4,"status":{"2xx":2},"slowest":[["/e",782]]}},
{"name":"random-2","tags":["hidden"],"args":{"lines":["2026-03-09T10:10:00Z GET / 200 329","2026-03-08T10:08:00Z POST /b 201 327ms","2026-03-04T10:57:00Z POST /a 201 96ms","2026-03-05T10:18:00Z POST  503 739ms","2026-03-09T10:09:00Z POST / 500 595ms","2026-03-06T10:25:00Z PUT / 500 499","2026-03-08T10:52:00Z GET /e 500 638ms"],"p":90},"expected":{"valid":4,"malformed":3,"status":{"2xx":2,"5xx":2},"slowest":[["/e",638],["/",595],["/b",327]]}},
{"name":"random-3","tags":["hidden"],"args":{"lines":["2026-03-09T10:10:00Z POST /b 404 289ms","2026-03-04T10:34:00Z GET /b 200 666ms","2026-03-02 10:01:00Z POS  /a 404 333ms","2026-03-02T10:37:00Z POST /c/d 301 547ms","2026-03-08T10:53:00Z POST / 201 760ms","2026-03-06T10:08:00Z POST / 503 721ms","2026-03-03 10:48:00Z GE  / 200 80ms","2026-03-02T10:08:00Z PUT / 201 281ms"],"p":99},"expected":{"valid":6,"malformed":2,"status":{"4xx":1,"2xx":3,"3xx":1,"5xx":1},"slowest":[["/",760],["/b",666],["/c/d",547]]}},
{"name":"random-4","tags":["hidden"],"args":{"lines":["2026-03-05T10:20:00Z POST /e 500 91ms","2026-03-03T10:18:00Z PUT / 503 413ms","2026-03-08 10:16:00Z GE  /a 301 44ms","2026-03-02T10:09:00Z GET /c/d 503 302ms"],"p":90},"expected":{"valid":3,"malformed":1,"status":{"5xx":3},"slowest":[["/",413],["/c/d",302],["/e",91]]}}
]}
```

## Reference solution

```python reference
import re
from collections import Counter, defaultdict

def solve(lines, p):
    LOG_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z (GET|POST|PUT|DELETE|PATCH) (/\S*) ([1-5][0-9][0-9]) ([0-9]+)ms")
    valid = malformed = 0
    status = Counter()
    lat = defaultdict(list)
    for line in lines:
        m = LOG_RE.fullmatch(line)
        if not m:
            malformed += 1
            continue
        valid += 1
        status[m.group(3)[0] + "xx"] += 1
        lat[m.group(2)].append(int(m.group(4)))
    ranked = []
    for path, vals in lat.items():
        vals.sort()
        rank = -(-p * len(vals) // 100)
        ranked.append((-vals[rank - 1], path))
    ranked.sort()
    return {"valid": valid, "malformed": malformed, "status": dict(status),
            "slowest": [[path, -neg] for neg, path in ranked[:3]]}
```

## Interviewer notes

- **Target complexity:** O(n log n) because of per-path sorting
- **Clarifying questions (answer verbatim):**
  - Q: Is `/` a valid path?  
    A: Yes.
  - Q: What is the 100th percentile?  
    A: The maximum.
- **Hint ladder:**
  - H0 (free): Separate parsing from aggregation.
  - H1 (-5): One compiled regular expression (or a strict split) that either yields all fields or rejects the line.
  - H2 (-10): Group latencies per path, then sort each group once.
  - H3 (-20): Rank = ceil(p * n / 100) using integer arithmetic to avoid float rounding.
- **Follow-ups:**
  - The input is 50 GB: how do you compute approximate percentiles in bounded memory (t-digest / HDR histogram)?
  - Windowed per-minute statistics.
  - Parallelise across files.
- **Mistakes the tests are built to catch:**
  - Float arithmetic in the rank (e.g. 0.95 * 20).
  - Accepting trailing whitespace or lowercase methods.
  - Raising on a malformed line.
  - Using a statistics library's interpolated percentile.
