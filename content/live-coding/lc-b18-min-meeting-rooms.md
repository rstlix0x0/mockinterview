---
id: lc-b18-min-meeting-rooms
title: Minimum Meeting Rooms
type: live-coding
level: [junior, mid]
tags: [intervals, sorting, heap]
time_minutes: 25
entry: min_meeting_rooms
kind: func
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

## Signature

```signature
min_meeting_rooms(intervals: int[][]) -> int
```

## Tests

```json tests
{"function":"min_meeting_rooms","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"intervals":[[0,30],[5,10],[15,20]]},"expected":2},
{"name":"example-2","tags":["visible"],"args":{"intervals":[[7,10],[2,4]]},"expected":1},
{"name":"edge-empty","tags":["edge"],"args":{"intervals":[]},"expected":0},
{"name":"edge-touching","tags":["edge"],"args":{"intervals":[[1,2],[2,3],[3,4]]},"expected":1},
{"name":"edge-all-overlap","tags":["edge"],"args":{"intervals":[[1,9],[2,9],[3,9]]},"expected":3},
{"name":"hidden-nested","tags":["hidden"],"args":{"intervals":[[1,10],[2,3],[4,5],[6,7]]},"expected":2},
{"name":"random-1","tags":["hidden"],"args":{"intervals":[[1,2],[0,1],[8,13],[10,12]]},"expected":2},
{"name":"random-2","tags":["hidden"],"args":{"intervals":[[2,3],[13,18],[13,14],[8,10],[2,5]]},"expected":2},
{"name":"random-3","tags":["hidden"],"args":{"intervals":[[7,8],[1,4],[0,5],[8,10],[11,16],[4,7]]},"expected":2},
{"name":"random-4","tags":["hidden"],"args":{"intervals":[[0,4],[5,9],[12,15]]},"expected":1}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(n log n) time
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
