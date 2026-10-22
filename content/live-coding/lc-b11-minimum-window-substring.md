---
id: lc-b11-minimum-window-substring
title: Minimum Window Substring
type: live-coding
level: [mid, senior]
tags: [sliding-window, hash-map]
time_minutes: 40
languages: [python]
entry: min_window
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B11
---

# Minimum Window Substring

## Statement

Return the shortest substring of `s` that contains every character of `t` with at least the same multiplicity (`t = "aab"` needs two `a` and one `b`). If several windows tie, return the leftmost. Return `""` if no window exists. `t` is non-empty.

**Signature:** `min_window(s: string, t: string) -> string`

**Constraints:**
- 0 <= len(s) <= 500000
- 1 <= len(t) <= 1000

**Examples:**

- **Example 1** - input: `{"s":"ADOBECODEBANC","t":"ABC"}`  
  output: `"BANC"`
- **Example 2** - input: `{"s":"a","t":"aa"}`  
  output: `""`
- **Example 3** - input: `{"s":"abcabdebac","t":"cda"}`  
  output: `"cabd"`

## Stub

```python
def min_window(s, t):
    """min_window(s: string, t: string) -> string"""
    raise NotImplementedError
```

## Signature

```signature
min_window(s: string, t: string) -> string
```

## Tests

```json tests
{"function":"min_window","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[50000,200000,500000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"ADOBECODEBANC","t":"ABC"}},
{"name":"example-2","tags":["visible"],"args":{"s":"a","t":"aa"}},
{"name":"example-3","tags":["visible"],"args":{"s":"abcabdebac","t":"cda"}},
{"name":"edge-empty-s","tags":["edge"],"args":{"s":"","t":"a"}},
{"name":"edge-whole-string","tags":["edge"],"args":{"s":"abc","t":"abc"}},
{"name":"hidden-multiplicity","tags":["hidden"],"args":{"s":"aabdecab","t":"aab"}},
{"name":"hidden-tie-leftmost","tags":["hidden"],"args":{"s":"abxab","t":"ab"}},
{"name":"hidden-t-longer","tags":["hidden"],"args":{"s":"ab","t":"abc"}}
]}
```

## Oracle

```python oracle
def solve(s, t):
    need = Counter(t)
    missing = len(t)
    best = (float('inf'), 0, 0)
    left = 0
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right + 1)
            need[s[left]] += 1
            missing += 1
            left += 1
    return "" if best[0] == float('inf') else s[best[1]:best[2]]

def gen_random(seed):
    rnd = random.Random(seed)
    return {"s": ''.join(rnd.choice("abc") for _ in range(rnd.randint(0, 12))),
            "t": ''.join(rnd.choice("abc") for _ in range(rnd.randint(1, 4)))}

def gen_perf(n):
    rnd = random.Random(11)
    return {"s": ''.join(rnd.choice("abcdefghij") for _ in range(n)), "t": "abcdefghijaabb"}
```

## Interviewer notes

- **Target complexity:** O(|s| + |t|) time
- **Scaling check:** sizes [50000, 200000, 500000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Case sensitive?  
    A: Yes.
- **Hint ladder:**
  - H0 (free): Expand until the window is valid, then shrink as far as possible.
  - H1 (-5): Track how many required characters are still missing.
  - H2 (-10): A map of needs, where counts can go negative for surplus characters.
  - H3 (-20): Record the best window every time you are valid, before moving left.
- **Follow-ups:**
  - Return all minimum windows.
  - Stream: characters arrive one at a time.
- **Mistakes the tests are built to catch:**
  - Ignoring multiplicity.
  - Shrinking too early.
  - Not returning the leftmost on ties (use strict < when updating).
