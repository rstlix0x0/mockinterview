---
id: lc-b28-longest-palindrome
title: Longest Palindromic Substring
type: live-coding
level: [junior, mid]
tags: [strings, expand-around-center, dp]
time_minutes: 30
languages: [python]
entry: longest_palindrome
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B28
---

# Longest Palindromic Substring

## Statement

Return the longest palindromic substring of `s`. If several have the same maximum length, return the one that starts first. The empty string returns `""`.

**Signature:** `longest_palindrome(s: string) -> string`

**Constraints:**
- 0 <= len(s) <= 3000

**Examples:**

- **Example 1** - input: `{"s":"babad"}`  
  output: `"bab"`
- **Example 2** - input: `{"s":"cbbd"}`  
  output: `"bb"`

## Stub

```python
def longest_palindrome(s):
    """longest_palindrome(s: string) -> string"""
    raise NotImplementedError
```

## Signature

```signature
longest_palindrome(s: string) -> string
```

## Tests

```json tests
{"function":"longest_palindrome","kind":"func","compare":"exact","fuzz":40,"perf":{"sizes":[500,1500,3000],"limit_ms":5000,"max_exponent":2.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"babad"}},
{"name":"example-2","tags":["visible"],"args":{"s":"cbbd"}},
{"name":"edge-empty","tags":["edge"],"args":{"s":""}},
{"name":"edge-single","tags":["edge"],"args":{"s":"a"}},
{"name":"edge-all-same","tags":["edge"],"args":{"s":"aaaa"}},
{"name":"hidden-tie-leftmost","tags":["hidden"],"args":{"s":"abcd"}},
{"name":"hidden-even-center","tags":["hidden"],"args":{"s":"abccba"}}
]}
```

## Oracle

```python oracle
def solve(s):
    best_l, best_r = 0, 0
    for c in range(len(s)):
        for l, r in ((c, c), (c, c + 1)):
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            if (r - l - 1) > (best_r - best_l):
                best_l, best_r = l + 1, r
    return s[best_l:best_r]

def gen_random(seed):
    rnd = random.Random(seed)
    return {"s": ''.join(rnd.choice("abc") for _ in range(rnd.randint(0, 12)))}

def gen_perf(n):
    return {"s": "a" * n}
```

## Interviewer notes

- **Target complexity:** O(n^2) time, O(1) space (expand around centres); Manacher is O(n)
- **Scaling check:** sizes [500, 1500, 3000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 2.4
- **Clarifying questions (answer verbatim):**
  - Q: Which one on ties?  
    A: The leftmost.
- **Hint ladder:**
  - H0 (free): Brute force checks all substrings: how expensive is that?
  - H1 (-5): Every palindrome has a centre.
  - H2 (-10): 2n - 1 centres (odd and even lengths). Expand outwards while characters match.
  - H3 (-20): Track the best (start, length) and update only on strictly longer.
- **Follow-ups:**
  - Count all palindromic substrings.
  - Manacher's algorithm for O(n).
- **Mistakes the tests are built to catch:**
  - Forgetting even-length palindromes.
  - Updating on >= (returns the rightmost tie).
  - O(n^3) brute force.
