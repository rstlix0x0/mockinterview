---
id: lc-fx-two-sum
title: Two Sum (fixture)
type: live-coding
level: [junior, mid]
tags: [hash-map, arrays]
time_minutes: 10
entry: two_sum
kind: func
source: original
author: tests
---
# Two Sum (fixture)

## Statement

Given `nums` and `target`, return indices `[i, j]` with `i < j` and `nums[i] + nums[j] == target`. Exactly one pair exists.

**Signature:** `two_sum(nums: int[], target: int) -> int[2]`

## Signature

```signature
two_sum(nums: int[], target: int) -> int[]
```

## Tests

```json tests
{"function":"two_sum","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[2,7,11,15],"target":9},"expected":[0,1]},
{"name":"edge-duplicates","tags":["edge"],"args":{"nums":[3,3],"target":6},"expected":[0,1]},
{"name":"hidden-negatives","tags":["hidden"],"args":{"nums":[-3,4,3,90],"target":0},"expected":[0,2]},
{"name":"random-1","tags":["hidden"],"args":{"nums":[-1,-9,-7,-10,10,10],"target":-8},"expected":[0,2]},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-8,-7,3,8],"target":11},"expected":[2,3]},
{"name":"random-3","tags":["hidden"],"args":{"nums":[-3,-7,9,-9,0],"target":6},"expected":[0,2]},
{"name":"random-4","tags":["hidden"],"args":{"nums":[2,8,-7],"target":-5},"expected":[0,2]}
]}
```

## Reference solution

```python reference
def solve(nums, target):
    seen = {}
    for j, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], j]
        seen[x] = j
    return []
```

## Interviewer notes

- **Target complexity:** O(n) time, O(n) space
- **Clarifying questions (answer verbatim):**
  - Q: Can the same element be used twice?  
    A: No.
- **Hint ladder:**
  - H0 (free): What is the cost of the brute force?
  - H1 (-5): For each element, which single value would complete the pair?
  - H2 (-10): How can you look up a seen value in constant time?
  - H3 (-20): One pass: keep a map from value to index.
- **Follow-ups:**
  - The array is sorted: solve in O(1) extra space.
- **Mistakes the tests are built to catch:**
  - Inserting before checking.
