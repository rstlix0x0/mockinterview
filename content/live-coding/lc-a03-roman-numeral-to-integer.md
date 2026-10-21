---
id: lc-a03-roman-numeral-to-integer
title: Roman Numeral to Integer
type: live-coding
level: [junior]
tags: [strings, parsing]
time_minutes: 10
languages: [python]
entry: roman_to_int
kind: func
runs_code: true
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

## Stub

```python
def roman_to_int(s):
    """roman_to_int(s: string) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"roman_to_int","kind":"func","compare":"exact","fuzz":10,"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"III"}},
{"name":"example-2","tags":["visible"],"args":{"s":"LVIII"}},
{"name":"example-3","tags":["visible"],"args":{"s":"MCMXCIV"}},
{"name":"edge-min","tags":["edge"],"args":{"s":"I"}},
{"name":"edge-max","tags":["edge"],"args":{"s":"MMMCMXCIX"}},
{"name":"hidden-iv","tags":["hidden"],"args":{"s":"IV"}},
{"name":"hidden-xl","tags":["hidden"],"args":{"s":"XLIX"}}
]}
```

## Oracle

```python oracle
def solve(s):
    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total = 0
    for i, ch in enumerate(s):
        if i + 1 < len(s) and v[ch] < v[s[i + 1]]:
            total -= v[ch]
        else:
            total += v[ch]
    return total

def gen_random(seed):
    n = random.Random(seed).randint(1, 3999)
    out = ''
    for val, sym in [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
                     (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]:
        while n >= val:
            out += sym
            n -= val
    return {"s": out}
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
