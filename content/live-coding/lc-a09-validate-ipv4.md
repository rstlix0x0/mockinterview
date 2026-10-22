---
id: lc-a09-validate-ipv4
title: Validate an IPv4 Address
type: live-coding
level: [junior]
tags: [strings, validation]
time_minutes: 10
languages: [python]
entry: valid_ipv4
kind: func
runs_code: true
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

## Stub

```python
def valid_ipv4(s):
    """valid_ipv4(s: string) -> bool"""
    raise NotImplementedError
```

## Signature

```signature
valid_ipv4(s: string) -> bool
```

## Tests

```json tests
{"function":"valid_ipv4","kind":"func","compare":"exact","fuzz":20,"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"192.168.0.1"}},
{"name":"example-2","tags":["visible"],"args":{"s":"256.1.1.1"}},
{"name":"example-3","tags":["visible"],"args":{"s":"1.01.1.1"}},
{"name":"edge-empty","tags":["edge"],"args":{"s":""}},
{"name":"edge-three-parts","tags":["edge"],"args":{"s":"1.2.3"}},
{"name":"edge-five-parts","tags":["edge"],"args":{"s":"1.2.3.4.5"}},
{"name":"edge-empty-part","tags":["edge"],"args":{"s":"1..2.3"}},
{"name":"hidden-zeros","tags":["hidden"],"args":{"s":"0.0.0.0"}},
{"name":"hidden-plus","tags":["hidden"],"args":{"s":"+1.2.3.4"}},
{"name":"hidden-space","tags":["hidden"],"args":{"s":"1.2.3.4 "}},
{"name":"hidden-unicode-digit","tags":["hidden"],"args":{"s":"1.2.3.٤"}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    pieces = ["0", "1", "255", "256", "01", "", "a", "10", "-1", "1 "]
    return {"s": '.'.join(rnd.choice(pieces) for _ in range(rnd.choice([3, 4, 4, 4, 5])))}
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
