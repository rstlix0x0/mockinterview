---
id: lc-b12-running-median
title: Running Median
type: live-coding
level: [junior, mid]
tags: [heap, design]
time_minutes: 30
languages: [python]
entry: MedianFinder
kind: ops
runs_code: true
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

## Stub

```python
class MedianFinder:
    def __init__(self):
        """No constructor arguments."""
        pass

    def add_num(self, x):
        """add_num(x: int) -> void"""
        raise NotImplementedError

    def find_median(self):
        """find_median() -> float"""
        raise NotImplementedError
```

## Signature

```signature
MedianFinder()
add_num(x: int) -> void
find_median() -> float
```

## Tests

```json tests
{"function":"MedianFinder","kind":"ops","compare":"approx","fuzz":20,"perf":{"sizes":[20000,100000,200000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["MedianFinder",[]],["add_num",[1]],["add_num",[2]],["find_median",[]],["add_num",[3]],["find_median",[]]]}},
{"name":"edge-single","tags":["edge"],"args":{"calls":[["MedianFinder",[]],["add_num",[-5]],["find_median",[]]]}},
{"name":"hidden-duplicates","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[4]],["add_num",[4]],["add_num",[4]],["find_median",[]]]}},
{"name":"hidden-descending","tags":["hidden"],"args":{"calls":[["MedianFinder",[]],["add_num",[9]],["add_num",[7]],["find_median",[]],["add_num",[5]],["add_num",[3]],["find_median",[]]]}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    calls = [["MedianFinder", []]]
    adds = 0
    for _ in range(rnd.randint(2, 14)):
        if adds and rnd.random() < 0.4:
            calls.append(["find_median", []])
        else:
            calls.append(["add_num", [rnd.randint(-20, 20)]])
            adds += 1
    if adds:
        calls.append(["find_median", []])
    return {"calls": calls}

def gen_perf(n):
    rnd = random.Random(12)
    calls = [["MedianFinder", []]]
    for i in range(n):
        calls.append(["add_num", [rnd.randint(-10**6, 10**6)]])
        if i % 4 == 3:
            calls.append(["find_median", []])
    return {"calls": calls}
```

## Interviewer notes

- **Target complexity:** O(log n) per add, O(1) per median
- **Scaling check:** sizes [20000, 100000, 200000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
