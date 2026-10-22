---
id: lc-b11-minimum-window-substring
title: Minimum Window Substring
type: live-coding
level: [mid, senior]
tags: [sliding-window, hash-map]
time_minutes: 40
entry: min_window
kind: func
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

## Signature

```signature
min_window(s: string, t: string) -> string
```

## Tests

```json tests
{"function":"min_window","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"ADOBECODEBANC","t":"ABC"},"expected":"BANC"},
{"name":"example-2","tags":["visible"],"args":{"s":"a","t":"aa"},"expected":""},
{"name":"example-3","tags":["visible"],"args":{"s":"abcabdebac","t":"cda"},"expected":"cabd"},
{"name":"edge-empty-s","tags":["edge"],"args":{"s":"","t":"a"},"expected":""},
{"name":"edge-whole-string","tags":["edge"],"args":{"s":"abc","t":"abc"},"expected":"abc"},
{"name":"hidden-multiplicity","tags":["hidden"],"args":{"s":"aabdecab","t":"aab"},"expected":"aab"},
{"name":"hidden-tie-leftmost","tags":["hidden"],"args":{"s":"abxab","t":"ab"},"expected":"ab"},
{"name":"hidden-t-longer","tags":["hidden"],"args":{"s":"ab","t":"abc"},"expected":""},
{"name":"random-1","tags":["hidden"],"args":{"s":"bacacacca","t":"cba"},"expected":"bac"},
{"name":"random-2","tags":["hidden"],"args":{"s":"aabcb","t":"c"},"expected":"c"},
{"name":"random-3","tags":["hidden"],"args":{"s":"aacacb","t":"c"},"expected":"c"},
{"name":"random-4","tags":["hidden"],"args":{"s":"aba","t":"bbbb"},"expected":""}
]}
```

## Reference solution

```python reference
from collections import Counter

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
```

## Interviewer notes

- **Target complexity:** O(|s| + |t|) time
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
