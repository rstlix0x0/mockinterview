---
id: lc-b30-sliding-window-maximum
title: Sliding Window Maximum
type: live-coding
level: [junior, mid]
tags: [deque, monotonic-queue, sliding-window]
time_minutes: 30
entry: sliding_window_max
kind: func
source: adapted
author: mockinterview
legacy_id: B30
---

# Sliding Window Maximum

## Statement

Return the maximum of every contiguous window of size `k` as it slides from left to right over `nums` (so `len(nums) - k + 1` values).

**Signature:** `sliding_window_max(nums: int[], k: int) -> int[]`

**Constraints:**
- 1 <= k <= len(nums) <= 500000

**Examples:**

- **Example 1** - input: `{"nums":[1,3,-1,-3,5,3,6,7],"k":3}`  
  output: `[3,3,5,5,6,7]`
- **Example 2** - input: `{"nums":[1],"k":1}`  
  output: `[1]`

---

## Signature

```signature
sliding_window_max(nums: int[], k: int) -> int[]
```

## Tests

```json tests
{"function":"sliding_window_max","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[1,3,-1,-3,5,3,6,7],"k":3},"expected":[3,3,5,5,6,7]},
{"name":"example-2","tags":["visible"],"args":{"nums":[1],"k":1},"expected":[1]},
{"name":"edge-k-one","tags":["edge"],"args":{"nums":[4,2,7],"k":1},"expected":[4,2,7]},
{"name":"edge-k-is-length","tags":["edge"],"args":{"nums":[4,2,7],"k":3},"expected":[7]},
{"name":"hidden-equal-values","tags":["hidden"],"args":{"nums":[2,2,2,2],"k":2},"expected":[2,2,2]},
{"name":"hidden-descending","tags":["hidden"],"args":{"nums":[9,8,7,6],"k":2},"expected":[9,8,7]},
{"name":"random-1","tags":["hidden"],"args":{"nums":[0,-8,-6,-9,-9,-1,7,1,-4,-6],"k":10},"expected":[7]},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-7,-6,4,9,4,-7],"k":5},"expected":[9,9]},
{"name":"random-3","tags":["hidden"],"args":{"nums":[-2,-6,-8,1,-9,7,-1],"k":6},"expected":[7,7]},
{"name":"random-4","tags":["hidden"],"args":{"nums":[-9,4,-4,4],"k":4},"expected":[4]}
]}
```

## Reference solution

```python reference
from collections import deque

def solve(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
```

## Interviewer notes

- **Target complexity:** O(n) time with a monotonic deque
- **Clarifying questions (answer verbatim):**
  - Q: Do I return indices?  
    A: No: values.
- **Hint ladder:**
  - H0 (free): Taking max() of each window is O(n*k).
  - H1 (-5): Which elements can never be a future maximum?
  - H2 (-10): Anything smaller than a newer element to its right.
  - H3 (-20): A deque of indices with decreasing values; drop from the back while smaller, from the front when outside the window.
- **Follow-ups:**
  - Sliding window minimum and maximum together.
  - Sliding window median.
- **Mistakes the tests are built to catch:**
  - Storing values instead of indices (cannot expire).
  - Wrong expiry condition (off by one).
  - Heap with lazy deletion is O(n log n): acceptable but explain.

---
