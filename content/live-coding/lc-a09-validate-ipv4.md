---
id: lc-a09-validate-ipv4
title: Validate an IPv4 Address
type: live-coding
level: [junior]
tags: [strings, validation]
time_minutes: 10
entry: valid_ipv4
kind: func
source: adapted
author: mockinterview
legacy_id: A9
---

# Validate an IPv4 Address

## Statement

Return `true` if `s` is a valid dotted-decimal IPv4 address: exactly four decimal parts separated by dots, each part made only of ASCII digits, with a value from 0 to 255 and no leading zeros (the part `0` itself is fine). No whitespace or signs are allowed.

**Signature:** `valid_ipv4(s: string) -> bool`

**Constraints:**
- 0 <= len(s) <= 100

**Examples:**

- **Example 1** - input: `{"s":"192.168.0.1"}`  
  output: `true`
- **Example 2** - input: `{"s":"256.1.1.1"}`  
  output: `false`
- **Example 3** - input: `{"s":"1.01.1.1"}`  
  output: `false`

## Signature

```signature
valid_ipv4(s: string) -> bool
```

## Tests

```json tests
{"function":"valid_ipv4","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"192.168.0.1"},"expected":true},
{"name":"example-2","tags":["visible"],"args":{"s":"256.1.1.1"},"expected":false},
{"name":"example-3","tags":["visible"],"args":{"s":"1.01.1.1"},"expected":false},
{"name":"edge-empty","tags":["edge"],"args":{"s":""},"expected":false},
{"name":"edge-three-parts","tags":["edge"],"args":{"s":"1.2.3"},"expected":false},
{"name":"edge-five-parts","tags":["edge"],"args":{"s":"1.2.3.4.5"},"expected":false},
{"name":"edge-empty-part","tags":["edge"],"args":{"s":"1..2.3"},"expected":false},
{"name":"hidden-zeros","tags":["hidden"],"args":{"s":"0.0.0.0"},"expected":true},
{"name":"hidden-plus","tags":["hidden"],"args":{"s":"+1.2.3.4"},"expected":false},
{"name":"hidden-space","tags":["hidden"],"args":{"s":"1.2.3.4 "},"expected":false},
{"name":"hidden-unicode-digit","tags":["hidden"],"args":{"s":"1.2.3.٤"},"expected":false},
{"name":"random-1","tags":["hidden"],"args":{"s":"01.0.1.0.0"},"expected":false},
{"name":"random-2","tags":["hidden"],"args":{"s":"1.1.a.1 "},"expected":false},
{"name":"random-3","tags":["hidden"],"args":{"s":"256.1.1 .0"},"expected":false},
{"name":"random-4","tags":["hidden"],"args":{"s":"0.a.255.a"},"expected":false}
]}
```

## Reference solution

```python reference
def solve(s):
    parts = s.split('.')
    if len(parts) != 4:
        return False
    for p in parts:
        if not p or not (p.isascii() and p.isdigit()):
            return False
        if len(p) > 1 and p[0] == '0':
            return False
        if int(p) > 255:
            return False
    return True
```

## Interviewer notes

- **Target complexity:** O(n)
- **Clarifying questions (answer verbatim):**
  - Q: Is 0.0.0.0 valid?  
    A: Yes.
  - Q: Are leading zeros allowed?  
    A: No, except the single digit 0.
- **Hint ladder:**
  - H0 (free): List every rule before coding.
  - H1 (-5): Split on dots and validate each part independently.
  - H2 (-10): Check emptiness, digit-only, leading zero, range, in that order.
  - H3 (-20): Beware of language helpers that accept signs, whitespace or Unicode digits.
- **Follow-ups:**
  - Validate IPv6.
  - Parse CIDR notation and test membership.
- **Mistakes the tests are built to catch:**
  - Using a language integer parser that accepts '+1' or ' 1'.
  - Overflow on a very long digit string before the range check.
