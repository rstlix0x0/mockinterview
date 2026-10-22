---
id: lc-b26-merge-k-sorted-lists
title: Merge K Sorted Lists
type: live-coding
level: [junior, mid]
tags: [heap, k-way-merge]
time_minutes: 25
entry: merge_k_sorted
kind: func
source: adapted
author: mockinterview
legacy_id: B26
---

# Merge K Sorted Lists

## Statement

Merge `k` individually sorted (ascending) lists of integers into one sorted list. Lists may be empty and `lists` itself may be empty. Aim for O(N log k), where N is the total number of elements.

**Signature:** `merge_k_sorted(lists: int[][]) -> int[]`

**Constraints:**
- 0 <= k <= 1000
- total elements N <= 500000

**Examples:**

- **Example 1** - input: `{"lists":[[1,4,5],[1,3,4],[2,6]]}`  
  output: `[1,1,2,3,4,4,5,6]`
- **Example 2** - input: `{"lists":[[],[1]]}`  
  output: `[1]`

## Signature

```signature
merge_k_sorted(lists: int[][]) -> int[]
```

## Tests

```json tests
{"function":"merge_k_sorted","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"lists":[[1,4,5],[1,3,4],[2,6]]},"expected":[1,1,2,3,4,4,5,6]},
{"name":"example-2","tags":["visible"],"args":{"lists":[[],[1]]},"expected":[1]},
{"name":"edge-no-lists","tags":["edge"],"args":{"lists":[]},"expected":[]},
{"name":"edge-all-empty","tags":["edge"],"args":{"lists":[[],[],[]]},"expected":[]},
{"name":"hidden-duplicates","tags":["hidden"],"args":{"lists":[[1,1],[1],[1,1]]},"expected":[1,1,1,1,1]},
{"name":"random-1","tags":["hidden"],"args":{"lists":[[-8,-6],[-9,-9,-1,1,7],[-6],[-9,-9,0,3,9]]},"expected":[-9,-9,-9,-9,-8,-6,-6,-1,0,1,3,7,9]},
{"name":"random-2","tags":["hidden"],"args":{"lists":[[],[]]},"expected":[]},
{"name":"random-3","tags":["hidden"],"args":{"lists":[[-6],[-9,-8,1,7],[-2,2]]},"expected":[-9,-8,-6,-2,1,2,7]},
{"name":"random-4","tags":["hidden"],"args":{"lists":[[]]},"expected":[]}
]}
```

## Reference solution

```python reference
import heapq

def solve(lists):
    heap = [(l[0], i, 0) for i, l in enumerate(lists) if l]
    heapq.heapify(heap)
    out = []
    while heap:
        v, i, j = heapq.heappop(heap)
        out.append(v)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out
```

## Interviewer notes

- **Target complexity:** O(N log k) time, O(k) extra space
- **Clarifying questions (answer verbatim):**
  - Q: Is a stable merge required?  
    A: Not observable for integers.
- **Hint ladder:**
  - H0 (free): Concatenate-and-sort is O(N log N). Can you use the existing order?
  - H1 (-5): At any moment only the heads of the lists matter.
  - H2 (-10): A min-heap of (value, list index, element index).
  - H3 (-20): Pop the smallest, push the next element from the same list.
- **Follow-ups:**
  - Merge two sorted lists in place.
  - Lists are on disk and do not fit in memory (external merge).
- **Mistakes the tests are built to catch:**
  - Heap entries that cannot be compared on ties (store an index).
  - Skipping empty lists incorrectly.
