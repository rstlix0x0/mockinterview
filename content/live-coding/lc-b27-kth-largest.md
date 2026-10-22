---
id: lc-b27-kth-largest
title: K-th Largest Element
type: live-coding
level: [junior, mid]
tags: [heap, quickselect, sorting]
time_minutes: 25
entry: kth_largest
kind: func
source: adapted
author: mockinterview
legacy_id: B27
---

# K-th Largest Element

## Statement

Return the k-th largest element of `nums` (1-based, duplicates counted: in `[3, 3, 2]` the 2nd largest is `3`). Sorting is acceptable for correctness, but discuss and, if time permits, implement a heap or quickselect solution.

**Signature:** `kth_largest(nums: int[], k: int) -> int`

**Constraints:**
- 1 <= k <= len(nums) <= 500000

**Examples:**

- **Example 1** - input: `{"nums":[3,2,1,5,6,4],"k":2}`  
  output: `5`
- **Example 2** - input: `{"nums":[3,2,3,1,2,4,5,5,6],"k":4}`  
  output: `4`

## Signature

```signature
kth_largest(nums: int[], k: int) -> int
```

## Tests

```json tests
{"function":"kth_largest","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[3,2,1,5,6,4],"k":2},"expected":5},
{"name":"example-2","tags":["visible"],"args":{"nums":[3,2,3,1,2,4,5,5,6],"k":4},"expected":4},
{"name":"edge-single","tags":["edge"],"args":{"nums":[9],"k":1},"expected":9},
{"name":"edge-k-is-length","tags":["edge"],"args":{"nums":[4,1,7],"k":3},"expected":1},
{"name":"hidden-duplicates","tags":["hidden"],"args":{"nums":[3,3,2],"k":2},"expected":3},
{"name":"random-1","tags":["hidden"],"args":{"nums":[0,-8,-6,-9,-9,-1,7,1,-4,-6],"k":10},"expected":-9},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-7,-6,4,9,4,-7],"k":5},"expected":-7},
{"name":"random-3","tags":["hidden"],"args":{"nums":[-2,-6,-8,1,-9,7,-1],"k":6},"expected":-8},
{"name":"random-4","tags":["hidden"],"args":{"nums":[-9,4,-4,4],"k":4},"expected":-9}
]}
```

## Reference solution

```python reference
import heapq

def solve(nums, k):
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]
```

## Interviewer notes

- **Target complexity:** O(n log k) with a size-k min-heap; O(n) average with quickselect
- **Clarifying questions (answer verbatim):**
  - Q: Are duplicates distinct ranks?  
    A: Yes: duplicates count.
- **Hint ladder:**
  - H0 (free): Sorting works. What is the cheaper structure if k is small?
  - H1 (-5): Keep the k largest seen so far.
  - H2 (-10): A min-heap of size k: its root is the k-th largest.
  - H3 (-20): Quickselect partitions around a pivot and only recurses into one side.
- **Follow-ups:**
  - Streaming: maintain the k-th largest as numbers arrive.
  - Worst-case O(n): median of medians (discuss).
- **Mistakes the tests are built to catch:**
  - Quickselect with a fixed pivot degrading to O(n^2) on sorted input.
  - Off-by-one between k-th largest and index k.
