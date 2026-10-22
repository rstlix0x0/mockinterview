---
id: lc-a11-valid-palindrome
title: Valid Palindrome
type: live-coding
level: [junior]
tags: [strings, two-pointers]
time_minutes: 10
entry: is_palindrome
kind: func
source: adapted
author: mockinterview
legacy_id: A11
---

# Valid Palindrome

## Statement

Return `true` if `s` reads the same forwards and backwards when you keep only ASCII letters and digits and ignore letter case. An empty result (no letters or digits) is a palindrome.

**Signature:** `is_palindrome(s: string) -> bool`

**Constraints:**
- 0 <= len(s) <= 1000000

**Examples:**

- **Example 1** - input: `{"s":"A man, a plan, a canal: Panama"}`  
  output: `true`
- **Example 2** - input: `{"s":"race a car"}`  
  output: `false`

## Signature

```signature
is_palindrome(s: string) -> bool
```

## Tests

```json tests
{"function":"is_palindrome","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"A man, a plan, a canal: Panama"},"expected":true},
{"name":"example-2","tags":["visible"],"args":{"s":"race a car"},"expected":false},
{"name":"edge-empty","tags":["edge"],"args":{"s":""},"expected":true},
{"name":"edge-only-punctuation","tags":["edge"],"args":{"s":".,! ?"},"expected":true},
{"name":"hidden-digits-and-letters","tags":["hidden"],"args":{"s":"0P"},"expected":false},
{"name":"hidden-single","tags":["hidden"],"args":{"s":"a"},"expected":true},
{"name":"random-1","tags":["hidden"],"args":{"s":"1abaaba1"},"expected":true},
{"name":"random-2","tags":["hidden"],"args":{"s":"bb?bb"},"expected":true},
{"name":"random-3","tags":["hidden"],"args":{"s":"Bba abB"},"expected":true},
{"name":"random-4","tags":["hidden"],"args":{"s":"Ba,A,, ,,A,aB"},"expected":true}
]}
```

## Reference solution

```python reference
def solve(s):
    keep = [c.lower() for c in s if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]
    return keep == keep[::-1]
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) extra space with two pointers
- **Clarifying questions (answer verbatim):**
  - Q: Non-ASCII letters?  
    A: They are ignored like punctuation.
- **Hint ladder:**
  - H0 (free): Do you need a cleaned copy of the string?
  - H1 (-5): Two pointers moving inward.
  - H2 (-10): Skip characters that are not alphanumeric.
  - H3 (-20): Compare lower-cased characters.
- **Follow-ups:**
  - Allow deleting at most one character (valid palindrome II).
  - Longest palindromic substring.
- **Mistakes the tests are built to catch:**
  - `0P` is not a palindrome: comparing `'0'` with `'p'` must fail.
  - Pointers crossing over inside the skip loops.
  - Using Unicode-aware classification when the statement says ASCII.
