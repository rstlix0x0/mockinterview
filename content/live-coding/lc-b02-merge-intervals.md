---
id: lc-b02-merge-intervals
title: Merge Intervals
type: live-coding
level: [junior, mid]
tags: [sorting, intervals]
time_minutes: 20
entry: merge_intervals
kind: func
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

## Signature

```signature
merge_intervals(intervals: int[][]) -> int[][]
```

## Tests

```json tests
{"function":"merge_intervals","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"intervals":[[1,3],[2,6],[8,10],[15,18]]},"expected":[[1,6],[8,10],[15,18]]},
{"name":"example-2","tags":["visible"],"args":{"intervals":[[1,4],[4,5]]},"expected":[[1,5]]},
{"name":"edge-empty","tags":["edge"],"args":{"intervals":[]},"expected":[]},
{"name":"edge-single","tags":["edge"],"args":{"intervals":[[5,5]]},"expected":[[5,5]]},
{"name":"hidden-nested","tags":["hidden"],"args":{"intervals":[[1,10],[2,3],[4,5]]},"expected":[[1,10]]},
{"name":"hidden-unsorted","tags":["hidden"],"args":{"intervals":[[8,9],[1,2],[2,8]]},"expected":[[1,9]]},
{"name":"hidden-point-intervals","tags":["hidden"],"args":{"intervals":[[3,3],[3,3],[4,4]]},"expected":[[3,3],[4,4]]},
{"name":"random-1","tags":["hidden"],"args":{"intervals":[[0,0],[11,11],[10,10],[4,8]]},"expected":[[0,0],[4,8],[10,10],[11,11]]},
{"name":"random-2","tags":["hidden"],"args":{"intervals":[[1,1],[6,10],[6,6],[8,10],[2,2]]},"expected":[[1,1],[2,2],[6,10]]},
{"name":"random-3","tags":["hidden"],"args":{"intervals":[[3,3],[9,9],[11,13],[0,4],[4,5],[5,9]]},"expected":[[0,9],[11,13]]},
{"name":"random-4","tags":["hidden"],"args":{"intervals":[[0,3],[2,5],[6,8]]},"expected":[[0,5],[6,8]]}
]}
```

## Reference solution

```python reference
def solve(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
```

## Interviewer notes

- **Target complexity:** O(n log n) time
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
