---
id: lc-b02-merge-intervals
title: Merge Intervals
type: live-coding
level: [junior, mid]
tags: [sorting, intervals]
time_minutes: 20
languages: [python]
entry: merge_intervals
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B2
---

# Merge Intervals

## Statement

Merge all overlapping closed intervals and return the result sorted by start. Intervals that touch (`[1,2]` and `[2,3]`) overlap and must be merged. The input is unsorted.

**Signature:** `merge_intervals(intervals: int[][2]) -> int[][2]`

**Constraints:**
- 0 <= len(intervals) <= 200000
- start <= end

**Examples:**

- **Example 1** - input: `{"intervals":[[1,3],[2,6],[8,10],[15,18]]}`  
  output: `[[1,6],[8,10],[15,18]]`
- **Example 2** - input: `{"intervals":[[1,4],[4,5]]}`  
  output: `[[1,5]]`

## Stub

```python
def merge_intervals(intervals):
    """merge_intervals(intervals: int[][2]) -> int[][2]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"merge_intervals","kind":"func","compare":"exact","fuzz":15,"perf":{"sizes":[20000,100000,200000],"limit_ms":5000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"intervals":[[1,3],[2,6],[8,10],[15,18]]}},
{"name":"example-2","tags":["visible"],"args":{"intervals":[[1,4],[4,5]]}},
{"name":"edge-empty","tags":["edge"],"args":{"intervals":[]}},
{"name":"edge-single","tags":["edge"],"args":{"intervals":[[5,5]]}},
{"name":"hidden-nested","tags":["hidden"],"args":{"intervals":[[1,10],[2,3],[4,5]]}},
{"name":"hidden-unsorted","tags":["hidden"],"args":{"intervals":[[8,9],[1,2],[2,8]]}},
{"name":"hidden-point-intervals","tags":["hidden"],"args":{"intervals":[[3,3],[3,3],[4,4]]}}
]}
```

## Oracle

```python oracle
def solve(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out

def gen_random(seed):
    rnd = random.Random(seed)
    iv = []
    for _ in range(rnd.randint(0, 7)):
        a = rnd.randint(0, 12)
        iv.append([a, a + rnd.randint(0, 4)])
    return {"intervals": iv}

def gen_perf(n):
    rnd = random.Random(3)
    iv = []
    for _ in range(n):
        a = rnd.randint(0, 10 * n)
        iv.append([a, a + rnd.randint(0, 20)])
    return {"intervals": iv}
```

## Interviewer notes

- **Target complexity:** O(n log n) time
- **Scaling check:** sizes [20000, 100000, 200000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: Closed or half-open intervals?  
    A: Closed. Touching intervals merge.
- **Hint ladder:**
  - H0 (free): What property makes the merge a single pass?
  - H1 (-5): Sort by start.
  - H2 (-10): Compare each start with the end of the last merged interval.
  - H3 (-20): Extend with max(end, previous end); do not just replace it.
- **Follow-ups:**
  - Insert one interval into an already merged list in O(n).
  - Find the free gaps.
- **Mistakes the tests are built to catch:**
  - Not taking max of the ends (nested intervals).
  - Mutating the input unintentionally.
  - Using < instead of <= for touching intervals.
