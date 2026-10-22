---
id: lc-a02-valid-brackets
title: Valid Brackets
type: live-coding
level: [junior]
tags: [stack, strings]
time_minutes: 10
entry: valid_brackets
kind: func
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

## Signature

```signature
valid_brackets(s: string) -> bool
```

## Tests

```json tests
{"function":"valid_brackets","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"([]{})"},"expected":true},
{"name":"example-2","tags":["visible"],"args":{"s":"(]"},"expected":false},
{"name":"example-3","tags":["visible"],"args":{"s":"a(b)c"},"expected":true},
{"name":"edge-empty","tags":["edge"],"args":{"s":""},"expected":true},
{"name":"edge-only-closer","tags":["edge"],"args":{"s":")"},"expected":false},
{"name":"edge-unclosed","tags":["edge"],"args":{"s":"(("},"expected":false},
{"name":"hidden-interleaved","tags":["hidden"],"args":{"s":"([)]"},"expected":false},
{"name":"hidden-deep","tags":["hidden"],"args":{"s":"{[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[({[()]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]})]}"},"expected":true},
{"name":"random-1","tags":["hidden"],"args":{"s":"{()(({}[)"},"expected":false},
{"name":"random-2","tags":["hidden"],"args":{"s":"))aa)"},"expected":false},
{"name":"random-3","tags":["hidden"],"args":{"s":"])(}({"},"expected":false},
{"name":"random-4","tags":["hidden"],"args":{"s":"(a["},"expected":false}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(n) time, O(n) space
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
