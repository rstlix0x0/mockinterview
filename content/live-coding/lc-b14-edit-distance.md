---
id: lc-b14-edit-distance
title: Edit Distance
type: live-coding
level: [junior, mid]
tags: [dynamic-programming, strings]
time_minutes: 30
entry: edit_distance
kind: func
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

## Signature

```signature
edit_distance(a: string, b: string) -> int
```

## Tests

```json tests
{"function":"edit_distance","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"a":"horse","b":"ros"},"expected":3},
{"name":"example-2","tags":["visible"],"args":{"a":"intention","b":"execution"},"expected":5},
{"name":"edge-both-empty","tags":["edge"],"args":{"a":"","b":""},"expected":0},
{"name":"edge-one-empty","tags":["edge"],"args":{"a":"","b":"abc"},"expected":3},
{"name":"edge-equal","tags":["edge"],"args":{"a":"same","b":"same"},"expected":0},
{"name":"hidden-transpose","tags":["hidden"],"args":{"a":"ab","b":"ba"},"expected":2},
{"name":"hidden-prefix","tags":["hidden"],"args":{"a":"abc","b":"abcdef"},"expected":3},
{"name":"random-1","tags":["hidden"],"args":{"a":"acac","b":""},"expected":4},
{"name":"random-2","tags":["hidden"],"args":{"a":"aabcb","b":"c"},"expected":4},
{"name":"random-3","tags":["hidden"],"args":{"a":"aacacb","b":""},"expected":6},
{"name":"random-4","tags":["hidden"],"args":{"a":"aba","b":"bbbbba"},"expected":4}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(|a| * |b|) time, O(min(|a|, |b|)) space with two rows
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
