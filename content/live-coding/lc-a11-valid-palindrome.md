---
id: lc-a11-valid-palindrome
title: Valid Palindrome
type: live-coding
level: [junior]
tags: [strings, two-pointers]
time_minutes: 10
languages: [python]
entry: is_palindrome
kind: func
runs_code: true
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

## Stub

```python
def is_palindrome(s):
    """is_palindrome(s: string) -> bool"""
    raise NotImplementedError
```

## Signature

```signature
is_palindrome(s: string) -> bool
```

## Tests

```json tests
{"function":"is_palindrome","kind":"func","compare":"exact","fuzz":20,"perf":{"sizes":[100000,500000,1000000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"A man, a plan, a canal: Panama"}},
{"name":"example-2","tags":["visible"],"args":{"s":"race a car"}},
{"name":"edge-empty","tags":["edge"],"args":{"s":""}},
{"name":"edge-only-punctuation","tags":["edge"],"args":{"s":".,! ?"}},
{"name":"hidden-digits-and-letters","tags":["hidden"],"args":{"s":"0P"}},
{"name":"hidden-single","tags":["hidden"],"args":{"s":"a"}}
]}
```

## Oracle

```python oracle
def solve(s):
    keep = [c.lower() for c in s if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]
    return keep == keep[::-1]

def gen_random(seed):
    rnd = random.Random(seed)
    half = ''.join(rnd.choice("abAB1 ,.") for _ in range(rnd.randint(0, 6)))
    mid = rnd.choice(["", "x", " ", "?"])
    s = half + mid + (half[::-1] if rnd.random() < 0.6 else ''.join(rnd.choice("abAB1 ,.") for _ in range(len(half))))
    return {"s": s}

def gen_perf(n):
    half = "ab" * (n // 2)
    return {"s": half + half[::-1]}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) extra space with two pointers
- **Scaling check:** sizes [100000, 500000, 1000000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
