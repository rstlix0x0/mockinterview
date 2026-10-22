---
id: lc-b08-longest-increasing-subsequence
title: Longest Strictly Increasing Subsequence
type: live-coding
level: [junior, mid]
tags: [dynamic-programming, binary-search]
time_minutes: 30
languages: [python]
entry: lis_length
kind: func
runs_code: true
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

## Stub

```python
def lis_length(nums):
    """lis_length(nums: int[]) -> int"""
    raise NotImplementedError
```

## Signature

```signature
lis_length(nums: int[]) -> int
```

## Tests

```json tests
{"function":"lis_length","kind":"func","compare":"exact","fuzz":20,"perf":{"sizes":[20000,100000,200000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[10,9,2,5,3,7,101,18]}},
{"name":"example-2","tags":["visible"],"args":{"nums":[7,7,7,7]}},
{"name":"edge-empty","tags":["edge"],"args":{"nums":[]}},
{"name":"edge-sorted","tags":["edge"],"args":{"nums":[1,2,3,4,5]}},
{"name":"edge-descending","tags":["edge"],"args":{"nums":[5,4,3,2,1]}},
{"name":"hidden-equal-values-strict","tags":["hidden"],"args":{"nums":[1,3,3,4]}}
]}
```

## Oracle

```python oracle
def solve(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)

def gen_random(seed):
    rnd = random.Random(seed)
    return {"nums": [rnd.randint(-5, 5) for _ in range(rnd.randint(0, 12))]}

def gen_perf(n):
    rnd = random.Random(8)
    return {"nums": [rnd.randint(-10**9, 10**9) for _ in range(n)]}
```

## Interviewer notes

- **Target complexity:** O(n log n) time, O(n) space
- **Scaling check:** sizes [20000, 100000, 200000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
