---
id: lc-b08-longest-increasing-subsequence
title: Longest Strictly Increasing Subsequence
type: live-coding
level: [junior, mid]
tags: [dynamic-programming, binary-search]
time_minutes: 30
entry: lis_length
kind: func
source: adapted
author: mockinterview
legacy_id: B8
---

# Longest Strictly Increasing Subsequence

## Statement

Return the length of the longest strictly increasing subsequence of `nums` (elements keep their order but need not be adjacent). An O(n^2) solution is accepted for correctness, but the large tests require O(n log n).

**Signature:** `lis_length(nums: int[]) -> int`

**Constraints:**
- 0 <= len(nums) <= 200000

**Examples:**

- **Example 1** - input: `{"nums":[10,9,2,5,3,7,101,18]}`  
  output: `4`
- **Example 2** - input: `{"nums":[7,7,7,7]}`  
  output: `1`

## Signature

```signature
lis_length(nums: int[]) -> int
```

## Tests

```json tests
{"function":"lis_length","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[10,9,2,5,3,7,101,18]},"expected":4},
{"name":"example-2","tags":["visible"],"args":{"nums":[7,7,7,7]},"expected":1},
{"name":"edge-empty","tags":["edge"],"args":{"nums":[]},"expected":0},
{"name":"edge-sorted","tags":["edge"],"args":{"nums":[1,2,3,4,5]},"expected":5},
{"name":"edge-descending","tags":["edge"],"args":{"nums":[5,4,3,2,1]},"expected":1},
{"name":"hidden-equal-values-strict","tags":["hidden"],"args":{"nums":[1,3,3,4]},"expected":3},
{"name":"random-1","tags":["hidden"],"args":{"nums":[-1,-5,-4,-5,5,5,-5,-1,3]},"expected":4},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-4,-4,1,4,1]},"expected":3},
{"name":"random-3","tags":["hidden"],"args":{"nums":[-2,-4,4,-5,0,-5]},"expected":2},
{"name":"random-4","tags":["hidden"],"args":{"nums":[-5,1,-3]},"expected":2}
]}
```

## Reference solution

```python reference
import bisect

def solve(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```

## Interviewer notes

- **Target complexity:** O(n log n) time, O(n) space
- **Clarifying questions (answer verbatim):**
  - Q: Strictly increasing?  
    A: Yes. Equal values do not extend a subsequence.
- **Hint ladder:**
  - H0 (free): Start with dp[i] = longest ending at i. What is the cost?
  - H1 (-5): Can you keep, for each length, the smallest possible tail value?
  - H2 (-10): That array of tails is always sorted: binary search the position for each new number.
  - H3 (-20): Use lower_bound (first tail >= x) for strictness.
- **Follow-ups:**
  - Reconstruct one actual subsequence.
  - Count the number of longest subsequences.
- **Mistakes the tests are built to catch:**
  - Using upper_bound, which allows equal values.
  - Believing the tails array is the subsequence.
