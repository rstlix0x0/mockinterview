---
id: lc-fx-counter
title: Mini Counter (fixture)
type: live-coding
level: [senior]
tags: [design]
time_minutes: 10
languages: [python]
entry: MiniCounter
kind: ops
runs_code: true
source: original
author: tests
---
# Mini Counter (fixture)

## Statement

Design `MiniCounter` with `add(x)` and `total()`.

## Stub

```python
class MiniCounter:
    def __init__(self):
        pass

    def add(self, x):
        pass

    def total(self):
        pass
```

## Signature

```signature
MiniCounter()
add(x: int) -> void
total() -> int
```

## Tests

```json tests
{"function":"MiniCounter","kind":"ops","compare":"exact","fuzz":3,"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["MiniCounter",[]],["add",[1]],["add",[2]],["total",[]]]}},
{"name":"edge-empty","tags":["edge"],"args":{"calls":[["MiniCounter",[]],["total",[]]]}},
{"name":"hidden-negative","tags":["hidden"],"args":{"calls":[["MiniCounter",[]],["add",[-4]],["total",[]]]}}
]}
```

## Oracle

```python oracle
class MiniCounter:
    def __init__(self):
        self.t = 0

    def add(self, x):
        self.t += x

    def total(self):
        return self.t

def gen_random(seed):
    rnd = random.Random(seed)
    calls = [["MiniCounter", []]]
    for _ in range(rnd.randint(1, 8)):
        calls.append(["add", [rnd.randint(-5, 5)]] if rnd.random() < 0.6 else ["total", []])
    return {"calls": calls}
```

## Interviewer notes

- **Hint ladder:**
  - H0 (free): What state do you keep?
  - H1 (-5): One integer is enough.
  - H2 (-10): Add into it.
  - H3 (-20): total returns it.
