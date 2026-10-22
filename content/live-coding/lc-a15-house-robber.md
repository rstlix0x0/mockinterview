---
id: lc-a15-house-robber
title: House Robber
type: live-coding
level: [junior]
tags: [dynamic-programming]
time_minutes: 15
entry: max_robbed
kind: func
source: adapted
author: mockinterview
legacy_id: A15
---

# House Robber

## Statement

`nums[i]` is the money in house `i` along a street. You cannot take from two adjacent houses. Return the maximum total you can take.

**Signature:** `max_robbed(nums: int[]) -> int`

**Constraints:**
- 0 <= len(nums) <= 1000000
- 0 <= nums[i] <= 10000

**Examples:**

- **Example 1** - input: `{"nums":[1,2,3,1]}`  
  output: `4`
- **Example 2** - input: `{"nums":[2,7,9,3,1]}`  
  output: `12`

## Signature

```signature
max_robbed(nums: int[]) -> int
```

## Tests

```json tests
{"function":"max_robbed","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[1,2,3,1]},"expected":4},
{"name":"example-2","tags":["visible"],"args":{"nums":[2,7,9,3,1]},"expected":12},
{"name":"edge-empty","tags":["edge"],"args":{"nums":[]},"expected":0},
{"name":"edge-single","tags":["edge"],"args":{"nums":[5]},"expected":5},
{"name":"hidden-skip-two","tags":["hidden"],"args":{"nums":[5,1,1,5]},"expected":10},
{"name":"hidden-zeros","tags":["hidden"],"args":{"nums":[0,0,0]},"expected":0},
{"name":"random-1","tags":["hidden"],"args":{"nums":[4,0,1,0,0,4,8,5,2]},"expected":15},
{"name":"random-2","tags":["hidden"],"args":{"nums":[1,1,6,9,6]},"expected":13},
{"name":"random-3","tags":["hidden"],"args":{"nums":[3,1,9,0,5,0]},"expected":17},
{"name":"random-4","tags":["hidden"],"args":{"nums":[0,6,2]},"expected":6}
]}
```

## Reference solution

```python reference
def solve(nums):
    take, skip = 0, 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
- **Clarifying questions (answer verbatim):**
  - Q: Is the street circular?  
    A: No. (That is a good follow-up.)
- **Hint ladder:**
  - H0 (free): For house i you either take it or not.
  - H1 (-5): best(i) = max(best(i-1), best(i-2) + nums[i]).
  - H2 (-10): You only need the previous two values.
  - H3 (-20): Handle lengths 0 and 1 naturally by starting both values at 0.
- **Follow-ups:**
  - Circular street (first and last are adjacent).
  - Return which houses were robbed.
- **Mistakes the tests are built to catch:**
  - Greedy 'take the larger of the neighbours'.
  - Recursion without memoisation.
