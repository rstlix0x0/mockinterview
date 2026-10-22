---
id: lc-b23-daily-temperatures
title: Days Until a Warmer Temperature
type: live-coding
level: [junior, mid]
tags: [stack, monotonic-stack]
time_minutes: 25
entry: daily_temperatures
kind: func
source: adapted
author: mockinterview
legacy_id: B23
---

# Days Until a Warmer Temperature

## Statement

For each day, return how many days you must wait for a **strictly warmer** temperature; `0` if there is none.

**Signature:** `daily_temperatures(temps: int[]) -> int[]`

**Constraints:**
- 0 <= len(temps) <= 500000

**Examples:**

- **Example 1** - input: `{"temps":[73,74,75,71,69,72,76,73]}`  
  output: `[1,1,4,2,1,1,0,0]`
- **Example 2** - input: `{"temps":[30,40,50,60]}`  
  output: `[1,1,1,0]`

## Signature

```signature
daily_temperatures(temps: int[]) -> int[]
```

## Tests

```json tests
{"function":"daily_temperatures","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"temps":[73,74,75,71,69,72,76,73]},"expected":[1,1,4,2,1,1,0,0]},
{"name":"example-2","tags":["visible"],"args":{"temps":[30,40,50,60]},"expected":[1,1,1,0]},
{"name":"edge-empty","tags":["edge"],"args":{"temps":[]},"expected":[]},
{"name":"edge-descending","tags":["edge"],"args":{"temps":[5,4,3]},"expected":[0,0,0]},
{"name":"edge-equal","tags":["edge"],"args":{"temps":[7,7,7]},"expected":[0,0,0]},
{"name":"hidden-valley","tags":["hidden"],"args":{"temps":[5,1,1,6]},"expected":[3,2,1,0]},
{"name":"random-1","tags":["hidden"],"args":{"temps":[34,30,31,30,40,40,30,34,38]},"expected":[4,1,2,1,0,0,1,1,0]},
{"name":"random-2","tags":["hidden"],"args":{"temps":[31,31,36,39,36]},"expected":[2,1,1,0,0]},
{"name":"random-3","tags":["hidden"],"args":{"temps":[33,31,39,30,35,30]},"expected":[2,1,0,1,0,0]},
{"name":"random-4","tags":["hidden"],"args":{"temps":[30,36,32]},"expected":[1,0,0]}
]}
```

## Reference solution

```python reference
def solve(temps):
    ans = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans
```

## Interviewer notes

- **Target complexity:** O(n) time
- **Clarifying questions (answer verbatim):**
  - Q: Does an equal temperature count as warmer?  
    A: No.
- **Hint ladder:**
  - H0 (free): Brute force is O(n^2). What is wasted?
  - H1 (-5): When a day is warmer than earlier days, those earlier days are resolved.
  - H2 (-10): Keep a stack of indices of unresolved days.
  - H3 (-20): The stack's temperatures are non-increasing from bottom to top.
- **Follow-ups:**
  - Next greater element in a circular array.
  - Largest rectangle in a histogram.
- **Mistakes the tests are built to catch:**
  - Using <= and resolving equal temperatures.
  - Storing temperatures instead of indices.
