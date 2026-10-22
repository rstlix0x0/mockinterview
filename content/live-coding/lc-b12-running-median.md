---
id: lc-b12-running-median
title: Running Median
type: live-coding
level: [junior, mid]
tags: [heap, design]
time_minutes: 30
entry: MedianFinder
kind: ops
source: adapted
author: mockinterview
legacy_id: B12
---

# Running Median

## Statement

Design `MedianFinder`: `add_num(x)` adds an integer to a growing collection and `find_median()` returns the median of all numbers added so far as a float (the mean of the two middle values when the count is even). `find_median` is only called after at least one `add_num`. `add_num` should be O(log n) and `find_median` O(1).

**Signature:** `class MedianFinder { add_num(x: int) -> void; find_median() -> float }`

**Constraints:**
- up to 200000 operations

**Examples:**

- **Example 1** - calls: `MedianFinder(); add_num(1); add_num(2); find_median(); add_num(3); find_median()`  
  returns: `[null,null,null,1.5,null,2.0]`

## Signature

```signature
MedianFinder()
add_num(x: int) -> void
find_median() -> float
```

## Tests

```json tests
{"function":"MedianFinder","kind":"ops","compare":"approx","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["MedianFinder",[]],["add_num",[1]],["add_num",[2]],["find_median",[]],["add_num",[3]],["find_median",[]]]},"expected":[null,null,null,1.5,null,2.0]},
{"name":"edge-single","tags":["edge"],"args":{"calls":[["MedianFinder",[]],["add_num",[-5]],["find_median",[]]]},"expected":[null,null,-5.0]},
{"name":"hidden-duplicates","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[4]],["add_num",[4]],["add_num",[4]],["find_median",[]]]},"expected":[null,null,null,null,4.0]},
{"name":"hidden-descending","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[9]],["add_num",[7]],["find_median",[]],["add_num",[5]],["add_num",[3]],["find_median",[]]]},"expected":[null,null,null,8.0,null,null,6.0]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[-1]],["add_num",[-13]],["add_num",[20]],["add_num",[-4]],["add_num",[12]],["find_median",[]],["add_num",[-14]],["add_num",[16]],["find_median",[]],["find_median",[]],["find_median",[]],["find_median",[]]]},"expected":[null,null,null,null,null,null,-1.0,null,null,-1.0,-1.0,-1.0,-1.0]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[-16]],["add_num",[-13]],["add_num",[6]],["add_num",[15]],["find_median",[]],["find_median",[]],["find_median",[]],["find_median",[]]]},"expected":[null,null,null,null,null,-3.5,-3.5,-3.5,-3.5]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[-6]],["find_median",[]],["find_median",[]],["add_num",[-20]],["add_num",[-3]],["add_num",[-5]],["find_median",[]],["add_num",[2]],["find_median",[]]]},"expected":[null,null,-6.0,-6.0,null,null,null,-5.5,null,-5.0]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[-20]],["add_num",[6]],["find_median",[]],["add_num",[-4]],["add_num",[5]],["find_median",[]]]},"expected":[null,null,null,-7.0,null,null,0.5]}
]}
```

## Reference solution

```python reference
import heapq

class MedianFinder:
    def __init__(self):
        self.lo, self.hi = [], []

    def add_num(self, x):
        heapq.heappush(self.lo, -x)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def find_median(self):
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2
```

## Interviewer notes

- **Target complexity:** O(log n) per add, O(1) per median
- **Clarifying questions (answer verbatim):**
  - Q: Return type?  
    A: A float. 2.0 and 2 compare equal in the checker.
  - Q: Out-of-order inserts?  
    A: Yes, any order.
- **Hint ladder:**
  - H0 (free): What do you need access to in order to read the median in O(1)?
  - H1 (-5): Only the middle one or two elements.
  - H2 (-10): Split the data into a lower half and an upper half.
  - H3 (-20): A max-heap for the lower half, a min-heap for the upper half, kept within one element of each other.
- **Follow-ups:**
  - Add `remove(x)`.
  - Sliding-window median.
  - Values are 0..100: can you do better?
- **Mistakes the tests are built to catch:**
  - Sorting on every query (O(n log n) per call).
  - Heaps drifting out of balance.
  - Integer division for the even-count case.
