---
id: lc-c05-access-log-analytics
title: Access-Log Analytics
type: live-coding
level: [mid, senior]
tags: [parsing, hash-map, percentiles]
time_minutes: 40
languages: [python]
entry: analyze_logs
kind: func
runs_code: true
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

## Stub

```python
def analyze_logs(lines, p):
    """analyze_logs(lines: string[], p: int) -> {valid, malformed, status, slowest}"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"analyze_logs","kind":"func","compare":"exact","fuzz":40,"perf":{"sizes":[30000,100000,300000],"limit_ms":5000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"lines":["2026-03-01T10:00:00Z GET /a 200 120ms","2026-03-01T10:00:01Z GET /a 500 300ms","oops","2026-03-01T10:00:02Z POST /b 201 40ms"],"p":100}},
{"name":"edge-empty","tags":["edge"],"args":{"lines":[],"p":50}},
{"name":"edge-all-malformed","tags":["edge"],"args":{"lines":["","x","GET /a 200 1ms"],"p":50}},
{"name":"hidden-nearest-rank","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /a 200 10ms","2026-03-01T10:00:00Z GET /a 200 20ms","2026-03-01T10:00:00Z GET /a 200 30ms","2026-03-01T10:00:00Z GET /a 200 40ms"],"p":50}},
{"name":"hidden-tie-by-path","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /b 200 5ms","2026-03-01T10:00:00Z GET /a 200 5ms"],"p":100}},
{"name":"hidden-more-than-three-paths","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /p0 200 0ms","2026-03-01T10:00:00Z GET /p1 200 10ms","2026-03-01T10:00:00Z GET /p2 200 20ms","2026-03-01T10:00:00Z GET /p3 200 30ms","2026-03-01T10:00:00Z GET /p4 200 40ms","2026-03-01T10:00:00Z GET /p5 200 50ms"],"p":99}},
{"name":"hidden-trailing-space","tags":["hidden"],"args":{"lines":["2026-03-01T10:00:00Z GET /a 200 5ms "],"p":50}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    lines = []
    for _ in range(rnd.randint(0, 25)):
        r = rnd.random()
        path = rnd.choice(["/a", "/b", "/c/d", "/e", "/"])
        line = "2026-03-0%dT10:%02d:00Z %s %s %d %dms" % (rnd.randint(1, 9), rnd.randint(0, 59), rnd.choice(["GET", "POST", "PUT"]), path,
                                                        rnd.choice([200, 201, 301, 404, 500, 503]), rnd.randint(1, 900))
        if r < 0.2:
            line = rnd.choice([line[:-2], line + " extra", "", "garbage", line.replace("T", " "), line.replace("GET", "get"), line.replace(" /", " ")])
        lines.append(line)
    return {"lines": lines, "p": rnd.choice([50, 90, 95, 99, 100, 1])}

def gen_perf(n):
    rnd = random.Random(105)
    lines = ["2026-03-01T10:00:00Z GET /p%d %d %dms" % (rnd.randint(0, 200), rnd.choice([200, 404, 500]), rnd.randint(1, 5000)) for _ in range(n)]
    return {"lines": lines, "p": 95}
```

## Interviewer notes

- **Target complexity:** O(n log n) because of per-path sorting
- **Scaling check:** sizes [30000, 100000, 300000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
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
