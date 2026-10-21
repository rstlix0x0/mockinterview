---
id: lc-c06-arithmetic-expression-evaluator
title: Arithmetic Expression Evaluator
type: live-coding
level: [mid, senior]
tags: [parsing, recursion, grammar]
time_minutes: 40
languages: [python]
entry: evaluate
kind: func
runs_code: true
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

## Stub

```python
def evaluate(expr):
    """evaluate(expr: string) -> int | 'ERROR'"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"evaluate","kind":"func","compare":"exact","fuzz":80,"perf":{"sizes":[20000,100000,200000],"limit_ms":5000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"expr":"1 + 2 * 3"}},
{"name":"example-2","tags":["visible"],"args":{"expr":"(1+2)*-3"}},
{"name":"example-3","tags":["visible"],"args":{"expr":"7 / (3 - 3)"}},
{"name":"edge-empty","tags":["edge"],"args":{"expr":""}},
{"name":"edge-spaces-only","tags":["edge"],"args":{"expr":"   "}},
{"name":"edge-double-minus","tags":["edge"],"args":{"expr":"--3"}},
{"name":"edge-unary-plus","tags":["edge"],"args":{"expr":"+3"}},
{"name":"hidden-trunc-neg","tags":["hidden"],"args":{"expr":"-7/2"}},
{"name":"hidden-trunc-neg-both","tags":["hidden"],"args":{"expr":"-7/-2"}},
{"name":"hidden-left-assoc","tags":["hidden"],"args":{"expr":"20-5-3"}},
{"name":"hidden-div-left-assoc","tags":["hidden"],"args":{"expr":"100/10/5"}},
{"name":"hidden-adjacent-numbers","tags":["hidden"],"args":{"expr":"2 3"}},
{"name":"hidden-unbalanced-open","tags":["hidden"],"args":{"expr":"(1+2"}},
{"name":"hidden-unbalanced-close","tags":["hidden"],"args":{"expr":"1+2)"}},
{"name":"hidden-empty-parens","tags":["hidden"],"args":{"expr":"()"}},
{"name":"hidden-dangling-op","tags":["hidden"],"args":{"expr":"1+"}},
{"name":"hidden-bad-char","tags":["hidden"],"args":{"expr":"1 + a"}},
{"name":"hidden-nested-50","tags":["hidden"],"args":{"expr":"((((((((((((((((((((((((((((((((((((((((((((((((((7))))))))))))))))))))))))))))))))))))))))))))))))))"}},
{"name":"hidden-leading-zeros","tags":["hidden"],"args":{"expr":"007 + 03"}},
{"name":"hidden-unary-in-product","tags":["hidden"],"args":{"expr":"2*-3*-4"}},
{"name":"hidden-power-not-supported","tags":["hidden"],"args":{"expr":"2**3"}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)

    def gen(d):
        if d == 0 or rnd.random() < 0.3:
            return str(rnd.randint(0, 20))
        c = rnd.random()
        if c < 0.15:
            return "(" + gen(d - 1) + ")"
        if c < 0.25:
            return "-" + gen(d - 1)
        return gen(d - 1) + rnd.choice([" + ", "-", " * ", "/", "*", " - "]) + gen(d - 1)

    e = gen(4)
    if rnd.random() < 0.3 and e:
        i = rnd.randrange(len(e))
        e = rnd.choice([e[:i] + e[i + 1:], e[:i] + rnd.choice("+*/()x ") + e[i:], e + rnd.choice("+)(")])
    return {"expr": e}

def gen_perf(n):
    rnd = random.Random(106)
    parts = [str(rnd.randint(1, 9))]
    for _ in range(n):
        parts.append(rnd.choice(["+", "-", "*1+", "/1-"]))
        parts.append(str(rnd.randint(1, 9)))
    return {"expr": " ".join(parts)}
```

## Interviewer notes

- **Target complexity:** O(n) time; O(depth) stack
- **Scaling check:** sizes [20000, 100000, 200000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
