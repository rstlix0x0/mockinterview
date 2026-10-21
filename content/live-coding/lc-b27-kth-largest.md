---
id: lc-b27-kth-largest
title: K-th Largest Element
type: live-coding
level: [junior, mid]
tags: [heap, quickselect, sorting]
time_minutes: 25
languages: [python]
entry: kth_largest
kind: func
runs_code: true
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

## Stub

```python
def kth_largest(nums, k):
    """kth_largest(nums: int[], k: int) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"kth_largest","kind":"func","compare":"exact","fuzz":30,"perf":{"sizes":[50000,200000,500000],"limit_ms":4000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[3,2,1,5,6,4],"k":2}},
{"name":"example-2","tags":["visible"],"args":{"nums":[3,2,3,1,2,4,5,5,6],"k":4}},
{"name":"edge-single","tags":["edge"],"args":{"nums":[9],"k":1}},
{"name":"edge-k-is-length","tags":["edge"],"args":{"nums":[4,1,7],"k":3}},
{"name":"hidden-duplicates","tags":["hidden"],"args":{"nums":[3,3,2],"k":2}}
]}
```

## Oracle

```python oracle
def solve(nums, k):
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]

def gen_random(seed):
    rnd = random.Random(seed)
    nums = [rnd.randint(-9, 9) for _ in range(rnd.randint(1, 12))]
    return {"nums": nums, "k": rnd.randint(1, len(nums))}

def gen_perf(n):
    rnd = random.Random(227)
    return {"nums": [rnd.randint(-10**9, 10**9) for _ in range(n)], "k": n // 3}
```

## Interviewer notes

- **Target complexity:** O(n log k) with a size-k min-heap; O(n) average with quickselect
- **Scaling check:** sizes [50000, 200000, 500000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
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
