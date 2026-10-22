---
id: lc-b01-longest-unique-substring
title: Longest Substring Without Repeating Characters
type: live-coding
level: [junior, mid]
tags: [sliding-window, hash-map]
time_minutes: 25
entry: longest_unique_substring
kind: func
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

## Signature

```signature
longest_unique_substring(s: string) -> int
```

## Tests

```json tests
{"function":"longest_unique_substring","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"abcabcbb"},"expected":3},
{"name":"example-2","tags":["visible"],"args":{"s":"bbbbb"},"expected":1},
{"name":"example-3","tags":["visible"],"args":{"s":"pwwkew"},"expected":3},
{"name":"edge-empty","tags":["edge"],"args":{"s":""},"expected":0},
{"name":"edge-single","tags":["edge"],"args":{"s":"a"},"expected":1},
{"name":"hidden-abba","tags":["hidden"],"args":{"s":"abba"},"expected":2},
{"name":"hidden-all-unique","tags":["hidden"],"args":{"s":"abcdefg"},"expected":7},
{"name":"hidden-tail-best","tags":["hidden"],"args":{"s":"aabcdef"},"expected":6},
{"name":"hidden-spaces","tags":["hidden"],"args":{"s":"a b a"},"expected":3},
{"name":"random-1","tags":["hidden"],"args":{"s":"caaaaccba"},"expected":3},
{"name":"random-2","tags":["hidden"],"args":{"s":"aadda"},"expected":2},
{"name":"random-3","tags":["hidden"],"args":{"s":"baacac"},"expected":2},
{"name":"random-4","tags":["hidden"],"args":{"s":"adb"},"expected":3}
]}
```

## Reference solution

```python reference
def solve(s):
    last, start, best = {}, 0, 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best
```

## Interviewer notes

- **Target complexity:** O(n) time, O(min(n, alphabet)) space
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
