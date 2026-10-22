---
id: lc-fx-two-sum
title: Two Sum (fixture)
type: live-coding
level: [junior, mid]
tags: [hash-map, arrays]
time_minutes: 10
languages: [python]
entry: two_sum
kind: func
runs_code: true
source: original
author: tests
---
# Two Sum (fixture)

## Statement

Given `nums` and `target`, return indices `[i, j]` with `i < j` and `nums[i] + nums[j] == target`. Exactly one pair exists.

**Signature:** `two_sum(nums: int[], target: int) -> int[2]`

## Stub

```python
def two_sum(nums, target):
    raise NotImplementedError
```

## Signature

```signature
two_sum(nums: int[], target: int) -> int[]
```

## Tests

```json tests
{"function":"two_sum","kind":"func","compare":"exact","fuzz":4,"perf":{"sizes":[2000,4000,8000],"limit_ms":3000,"max_exponent":1.6},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[2,7,11,15],"target":9}},
{"name":"edge-duplicates","tags":["edge"],"args":{"nums":[3,3],"target":6}},
{"name":"hidden-negatives","tags":["hidden"],"args":{"nums":[-3,4,3,90],"target":0}}
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
