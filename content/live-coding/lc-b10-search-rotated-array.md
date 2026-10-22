---
id: lc-b10-search-rotated-array
title: Search in a Rotated Sorted Array
type: live-coding
level: [junior, mid]
tags: [binary-search]
time_minutes: 25
entry: search_rotated
kind: func
source: adapted
author: mockinterview
legacy_id: B10
---

# Search in a Rotated Sorted Array

## Statement

A strictly increasing array of distinct integers was rotated at an unknown pivot (for example `[4,5,6,7,0,1,2]`). Return the index of `target`, or `-1` if absent. The solution must run in O(log n).

**Signature:** `search_rotated(nums: int[], target: int) -> int`

**Constraints:**
- 1 <= len(nums) <= 1000000
- values are distinct

**Examples:**

- **Example 1** - input: `{"nums":[4,5,6,7,0,1,2],"target":0}`  
  output: `4`
- **Example 2** - input: `{"nums":[4,5,6,7,0,1,2],"target":3}`  
  output: `-1`
- **Example 3** - input: `{"nums":[1],"target":0}`  
  output: `-1`

## Signature

```signature
search_rotated(nums: int[], target: int) -> int
```

## Tests

```json tests
{"function":"search_rotated","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[4,5,6,7,0,1,2],"target":0},"expected":4},
{"name":"example-2","tags":["visible"],"args":{"nums":[4,5,6,7,0,1,2],"target":3},"expected":-1},
{"name":"example-3","tags":["visible"],"args":{"nums":[1],"target":0},"expected":-1},
{"name":"edge-single-hit","tags":["edge"],"args":{"nums":[1],"target":1},"expected":0},
{"name":"edge-not-rotated","tags":["edge"],"args":{"nums":[1,2,3,4],"target":4},"expected":3},
{"name":"edge-two-elements","tags":["edge"],"args":{"nums":[3,1],"target":1},"expected":1},
{"name":"hidden-target-at-pivot","tags":["hidden"],"args":{"nums":[5,6,7,1,2,3,4],"target":1},"expected":3},
{"name":"hidden-first-and-last","tags":["hidden"],"args":{"nums":[6,7,8,1,2,3],"target":3},"expected":5},
{"name":"random-1","tags":["hidden"],"args":{"nums":[-19,-18,-13,-9,-4,-1,0,10,12,-20],"target":16},"expected":-1},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-13,-3,6,17,19,-16],"target":-16},"expected":5},
{"name":"random-3","tags":["hidden"],"args":{"nums":[0,12,-20,-18,-14,-6,-3],"target":-5},"expected":-1},
{"name":"random-4","tags":["hidden"],"args":{"nums":[5,6,-20,-10],"target":8},"expected":-1}
]}
```

## Reference solution

```python reference
def solve(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

## Interviewer notes

- **Target complexity:** O(log n) time, O(1) space
- **Clarifying questions (answer verbatim):**
  - Q: Duplicates?  
    A: No. Mention how duplicates would change the worst case.
  - Q: May I find the pivot first?  
    A: Yes, or do it in one pass.
- **Hint ladder:**
  - H0 (free): After any split, which half is sorted?
  - H1 (-5): Compare nums[lo] with nums[mid].
  - H2 (-10): Check whether the target lies inside the sorted half; keep that half, else the other.
  - H3 (-20): Use <= when comparing nums[lo] with nums[mid] to cover two-element ranges.
- **Follow-ups:**
  - Duplicates allowed: what is the worst case?
  - Find the minimum of a rotated array.
- **Mistakes the tests are built to catch:**
  - Strict < in `nums[lo] <= nums[mid]` breaking two-element ranges.
  - Infinite loops from bad bounds.
  - Linear scan (fails the complexity requirement; the tests cannot detect it, so be honest in review).
