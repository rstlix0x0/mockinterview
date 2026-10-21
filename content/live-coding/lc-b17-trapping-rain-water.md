---
id: lc-b17-trapping-rain-water
title: Trapping Rain Water
type: live-coding
level: [junior, mid]
tags: [two-pointers, arrays]
time_minutes: 30
languages: [python]
entry: trap_rain
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B17
---

# Trapping Rain Water

## Statement

`height[i]` is the height of a bar of width 1. After rain, how many units of water are trapped between the bars?

**Signature:** `trap_rain(height: int[]) -> int`

**Constraints:**
- 0 <= len(height) <= 1000000
- 0 <= height[i] <= 100000

**Examples:**

- **Example 1** - input: `{"height":[0,1,0,2,1,0,1,3,2,1,2,1]}`  
  output: `6`
- **Example 2** - input: `{"height":[4,2,0,3,2,5]}`  
  output: `9`

## Stub

```python
def trap_rain(height):
    """trap_rain(height: int[]) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"trap_rain","kind":"func","compare":"exact","fuzz":30,"perf":{"sizes":[100000,500000,1000000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"height":[0,1,0,2,1,0,1,3,2,1,2,1]}},
{"name":"example-2","tags":["visible"],"args":{"height":[4,2,0,3,2,5]}},
{"name":"edge-empty","tags":["edge"],"args":{"height":[]}},
{"name":"edge-two-bars","tags":["edge"],"args":{"height":[3,5]}},
{"name":"edge-monotonic","tags":["edge"],"args":{"height":[1,2,3,4]}},
{"name":"hidden-valley","tags":["hidden"],"args":{"height":[5,0,0,5]}},
{"name":"hidden-flat","tags":["hidden"],"args":{"height":[2,2,2]}}
]}
```

## Oracle

```python oracle
def solve(height):
    l, r = 0, len(height) - 1
    lm = rm = water = 0
    while l < r:
        if height[l] < height[r]:
            lm = max(lm, height[l])
            water += lm - height[l]
            l += 1
        else:
            rm = max(rm, height[r])
            water += rm - height[r]
            r -= 1
    return water

def gen_random(seed):
    rnd = random.Random(seed)
    return {"height": [rnd.randint(0, 6) for _ in range(rnd.randint(0, 12))]}

def gen_perf(n):
    rnd = random.Random(17)
    return {"height": [rnd.randint(0, 10000) for _ in range(n)]}
```

## Interviewer notes

- **Target complexity:** O(n) time; O(1) space with two pointers
- **Scaling check:** sizes [100000, 500000, 1000000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Is water trapped at the edges?  
    A: No: it would spill over.
- **Hint ladder:**
  - H0 (free): What limits the water above bar i?
  - H1 (-5): min(tallest bar on its left, tallest bar on its right) - height[i].
  - H2 (-10): Precompute prefix and suffix maxima, or...
  - H3 (-20): Two pointers: always advance the side with the smaller maximum.
- **Follow-ups:**
  - The 2D version (trapping rain water II).
  - Monotonic stack formulation.
- **Mistakes the tests are built to catch:**
  - Computing max-left and max-right in O(n) per bar.
  - Adding negative water for bars higher than the running max.
