---
id: lc-c09-spreadsheet-evaluator
title: Spreadsheet Formula Evaluator
type: live-coding
level: [senior, staff]
tags: [graph, dfs, cycle-detection, memoization]
time_minutes: 45
languages: [python]
entry: evaluate_sheet
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: C9
---

# Spreadsheet Formula Evaluator

## Statement

`cells` maps a cell name (a capital letter followed by digits, like `B12`) to its raw text. Compute the value of every cell.

- A raw text that is an integer (`"42"`, `"-7"`) is that number.
- A text starting with `=` is a formula: one or more operands joined by `+` or `-`, with no spaces and no unary signs. An operand is an integer literal (non-negative) or a cell name. Example: `=A1+10-B2`.
- A reference to a cell that is not in `cells` counts as 0.
- Any other text, or a formula that does not match that shape (`=`, `=A1+`, `= 1`, `=1++2`), has the value `"#ERR"`.
- A cell that is part of a reference cycle, or depends (directly or indirectly) on one, has the value `"#CYCLE"`.
- If a formula has both kinds of bad operands, `"#CYCLE"` wins over `"#ERR"`.

Return a map with the same keys as `cells`. Chains can be 100000 cells long, so recursion depth matters.

**Signature:** `evaluate_sheet(cells: {string: string}) -> {string: int | "#ERR" | "#CYCLE"}`

**Constraints:**
- 0 <= len(cells) <= 100000
- dependency chains up to 100000 long

**Examples:**

- **Example 1** - input: `{"cells":{"A1":"5","A2":"=A1+3","A3":"=A2-A1-10"}}`  
  output: `{"A1":5,"A2":8,"A3":-7}`
- **Example 2** - input: `{"cells":{"A1":"=B1","B1":"=A1","C1":"=A1+1"}}`  
  output: `{"A1":"#CYCLE","B1":"#CYCLE","C1":"#CYCLE"}`

## Stub

```python
def evaluate_sheet(cells):
    """evaluate_sheet(cells: {string: string}) -> {string: int | '#ERR' | '#CYCLE'}"""
    raise NotImplementedError
```

## Signature

```signature
evaluate_sheet(cells: {string: string}) -> {string: int | string}
```

## Tests

```json tests
{"function":"evaluate_sheet","kind":"func","compare":"exact","fuzz":60,"perf":{"sizes":[10000,50000,100000],"limit_ms":5000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"cells":{"A1":"5","A2":"=A1+3","A3":"=A2-A1-10"}}},
{"name":"example-2","tags":["visible"],"args":{"cells":{"A1":"=B1","B1":"=A1","C1":"=A1+1"}}},
{"name":"edge-empty","tags":["edge"],"args":{"cells":{}}},
{"name":"edge-self-reference","tags":["edge"],"args":{"cells":{"A1":"=A1+1"}}},
{"name":"edge-missing-ref","tags":["edge"],"args":{"cells":{"A1":"=Z9+4"}}},
{"name":"hidden-cycle-beats-err","tags":["hidden"],"args":{"cells":{"A1":"=B1+C1","B1":"oops","C1":"=A1"}}},
{"name":"hidden-err-propagates","tags":["hidden"],"args":{"cells":{"A1":"x","A2":"=A1+1","A3":"=A2"}}},
{"name":"hidden-diamond","tags":["hidden"],"args":{"cells":{"A1":"2","B1":"=A1+A1","C1":"=A1-1","D1":"=B1+C1"}}},
{"name":"hidden-feeds-cycle-but-not-in-it","tags":["hidden"],"args":{"cells":{"A1":"=B1","B1":"=A1","C1":"5","D1":"=C1+1"}}}
]}
```

## Oracle

```python oracle
def solve(cells):
    CELL_RE = re.compile(r"(?:[A-Z][0-9]+|[0-9]+)(?:[+-](?:[A-Z][0-9]+|[0-9]+))*")
    TOK_RE = re.compile(r"([+-])([A-Z][0-9]+|[0-9]+)")

    def parse(raw):
        if raw.startswith("="):
            body = raw[1:]
            if not CELL_RE.fullmatch(body):
                return None
            return TOK_RE.findall("+" + body)
        m = re.fullmatch(r"(-?)([0-9]+)", raw)
        if m:
            return [(m.group(1) or "+", m.group(2))]
        return None

    state, value, parsed = {}, {}, {}

    def operand(tok):
        if tok[0] in "0123456789":
            return int(tok)
        if tok not in cells:
            return 0
        return value.get(tok, "#CYCLE")

    for root in cells:
        if root in value:
            continue
        stack = [root]
        while stack:
            name = stack[-1]
            if name in value:
                stack.pop()
                continue
            if name not in state:
                state[name] = "visiting"
                parsed[name] = parse(cells[name])
            terms = parsed[name]
            if terms is None:
                value[name] = "#ERR"
                stack.pop()
                continue
            pending = [t for _, t in terms if t in cells and t not in state]
            if pending:
                stack.append(pending[0])
                continue
            vals = [(sign, operand(t)) for sign, t in terms]
            if any(v == "#CYCLE" for _, v in vals):
                value[name] = "#CYCLE"
            elif any(v == "#ERR" for _, v in vals):
                value[name] = "#ERR"
            else:
                value[name] = sum(v if s == "+" else -v for s, v in vals)
            stack.pop()
    return {k: value[k] for k in cells}

def gen_random(seed):
    rnd = random.Random(seed)
    names = ["A1", "A2", "B1", "B2", "C1"]
    cells = {}
    for nm in rnd.sample(names, rnd.randint(1, 5)):
        r = rnd.random()
        if r < 0.25:
            cells[nm] = str(rnd.randint(-9, 99))
        elif r < 0.9:
            cells[nm] = "=" + "".join((rnd.choice("+-") if i else "") + rnd.choice(names + ["7", "12", "Z9"]) for i in range(rnd.randint(1, 3)))
        else:
            cells[nm] = rnd.choice(["abc", "=", "=A1+", "= 1", "=1++2", "1.5"])
    return {"cells": cells}

def gen_perf(n):
    cells = {"A1": "1"}
    for i in range(2, n + 1):
        cells["A%d" % i] = "=A%d+1" % (i - 1)
    return {"cells": dict(reversed(list(cells.items())))}
```

## Interviewer notes

- **Target complexity:** O(cells + references)
- **Scaling check:** sizes [10000, 50000, 100000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: Are formulas case sensitive?  
    A: Yes. Only capital letters are cell names.
  - Q: Is `=5` valid?  
    A: Yes, a single operand.
- **Hint ladder:**
  - H0 (free): What graph do the references form?
  - H1 (-5): Evaluate with a depth-first search that memoises results.
  - H2 (-10): Mark nodes as 'in progress'. Reaching an in-progress node means a cycle.
  - H3 (-20): With a 100000-long chain a recursive DFS overflows the stack in most languages: use an explicit stack.
- **Follow-ups:**
  - The user edits one cell: recompute only what depends on it (reverse edges, topological order).
  - Add ranges `SUM(A1:A9)`.
  - Detect and print one cycle path.
- **Mistakes the tests are built to catch:**
  - Recursion depth overflow on the long chain.
  - Forgetting that a cell depending on a cycle is also #CYCLE.
  - Letting an unvisited-but-memoised value shadow the in-progress marker.
  - Treating missing cells as errors.
