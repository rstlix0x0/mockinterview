---
id: lc-c06-arithmetic-expression-evaluator
title: Arithmetic Expression Evaluator
type: live-coding
level: [mid, senior]
tags: [parsing, recursion, grammar]
time_minutes: 40
entry: evaluate
kind: func
source: adapted
author: mockinterview
legacy_id: C6
---

# Arithmetic Expression Evaluator

## Statement

Evaluate an arithmetic expression over **integers** and return the integer result, or the string `"ERROR"` for anything invalid. Supported: non-negative integer literals (leading zeros allowed), binary `+ - * /`, unary `-` (it can repeat: `--3` is 3), parentheses, and spaces anywhere between tokens. `*` and `/` bind tighter than `+` and `-`; all binary operators are left-associative. `/` is integer division **truncating toward zero** (`-7/2 = -3`). Return `"ERROR"` for division by zero, unbalanced parentheses, an empty expression, two adjacent numbers (`"2 3"`), a dangling operator, unary plus, or any other character.

Do not call `eval` or any equivalent.

**Signature:** `evaluate(expr: string) -> int | "ERROR"`

**Constraints:**
- 0 <= len(expr) <= 400000
- parenthesis nesting depth <= 100
- results fit in 64-bit signed integers in all tests

**Examples:**

- **Example 1** - input: `{"expr":"1 + 2 * 3"}`  
  output: `7`
- **Example 2** - input: `{"expr":"(1+2)*-3"}`  
  output: `-9`
- **Example 3** - input: `{"expr":"7 / (3 - 3)"}`  
  output: `"ERROR"`

## Signature

```signature
evaluate(expr: string) -> int | string
```

## Tests

```json tests
{"function":"evaluate","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"expr":"1 + 2 * 3"},"expected":7},
{"name":"example-2","tags":["visible"],"args":{"expr":"(1+2)*-3"},"expected":-9},
{"name":"example-3","tags":["visible"],"args":{"expr":"7 / (3 - 3)"},"expected":"ERROR"},
{"name":"edge-empty","tags":["edge"],"args":{"expr":""},"expected":"ERROR"},
{"name":"edge-spaces-only","tags":["edge"],"args":{"expr":"   "},"expected":"ERROR"},
{"name":"edge-double-minus","tags":["edge"],"args":{"expr":"--3"},"expected":3},
{"name":"edge-unary-plus","tags":["edge"],"args":{"expr":"+3"},"expected":"ERROR"},
{"name":"hidden-trunc-neg","tags":["hidden"],"args":{"expr":"-7/2"},"expected":-3},
{"name":"hidden-trunc-neg-both","tags":["hidden"],"args":{"expr":"-7/-2"},"expected":3},
{"name":"hidden-left-assoc","tags":["hidden"],"args":{"expr":"20-5-3"},"expected":12},
{"name":"hidden-div-left-assoc","tags":["hidden"],"args":{"expr":"100/10/5"},"expected":2},
{"name":"hidden-adjacent-numbers","tags":["hidden"],"args":{"expr":"2 3"},"expected":"ERROR"},
{"name":"hidden-unbalanced-open","tags":["hidden"],"args":{"expr":"(1+2"},"expected":"ERROR"},
{"name":"hidden-unbalanced-close","tags":["hidden"],"args":{"expr":"1+2)"},"expected":"ERROR"},
{"name":"hidden-empty-parens","tags":["hidden"],"args":{"expr":"()"},"expected":"ERROR"},
{"name":"hidden-dangling-op","tags":["hidden"],"args":{"expr":"1+"},"expected":"ERROR"},
{"name":"hidden-bad-char","tags":["hidden"],"args":{"expr":"1 + a"},"expected":"ERROR"},
{"name":"hidden-nested-50","tags":["hidden"],"args":{"expr":"((((((((((((((((((((((((((((((((((((((((((((((((((7))))))))))))))))))))))))))))))))))))))))))))))))))"},"expected":7},
{"name":"hidden-leading-zeros","tags":["hidden"],"args":{"expr":"007 + 03"},"expected":10},
{"name":"hidden-unary-in-product","tags":["hidden"],"args":{"expr":"2*-3*-4"},"expected":24},
{"name":"hidden-power-not-supported","tags":["hidden"],"args":{"expr":"2**3"},"expected":"ERROR"},
{"name":"random-1","tags":["hidden"],"args":{"expr":"(16) * 3 - 9 + 0 * 18*16"},"expected":39},
{"name":"random-2","tags":["hidden"],"args":{"expr":"18/8 + -9/14"},"expected":2},
{"name":"random-3","tags":["hidden"],"args":{"expr":"(10)("},"expected":"ERROR"},
{"name":"random-4","tags":["hidden"],"args":{"expr":"(12)"},"expected":12}
]}
```

## Reference solution

```python reference
def solve(expr):
    DIGITS = "0123456789"
    n = len(expr)
    pos = 0

    def skip():
        nonlocal pos
        while pos < n and expr[pos] == " ":
            pos += 1

    def primary():
        nonlocal pos
        skip()
        if pos < n and expr[pos] == "(":
            pos += 1
            v = additive()
            skip()
            if pos >= n or expr[pos] != ")":
                raise ValueError("expected )")
            pos += 1
            return v
        start = pos
        while pos < n and expr[pos] in DIGITS:
            pos += 1
        if start == pos:
            raise ValueError("expected number")
        return int(expr[start:pos])

    def unary():
        nonlocal pos
        neg = False
        skip()
        while pos < n and expr[pos] == "-":
            neg = not neg
            pos += 1
            skip()
        v = primary()
        return -v if neg else v

    def term():
        nonlocal pos
        v = unary()
        while True:
            skip()
            if pos < n and expr[pos] in "*/":
                op = expr[pos]
                pos += 1
                r = unary()
                if op == "*":
                    v *= r
                else:
                    if r == 0:
                        raise ValueError("division by zero")
                    q = abs(v) // abs(r)
                    v = q if (v < 0) == (r < 0) else -q
            else:
                return v

    def additive():
        nonlocal pos
        v = term()
        while True:
            skip()
            if pos < n and expr[pos] in "+-":
                op = expr[pos]
                pos += 1
                r = term()
                v = v + r if op == "+" else v - r
            else:
                return v

    try:
        v = additive()
        skip()
        if pos != n:
            raise ValueError("trailing input")
        return v
    except ValueError:
        return "ERROR"
```

## Interviewer notes

- **Target complexity:** O(n) time; O(depth) stack
- **Clarifying questions (answer verbatim):**
  - Q: Is `-(2+3)` valid?  
    A: Yes: unary minus applies to any primary.
  - Q: What about `1 - -1`?  
    A: Valid, equals 2.
- **Hint ladder:**
  - H0 (free): Write the grammar down before any code.
  - H1 (-5): expr := term (('+'|'-') term)*; term := unary (('*'|'/') unary)*; unary := '-' unary | primary; primary := INT | '(' expr ')'.
  - H2 (-10): One function per grammar rule (recursive descent) with a shared position cursor.
  - H3 (-20): Raise one internal error type and convert it to "ERROR" at the top. Remember to check that the whole input was consumed.
- **Follow-ups:**
  - Add `^` (right-associative) and unary plus.
  - Support variables and function calls.
  - Convert to an iterative shunting-yard version.
  - Report the error position.
- **Mistakes the tests are built to catch:**
  - Python/JS integer division on negatives (floors instead of truncating).
  - Accepting trailing garbage because the parse stopped early.
  - Using eval.
  - Making `-` right-associative.
