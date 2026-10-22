---
id: lc-a13-maximum-subarray-sum
title: Maximum Subarray Sum
type: live-coding
level: [junior]
tags: [dynamic-programming, arrays]
time_minutes: 15
entry: max_subarray
kind: func
source: adapted
author: mockinterview
legacy_id: A13
---

# Maximum Subarray Sum

## Statement

Return the largest sum of any non-empty contiguous subarray of `nums`.

**Signature:** `max_subarray(nums: int[]) -> int`

**Constraints:**
- 1 <= len(nums) <= 1000000

**Examples:**

- **Example 1** - input: `{"nums":[-2,1,-3,4,-1,2,1,-5,4]}`  
  output: `6`
- **Example 2** - input: `{"nums":[-3,-1,-2]}`  
  output: `-1`

## Signature

```signature
max_subarray(nums: int[]) -> int
```

## Tests

```json tests
{"function":"max_subarray","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[-2,1,-3,4,-1,2,1,-5,4]},"expected":6},
{"name":"example-2","tags":["visible"],"args":{"nums":[-3,-1,-2]},"expected":-1},
{"name":"edge-single-negative","tags":["edge"],"args":{"nums":[-5]},"expected":-5},
{"name":"edge-all-positive","tags":["edge"],"args":{"nums":[1,2,3]},"expected":6},
{"name":"hidden-restart","tags":["hidden"],"args":{"nums":[5,-10,3,2]},"expected":5},
{"name":"random-1","tags":["hidden"],"args":{"nums":[1,-7,-5,-8,-8,0,8,2,-3,-5]},"expected":10},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-6,-5,5,5,-6,0]},"expected":10},
{"name":"random-3","tags":["hidden"],"args":{"nums":[-1,-5,-7,2,-8,8,0]},"expected":8},
{"name":"random-4","tags":["hidden"],"args":{"nums":[-8,5,-3,5]},"expected":7}
]}
```

## Reference solution

```python reference
def solve(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space (Kadane)
- **Clarifying questions (answer verbatim):**
  - Q: May the subarray be empty?  
    A: No. With all-negative input the answer is the largest element.
- **Hint ladder:**
  - H0 (free): What is the best sum of a subarray ending at index i?
  - H1 (-5): Either extend the best ending at i-1, or start fresh at i.
  - H2 (-10): Keep a running 'best ending here' and a global maximum.
  - H3 (-20): Initialise from nums[0], not 0.
- **Follow-ups:**
  - Return the start and end indices.
  - Circular array version.
- **Mistakes the tests are built to catch:**
  - Initialising the answer to 0, which breaks all-negative input.
  - O(n^2) prefix-sum double loop.
