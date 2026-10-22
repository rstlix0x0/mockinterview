---
id: lc-a15-house-robber
title: House Robber
type: live-coding
level: [junior]
tags: [dynamic-programming]
time_minutes: 15
languages: [python]
entry: max_robbed
kind: func
runs_code: true
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

## Stub

```python
def max_robbed(nums):
    """max_robbed(nums: int[]) -> int"""
    raise NotImplementedError
```

## Signature

```signature
max_robbed(nums: int[]) -> int
```

## Tests

```json tests
{"function":"max_robbed","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[100000,500000,1000000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[1,2,3,1]}},
{"name":"example-2","tags":["visible"],"args":{"nums":[2,7,9,3,1]}},
{"name":"edge-empty","tags":["edge"],"args":{"nums":[]}},
{"name":"edge-single","tags":["edge"],"args":{"nums":[5]}},
{"name":"hidden-skip-two","tags":["hidden"],"args":{"nums":[5,1,1,5]}},
{"name":"hidden-zeros","tags":["hidden"],"args":{"nums":[0,0,0]}}
]}
```

## Oracle

```python oracle
def solve(nums):
    take, skip = 0, 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)

def gen_random(seed):
    rnd = random.Random(seed)
    return {"nums": [rnd.randint(0, 9) for _ in range(rnd.randint(0, 10))]}

def gen_perf(n):
    rnd = random.Random(215)
    return {"nums": [rnd.randint(0, 1000) for _ in range(n)]}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
- **Scaling check:** sizes [100000, 500000, 1000000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
