---
id: lc-b14-edit-distance
title: Edit Distance
type: live-coding
level: [junior, mid]
tags: [dynamic-programming, strings]
time_minutes: 30
languages: [python]
entry: edit_distance
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B14
---

# Edit Distance

## Statement

Return the minimum number of single-character insertions, deletions and substitutions needed to turn `a` into `b`.

**Signature:** `edit_distance(a: string, b: string) -> int`

**Constraints:**
- 0 <= len(a), len(b) <= 2000

**Examples:**

- **Example 1** - input: `{"a":"horse","b":"ros"}`  
  output: `3`
- **Example 2** - input: `{"a":"intention","b":"execution"}`  
  output: `5`

## Stub

```python
def edit_distance(a, b):
    """edit_distance(a: string, b: string) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"edit_distance","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[200,800,1500],"limit_ms":6000,"max_exponent":2.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"a":"horse","b":"ros"}},
{"name":"example-2","tags":["visible"],"args":{"a":"intention","b":"execution"}},
{"name":"edge-both-empty","tags":["edge"],"args":{"a":"","b":""}},
{"name":"edge-one-empty","tags":["edge"],"args":{"a":"","b":"abc"}},
{"name":"edge-equal","tags":["edge"],"args":{"a":"same","b":"same"}},
{"name":"hidden-transpose","tags":["hidden"],"args":{"a":"ab","b":"ba"}},
{"name":"hidden-prefix","tags":["hidden"],"args":{"a":"abc","b":"abcdef"}}
]}
```

## Oracle

```python oracle
def solve(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]

def gen_random(seed):
    rnd = random.Random(seed)
    return {"a": ''.join(rnd.choice("abc") for _ in range(rnd.randint(0, 7))),
            "b": ''.join(rnd.choice("abc") for _ in range(rnd.randint(0, 7)))}

def gen_perf(n):
    rnd = random.Random(14)
    return {"a": ''.join(rnd.choice("abc") for _ in range(n)), "b": ''.join(rnd.choice("abc") for _ in range(n))}
```

## Interviewer notes

- **Target complexity:** O(|a| * |b|) time, O(min(|a|, |b|)) space with two rows
- **Scaling check:** sizes [200, 800, 1500], limit 6000 ms (calibrated to a straightforward Python solution), growth exponent at most 2.4
- **Clarifying questions (answer verbatim):**
  - Q: Is a swap of adjacent characters one operation?  
    A: No: only insert, delete, substitute.
- **Hint ladder:**
  - H0 (free): Define d(i, j) for the prefixes a[:i], b[:j].
  - H1 (-5): If the last characters match, d(i, j) = d(i-1, j-1).
  - H2 (-10): Otherwise 1 + min of delete, insert, substitute.
  - H3 (-20): You only need the previous row.
- **Follow-ups:**
  - Recover the edit script.
  - Banded version when the distance is known to be small (<= k).
- **Mistakes the tests are built to catch:**
  - Wrong base cases d(i, 0) = i and d(0, j) = j.
  - Recursion without memoization.
  - 2D array of 2001 x 2001 objects in a slow language.
