---
id: lc-b18-min-meeting-rooms
title: Minimum Meeting Rooms
type: live-coding
level: [junior, mid]
tags: [intervals, sorting, heap]
time_minutes: 25
languages: [python]
entry: min_meeting_rooms
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B18
---

# Minimum Meeting Rooms

## Statement

Given meeting time intervals `[start, end)` with `start < end`, return the minimum number of rooms required so that no two meetings in the same room overlap. A meeting that ends at time `t` does not conflict with one starting at `t`.

**Signature:** `min_meeting_rooms(intervals: int[][2]) -> int`

**Constraints:**
- 0 <= len(intervals) <= 500000

**Examples:**

- **Example 1** - input: `{"intervals":[[0,30],[5,10],[15,20]]}`  
  output: `2`
- **Example 2** - input: `{"intervals":[[7,10],[2,4]]}`  
  output: `1`

## Stub

```python
def min_meeting_rooms(intervals):
    """min_meeting_rooms(intervals: int[][2]) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"min_meeting_rooms","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[50000,150000,300000],"limit_ms":5000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"intervals":[[0,30],[5,10],[15,20]]}},
{"name":"example-2","tags":["visible"],"args":{"intervals":[[7,10],[2,4]]}},
{"name":"edge-empty","tags":["edge"],"args":{"intervals":[]}},
{"name":"edge-touching","tags":["edge"],"args":{"intervals":[[1,2],[2,3],[3,4]]}},
{"name":"edge-all-overlap","tags":["edge"],"args":{"intervals":[[1,9],[2,9],[3,9]]}},
{"name":"hidden-nested","tags":["hidden"],"args":{"intervals":[[1,10],[2,3],[4,5],[6,7]]}}
]}
```

## Oracle

```python oracle
def solve(intervals):
    starts = sorted(s for s, e in intervals)
    ends = sorted(e for s, e in intervals)
    rooms = best = j = 0
    for s in starts:
        while j < len(ends) and ends[j] <= s:
            j += 1
            rooms -= 1
        rooms += 1
        best = max(best, rooms)
    return best

def gen_random(seed):
    rnd = random.Random(seed)
    iv = []
    for _ in range(rnd.randint(0, 8)):
        a = rnd.randint(0, 15)
        iv.append([a, a + rnd.randint(1, 5)])
    return {"intervals": iv}

def gen_perf(n):
    rnd = random.Random(18)
    iv = []
    for _ in range(n):
        a = rnd.randint(0, 3 * n)
        iv.append([a, a + rnd.randint(1, 50)])
    return {"intervals": iv}
```

## Interviewer notes

- **Target complexity:** O(n log n) time
- **Scaling check:** sizes [50000, 150000, 300000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: Do touching meetings share a room?  
    A: Yes: end == next start is fine.
- **Hint ladder:**
  - H0 (free): What is the maximum number of meetings in progress at once?
  - H1 (-5): Sweep over events in time order.
  - H2 (-10): Sort starts and ends separately and walk two pointers.
  - H3 (-20): Or keep a min-heap of end times of rooms in use.
- **Follow-ups:**
  - Return the room assignment for each meeting.
  - Weighted meetings.
- **Mistakes the tests are built to catch:**
  - Using < instead of <= when releasing rooms.
  - Sorting pairs without handling ties correctly in an event sweep.
