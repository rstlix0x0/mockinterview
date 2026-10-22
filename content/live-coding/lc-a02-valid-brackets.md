---
id: lc-a02-valid-brackets
title: Valid Brackets
type: live-coding
level: [junior]
tags: [stack, strings]
time_minutes: 10
languages: [python]
entry: valid_brackets
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: A2
---

# Valid Brackets

## Statement

Return `true` if every bracket in `s` is closed by the same type in the correct order. The bracket types are `()`, `[]` and `{}`. Any other character is ignored. An empty string is valid.

**Signature:** `valid_brackets(s: string) -> bool`

**Constraints:**
- 0 <= len(s) <= 1000000

**Examples:**

- **Example 1** - input: `{"s":"([]{})"}`  
  output: `true`
- **Example 2** - input: `{"s":"(]"}`  
  output: `false`
- **Example 3** - input: `{"s":"a(b)c"}`  
  output: `true`

## Stub

```python
def valid_brackets(s):
    """valid_brackets(s: string) -> bool"""
    raise NotImplementedError
```

## Signature

```signature
valid_brackets(s: string) -> bool
```

## Tests

```json tests
{"function":"valid_brackets","kind":"func","compare":"exact","fuzz":6,"perf":{"sizes":[100000,500000,1000000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"([]{})"}},
{"name":"example-2","tags":["visible"],"args":{"s":"(]"}},
{"name":"example-3","tags":["visible"],"args":{"s":"a(b)c"}},
{"name":"edge-empty","tags":["edge"],"args":{"s":""}},
{"name":"edge-only-closer","tags":["edge"],"args":{"s":")"}},
{"name":"edge-unclosed","tags":["edge"],"args":{"s":"(("}},
{"name":"hidden-interleaved","tags":["hidden"],"args":{"s":"([)]"}},
{"name":"hidden-deep","tags":["hidden"],"args":{"s":"{[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[()]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]}"}}
]}
```

## Oracle

```python oracle
def solve(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack

def gen_random(seed):
    rnd = random.Random(seed)
    return {"s": ''.join(rnd.choice("()[]{}ab") for _ in range(rnd.randint(0, 10)))}

def gen_perf(n):
    return {"s": '(' * (n // 2) + ')' * (n // 2)}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(n) space
- **Scaling check:** sizes [100000, 500000, 1000000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Are letters allowed?  
    A: Yes, they are ignored.
  - Q: Is the empty string valid?  
    A: Yes.
- **Hint ladder:**
  - H0 (free): Which bracket must be closed first?
  - H1 (-5): That is last-in-first-out.
  - H2 (-10): Push openers; on a closer compare with the top.
  - H3 (-20): Remember the empty-stack case and leftover openers at the end.
- **Follow-ups:**
  - Return the index of the first invalid character.
  - Return the length of the longest valid substring.
- **Mistakes the tests are built to catch:**
  - Popping from an empty stack.
  - Forgetting leftover openers.
  - Recursion that overflows on 500000 nested brackets.
