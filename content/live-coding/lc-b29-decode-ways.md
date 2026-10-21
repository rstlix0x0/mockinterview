---
id: lc-b29-decode-ways
title: Decode Ways
type: live-coding
level: [junior, mid]
tags: [dynamic-programming, strings]
time_minutes: 25
languages: [python]
entry: decode_ways
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B29
---

# Decode Ways

## Statement

A message of letters was encoded with `A=1, B=2, ... Z=26`. Given the digit string `s`, return the number of ways to decode it. Leading zeros are invalid (`"06"` cannot be decoded); `"0"` alone cannot be decoded. The empty string has 0 ways. The answer fits in a signed 64-bit integer.

**Signature:** `decode_ways(s: string) -> int`

**Constraints:**
- 0 <= len(s) <= 90
- digits only

**Examples:**

- **Example 1** - input: `{"s":"12"}`  
  output: `2`
- **Example 2** - input: `{"s":"226"}`  
  output: `3`
- **Example 3** - input: `{"s":"06"}`  
  output: `0`

## Stub

```python
def decode_ways(s):
    """decode_ways(s: string) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"decode_ways","kind":"func","compare":"exact","fuzz":40,"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"12"}},
{"name":"example-2","tags":["visible"],"args":{"s":"226"}},
{"name":"example-3","tags":["visible"],"args":{"s":"06"}},
{"name":"edge-empty","tags":["edge"],"args":{"s":""}},
{"name":"edge-zero","tags":["edge"],"args":{"s":"0"}},
{"name":"edge-ten","tags":["edge"],"args":{"s":"10"}},
{"name":"hidden-twenty-seven","tags":["hidden"],"args":{"s":"27"}},
{"name":"hidden-double-zero","tags":["hidden"],"args":{"s":"100"}},
{"name":"hidden-long","tags":["hidden"],"args":{"s":"111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"}}
]}
```

## Oracle

```python oracle
def solve(s):
    if not s:
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 0 if s[0] == "0" else 1
    for i in range(2, n + 1):
        if s[i - 1] != "0":
            dp[i] += dp[i - 1]
        if 10 <= int(s[i - 2:i]) <= 26:
            dp[i] += dp[i - 2]
    return dp[n]

def gen_random(seed):
    rnd = random.Random(seed)
    return {"s": ''.join(rnd.choice("0123456789" if rnd.random() < 0.3 else "12") for _ in range(rnd.randint(0, 12)))}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
- **Clarifying questions (answer verbatim):**
  - Q: Is '00' valid?  
    A: No.
- **Hint ladder:**
  - H0 (free): Count prefixes: ways(i) depends on the last one or two digits.
  - H1 (-5): A single digit 1-9 adds ways(i-1).
  - H2 (-10): A two-digit number 10-26 adds ways(i-2).
  - H3 (-20): Zeros only work as the second digit of 10 or 20.
- **Follow-ups:**
  - Return the decoded strings.
  - Allow '*' as a wildcard digit.
- **Mistakes the tests are built to catch:**
  - Treating '0' as a valid single digit.
  - Accepting two-digit values with a leading zero (`06`).
  - Plain recursion (exponential on 90 ones).
