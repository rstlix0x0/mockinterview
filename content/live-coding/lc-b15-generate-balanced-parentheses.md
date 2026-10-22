---
id: lc-b15-generate-balanced-parentheses
title: Generate Balanced Parentheses
type: live-coding
level: [junior, mid]
tags: [backtracking]
time_minutes: 20
languages: [python]
entry: generate_parentheses
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B15
---

# Generate Balanced Parentheses

## Statement

Return every string of `n` pairs of balanced parentheses, in lexicographic order (`(` sorts before `)`).

**Signature:** `generate_parentheses(n: int) -> string[]`

**Constraints:**
- 1 <= n <= 10

**Examples:**

- **Example 1** - input: `{"n":1}`  
  output: `["()"]`
- **Example 2** - input: `{"n":3}`  
  output: `["((()))","(()())","(())()","()(())","()()()"]`

## Stub

```python
def generate_parentheses(n):
    """generate_parentheses(n: int) -> string[]"""
    raise NotImplementedError
```

## Signature

```signature
generate_parentheses(n: int) -> string[]
```

## Tests

```json tests
{"function":"generate_parentheses","kind":"func","compare":"exact","fuzz":6,"perf":{"sizes":[8,9,10],"limit_ms":4000,"max_exponent":null},"cases":[
{"name":"example-1","tags":["visible"],"args":{"n":1}},
{"name":"example-2","tags":["visible"],"args":{"n":3}},
{"name":"edge-n-2","tags":["edge"],"args":{"n":2}},
{"name":"hidden-n-4","tags":["hidden"],"args":{"n":4}},
{"name":"hidden-n-8","tags":["hidden"],"args":{"n":8}}
]}
```

## Oracle

```python oracle
def solve(n):
    res = []

    def go(s, o, c):
        if len(s) == 2 * n:
            res.append(s)
            return
        if o < n:
            go(s + '(', o + 1, c)
        if c < o:
            go(s + ')', o, c + 1)
    go('', 0, 0)
    return res

def gen_random(seed):
    return {"n": (seed % 6) + 1}

def gen_perf(n):
    return {"n": n}
```

## Interviewer notes

- **Target complexity:** O(4^n / sqrt(n)) outputs (Catalan number)
- **Scaling check:** sizes [8, 9, 10], limit 4000 ms (calibrated to a straightforward Python solution)
- **Clarifying questions (answer verbatim):**
  - Q: Is the ordering required?  
    A: Yes, lexicographic.
- **Hint ladder:**
  - H0 (free): When may you add '('?
  - H1 (-5): While fewer than n have been opened.
  - H2 (-10): When may you add ')'?
  - H3 (-20): Only if closes < opens. Build strings left to right.
- **Follow-ups:**
  - Count them without generating (Catalan numbers).
  - Iterative version.
- **Mistakes the tests are built to catch:**
  - Generating all 2^(2n) strings and filtering.
  - Wrong ordering.
