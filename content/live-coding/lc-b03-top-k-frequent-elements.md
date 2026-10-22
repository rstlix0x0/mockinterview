---
id: lc-b03-top-k-frequent-elements
title: Top K Frequent Elements
type: live-coding
level: [junior, mid]
tags: [hash-map, heap, sorting]
time_minutes: 20
entry: top_k_frequent
kind: func
source: adapted
author: mockinterview
legacy_id: B3
---

# Top K Frequent Elements

## Statement

Return the `k` most frequent values in `nums`, ordered by frequency descending and then by value ascending. `k` is at most the number of distinct values.

**Signature:** `top_k_frequent(nums: int[], k: int) -> int[]`

**Constraints:**
- 1 <= len(nums) <= 200000
- 1 <= k <= distinct values

**Examples:**

- **Example 1** - input: `{"nums":[1,1,1,2,2,3],"k":2}`  
  output: `[1,2]`
- **Example 2** - input: `{"nums":[4,4,5,5,6],"k":2}`  
  output: `[4,5]`

## Signature

```signature
top_k_frequent(nums: int[], k: int) -> int[]
```

## Tests

```json tests
{"function":"top_k_frequent","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[1,1,1,2,2,3],"k":2},"expected":[1,2]},
{"name":"example-2","tags":["visible"],"args":{"nums":[4,4,5,5,6],"k":2},"expected":[4,5]},
{"name":"edge-single","tags":["edge"],"args":{"nums":[9],"k":1},"expected":[9]},
{"name":"edge-all-equal-freq","tags":["edge"],"args":{"nums":[3,1,2],"k":3},"expected":[1,2,3]},
{"name":"hidden-negatives","tags":["hidden"],"args":{"nums":[-1,-1,2,2,2,0],"k":1},"expected":[2]},
{"name":"random-1","tags":["hidden"],"args":{"nums":[0,-4,-3,-4,-4,0,4,1,-2,-3],"k":6},"expected":[-4,-3,0,-2,1,4]},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-3,-3,2,2,-3,4],"k":2},"expected":[-3,2]},
{"name":"random-3","tags":["hidden"],"args":{"nums":[-1,-3,-4,1,-4,4,0],"k":6},"expected":[-4,-3,-1,0,1,4]},
{"name":"random-4","tags":["hidden"],"args":{"nums":[-4,2,-2,2],"k":2},"expected":[2,-4]}
]}
```

## Reference solution

```python reference
from collections import Counter

def solve(nums, k):
    c = Counter(nums)
    return [v for v, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]
```

## Interviewer notes

- **Target complexity:** O(n log k) with a heap, or O(n) with bucket sort
- **Clarifying questions (answer verbatim):**
  - Q: Tie-breaking?  
    A: Lower value first.
- **Hint ladder:**
  - H0 (free): Count first.
  - H1 (-5): Then select the top k by a composite key.
  - H2 (-10): A heap of size k, or bucket by frequency for O(n).
  - H3 (-20): Respect the tie-break exactly.
- **Follow-ups:**
  - O(n) bucket-sort version.
  - Top k on a stream with bounded memory (Misra-Gries / count-min sketch discussion).
- **Mistakes the tests are built to catch:**
  - Sorting only by frequency and leaving ties unspecified.
  - Using a max-heap of all items: O(d log d) is fine but explain the trade-off.
