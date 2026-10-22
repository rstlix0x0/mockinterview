---
id: lc-fx-counter
title: Mini Counter (fixture)
type: live-coding
level: [senior]
tags: [design]
time_minutes: 10
entry: MiniCounter
kind: ops
source: original
author: tests
---
# Mini Counter (fixture)

## Statement

Design `MiniCounter` with `add(x)` and `total()`.

## Signature

```signature
MiniCounter()
add(x: int) -> void
total() -> int
```

## Tests

```json tests
{"function":"MiniCounter","kind":"ops","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["MiniCounter",[]],["add",[1]],["add",[2]],["total",[]]]},"expected":[null,null,null,3]},
{"name":"edge-empty","tags":["edge"],"args":{"calls":[["MiniCounter",[]],["total",[]]]},"expected":[null,0]},
{"name":"hidden-negative","tags":["hidden"],"args":{"calls":[["MiniCounter",[]],["add",[-4]],["total",[]]]},"expected":[null,null,-4]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["MiniCounter",[]],["total",[]],["total",[]],["total",[]],["total",[]],["total",[]]]},"expected":[null,0,0,0,0,0]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["MiniCounter",[]],["add",[-4]],["add",[1]],["total",[]],["add",[-3]],["add",[-1]],["add",[-1]]]},"expected":[null,null,null,-3,null,null,null]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["MiniCounter",[]],["add",[4]],["add",[0]],["add",[-1]],["total",[]],["total",[]],["add",[4]],["add",[0]]]},"expected":[null,null,null,null,3,3,null,null]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["MiniCounter",[]],["add",[-3]],["add",[-1]],["add",[-1]],["add",[1]]]},"expected":[null,null,null,null,null]}
]}
```

## Reference solution

```python reference
class MiniCounter:
    def __init__(self):
        self.t = 0

    def add(self, x):
        self.t += x

    def total(self):
        return self.t
```

## Interviewer notes

- **Hint ladder:**
  - H0 (free): What state do you keep?
  - H1 (-5): One integer is enough.
  - H2 (-10): Add into it.
  - H3 (-20): total returns it.
