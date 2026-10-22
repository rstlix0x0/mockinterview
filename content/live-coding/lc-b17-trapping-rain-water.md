---
id: lc-b17-trapping-rain-water
title: Trapping Rain Water
type: live-coding
level: [junior, mid]
tags: [two-pointers, arrays]
time_minutes: 30
entry: trap_rain
kind: func
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

## Signature

```signature
trap_rain(height: int[]) -> int
```

## Tests

```json tests
{"function":"trap_rain","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"height":[0,1,0,2,1,0,1,3,2,1,2,1]},"expected":6},
{"name":"example-2","tags":["visible"],"args":{"height":[4,2,0,3,2,5]},"expected":9},
{"name":"edge-empty","tags":["edge"],"args":{"height":[]},"expected":0},
{"name":"edge-two-bars","tags":["edge"],"args":{"height":[3,5]},"expected":0},
{"name":"edge-monotonic","tags":["edge"],"args":{"height":[1,2,3,4]},"expected":0},
{"name":"hidden-valley","tags":["hidden"],"args":{"height":[5,0,0,5]},"expected":10},
{"name":"hidden-flat","tags":["hidden"],"args":{"height":[2,2,2]},"expected":0},
{"name":"random-1","tags":["hidden"],"args":{"height":[6,2,0,5,0,5,0,5,6]},"expected":25},
{"name":"random-2","tags":["hidden"],"args":{"height":[0,6,6,0,3]},"expected":3},
{"name":"random-3","tags":["hidden"],"args":{"height":[1,0,4,0,5,2]},"expected":5},
{"name":"random-4","tags":["hidden"],"args":{"height":[0,3,1]},"expected":0}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(n) time; O(1) space with two pointers
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
