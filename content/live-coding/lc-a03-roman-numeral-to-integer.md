---
id: lc-a03-roman-numeral-to-integer
title: Roman Numeral to Integer
type: live-coding
level: [junior]
tags: [strings, parsing]
time_minutes: 10
entry: roman_to_int
kind: func
source: adapted
author: mockinterview
legacy_id: A3
---

# Roman Numeral to Integer

## Statement

Convert a valid Roman numeral to an integer. Subtractive pairs (IV, IX, XL, XC, CD, CM) are used. The input is always a valid numeral from 1 to 3999.

**Signature:** `roman_to_int(s: string) -> int`

**Constraints:**
- valid numeral, value between 1 and 3999

**Examples:**

- **Example 1** - input: `{"s":"III"}`  
  output: `3`
- **Example 2** - input: `{"s":"LVIII"}`  
  output: `58`
- **Example 3** - input: `{"s":"MCMXCIV"}`  
  output: `1994`

## Signature

```signature
roman_to_int(s: string) -> int
```

## Tests

```json tests
{"function":"roman_to_int","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"III"},"expected":3},
{"name":"example-2","tags":["visible"],"args":{"s":"LVIII"},"expected":58},
{"name":"example-3","tags":["visible"],"args":{"s":"MCMXCIV"},"expected":1994},
{"name":"edge-min","tags":["edge"],"args":{"s":"I"},"expected":1},
{"name":"edge-max","tags":["edge"],"args":{"s":"MMMCMXCIX"},"expected":3999},
{"name":"hidden-iv","tags":["hidden"],"args":{"s":"IV"},"expected":4},
{"name":"hidden-xl","tags":["hidden"],"args":{"s":"XLIX"},"expected":49},
{"name":"random-1","tags":["hidden"],"args":{"s":"MMCCCLXVIII"},"expected":2368},
{"name":"random-2","tags":["hidden"],"args":{"s":"MCDLX"},"expected":1460},
{"name":"random-3","tags":["hidden"],"args":{"s":"MDXCVIII"},"expected":1598},
{"name":"random-4","tags":["hidden"],"args":{"s":"MMMDLXXVIII"},"expected":3578}
]}
```

## Reference solution

```python reference
def solve(s):
    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total = 0
    for i, ch in enumerate(s):
        if i + 1 < len(s) and v[ch] < v[s[i + 1]]:
            total -= v[ch]
        else:
            total += v[ch]
    return total
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
- **Clarifying questions (answer verbatim):**
  - Q: Do I need to validate the input?  
    A: No, it is always valid.
- **Hint ladder:**
  - H0 (free): When is a symbol subtracted rather than added?
  - H1 (-5): Compare each symbol with the next one.
  - H2 (-10): Subtract when the value is smaller than its right neighbour; otherwise add.
  - H3 (-20): Mind the last character.
- **Follow-ups:**
  - Write int_to_roman.
  - Validate arbitrary strings and reject non-canonical forms such as IIII or IC.
- **Mistakes the tests are built to catch:**
  - Handling subtractive pairs with a lookup table but missing XL/XC/CD/CM.
  - Reading past the end of the string.
