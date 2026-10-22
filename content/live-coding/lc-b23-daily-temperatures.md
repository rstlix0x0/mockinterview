---
id: lc-b23-daily-temperatures
title: Days Until a Warmer Temperature
type: live-coding
level: [junior, mid]
tags: [stack, monotonic-stack]
time_minutes: 25
languages: [python]
entry: daily_temperatures
kind: func
runs_code: true
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

## Stub

```python
def daily_temperatures(temps):
    """daily_temperatures(temps: int[]) -> int[]"""
    raise NotImplementedError
```

## Signature

```signature
daily_temperatures(temps: int[]) -> int[]
```

## Tests

```json tests
{"function":"daily_temperatures","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[50000,200000,500000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"temps":[73,74,75,71,69,72,76,73]}},
{"name":"example-2","tags":["visible"],"args":{"temps":[30,40,50,60]}},
{"name":"edge-empty","tags":["edge"],"args":{"temps":[]}},
{"name":"edge-descending","tags":["edge"],"args":{"temps":[5,4,3]}},
{"name":"edge-equal","tags":["edge"],"args":{"temps":[7,7,7]}},
{"name":"hidden-valley","tags":["hidden"],"args":{"temps":[5,1,1,6]}}
]}
```

## Oracle

```python oracle
def solve(temps):
    ans = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans

def gen_random(seed):
    rnd = random.Random(seed)
    return {"temps": [rnd.randint(30, 40) for _ in range(rnd.randint(0, 12))]}

def gen_perf(n):
    rnd = random.Random(223)
    return {"temps": [rnd.randint(30, 100) for _ in range(n)]}
```

## Interviewer notes

- **Target complexity:** O(n) time
- **Scaling check:** sizes [50000, 200000, 500000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
