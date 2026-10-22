---
id: lc-a13-maximum-subarray-sum
title: Maximum Subarray Sum
type: live-coding
level: [junior]
tags: [dynamic-programming, arrays]
time_minutes: 15
languages: [python]
entry: max_subarray
kind: func
runs_code: true
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

## Stub

```python
def max_subarray(nums):
    """max_subarray(nums: int[]) -> int"""
    raise NotImplementedError
```

## Signature

```signature
max_subarray(nums: int[]) -> int
```

## Tests

```json tests
{"function":"max_subarray","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[100000,500000,1000000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[-2,1,-3,4,-1,2,1,-5,4]}},
{"name":"example-2","tags":["visible"],"args":{"nums":[-3,-1,-2]}},
{"name":"edge-single-negative","tags":["edge"],"args":{"nums":[-5]}},
{"name":"edge-all-positive","tags":["edge"],"args":{"nums":[1,2,3]}},
{"name":"hidden-restart","tags":["hidden"],"args":{"nums":[5,-10,3,2]}}
]}
```

## Oracle

```python oracle
def solve(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

def gen_random(seed):
    rnd = random.Random(seed)
    return {"nums": [rnd.randint(-8, 8) for _ in range(rnd.randint(1, 12))]}

def gen_perf(n):
    rnd = random.Random(213)
    return {"nums": [rnd.randint(-1000, 1000) for _ in range(n)]}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space (Kadane)
- **Scaling check:** sizes [100000, 500000, 1000000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
