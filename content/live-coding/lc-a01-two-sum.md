---
id: lc-a01-two-sum
title: Two Sum
type: live-coding
level: [junior]
tags: [hash-map]
time_minutes: 10
languages: [python]
entry: two_sum
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: A1
---

# Two Sum

## Statement

Given an array of integers `nums` and an integer `target`, return the indices `[i, j]` with `i < j` such that `nums[i] + nums[j] == target`. Exactly one such pair exists in every input.

**Signature:** `two_sum(nums: int[], target: int) -> int[2]`

**Constraints:**
- 2 <= len(nums) <= 200000
- -10^9 <= nums[i], target <= 10^9
- exactly one valid pair

**Examples:**

- **Example 1** - input: `{"nums":[2,7,11,15],"target":9}`  
  output: `[0,1]`
- **Example 2** - input: `{"nums":[3,2,4],"target":6}`  
  output: `[1,2]`

## Stub

```python
def two_sum(nums, target):
    """two_sum(nums: int[], target: int) -> int[2]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"two_sum","kind":"func","compare":"exact","fuzz":6,"perf":{"sizes":[20000,100000,200000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[2,7,11,15],"target":9}},
{"name":"example-2","tags":["visible"],"args":{"nums":[3,2,4],"target":6}},
{"name":"edge-negatives","tags":["edge"],"args":{"nums":[-3,4,3,90],"target":0}},
{"name":"edge-duplicates","tags":["edge"],"args":{"nums":[3,3],"target":6}},
{"name":"edge-zero-pair","tags":["edge"],"args":{"nums":[0,4,3,0],"target":0}},
{"name":"hidden-large-values","tags":["hidden"],"args":{"nums":[1000000000,-1000000000,5],"target":0}},
{"name":"hidden-pair-at-end","tags":["hidden"],"args":{"nums":[1,2,3,4,5,6],"target":11}}
]}
```

## Oracle

```python oracle
def solve(nums, target):
    seen = {}
    for j, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], j]
        seen[x] = j
    return []

def gen_random(seed):
    rnd = random.Random(seed)
    while True:
        n = rnd.randint(2, 8)
        nums = [rnd.randint(-10, 10) for _ in range(n)]
        i, j = sorted(rnd.sample(range(n), 2))
        target = nums[i] + nums[j]
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if nums[a] + nums[b] == target]
        if len(pairs) == 1:
            return {"nums": nums, "target": target}

def gen_perf(n):
    nums = list(range(n))
    random.Random(1).shuffle(nums)
    return {"nums": nums, "target": (n - 2) + (n - 1)}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(n) space
- **Scaling check:** sizes [20000, 100000, 200000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Can the same element be used twice?  
    A: No. The two indices must differ.
  - Q: Can I assume exactly one answer?  
    A: Yes.
  - Q: Is the array sorted?  
    A: No.
- **Hint ladder:**
  - H0 (free): What is the cost of the brute force, and what repeated work does it do?
  - H1 (-5): For each element, which single value would complete the pair?
  - H2 (-10): How can you look up 'have I seen this value' in constant time?
  - H3 (-20): One pass: keep a map from value to index; before inserting x, look up target - x.
- **Follow-ups:**
  - Return all pairs (with duplicates) in sorted order.
  - The array is sorted: solve in O(1) extra space.
  - The data does not fit in memory: what do you change?
- **Mistakes the tests are built to catch:**
  - Inserting before checking, which pairs an element with itself.
  - Returning values instead of indices.
  - Nested loops that time out at n = 200000.
