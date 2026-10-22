---
id: lc-b01-longest-unique-substring
title: Longest Substring Without Repeating Characters
type: live-coding
level: [junior, mid]
tags: [sliding-window, hash-map]
time_minutes: 25
languages: [python]
entry: longest_unique_substring
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B1
---

# Longest Substring Without Repeating Characters

## Statement

Return the length of the longest substring of `s` that contains no repeated character.

**Signature:** `longest_unique_substring(s: string) -> int`

**Constraints:**
- 0 <= len(s) <= 500000
- any ASCII characters

**Examples:**

- **Example 1** - input: `{"s":"abcabcbb"}`  
  output: `3`
- **Example 2** - input: `{"s":"bbbbb"}`  
  output: `1`
- **Example 3** - input: `{"s":"pwwkew"}`  
  output: `3`

## Stub

```python
def longest_unique_substring(s):
    """longest_unique_substring(s: string) -> int"""
    raise NotImplementedError
```

## Signature

```signature
longest_unique_substring(s: string) -> int
```

## Tests

```json tests
{"function":"longest_unique_substring","kind":"func","compare":"exact","fuzz":15,"perf":{"sizes":[50000,200000,500000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"abcabcbb"}},
{"name":"example-2","tags":["visible"],"args":{"s":"bbbbb"}},
{"name":"example-3","tags":["visible"],"args":{"s":"pwwkew"}},
{"name":"edge-empty","tags":["edge"],"args":{"s":""}},
{"name":"edge-single","tags":["edge"],"args":{"s":"a"}},
{"name":"hidden-abba","tags":["hidden"],"args":{"s":"abba"}},
{"name":"hidden-all-unique","tags":["hidden"],"args":{"s":"abcdefg"}},
{"name":"hidden-tail-best","tags":["hidden"],"args":{"s":"aabcdef"}},
{"name":"hidden-spaces","tags":["hidden"],"args":{"s":"a b a"}}
]}
```

## Oracle

```python oracle
def solve(s):
    last, start, best = {}, 0, 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best

def gen_random(seed):
    rnd = random.Random(seed)
    return {"s": ''.join(rnd.choice("abcd") for _ in range(rnd.randint(0, 12)))}

def gen_perf(n):
    rnd = random.Random(2)
    return {"s": ''.join(rnd.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n))}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(min(n, alphabet)) space
- **Scaling check:** sizes [50000, 200000, 500000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Substring or subsequence?  
    A: Substring: contiguous.
- **Hint ladder:**
  - H0 (free): What is the brute-force cost and where does it repeat work?
  - H1 (-5): Keep a window [start, i] with no duplicates.
  - H2 (-10): When you see a repeat inside the window, move start just past its previous index.
  - H3 (-20): Store last-seen indices and only move start forward.
- **Follow-ups:**
  - At most K distinct characters.
  - Return the substring itself, leftmost on ties.
- **Mistakes the tests are built to catch:**
  - Moving `start` backwards on 'abba'.
  - Resetting the window and losing characters.
  - O(n^2) with a set rebuilt per start.
