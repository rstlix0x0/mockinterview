---
id: lc-a16-stack-with-minimum
title: Stack With Minimum
type: live-coding
level: [junior]
tags: [design, stack]
time_minutes: 15
languages: [python]
entry: MinStack
kind: ops
runs_code: true
source: adapted
author: mockinterview
legacy_id: A16
---

# Stack With Minimum

## Statement

Design `MinStack`: `push(x)`, `pop()` (removes and returns the top), `top()` (returns it without removing) and `get_min()` (the smallest value currently on the stack). Every operation must be O(1). `pop`, `top` and `get_min` are only called on a non-empty stack.

**Signature:** `class MinStack { push(x: int); pop() -> int; top() -> int; get_min() -> int }`

**Constraints:**
- up to 300000 operations

**Examples:**

- **Example 1** - calls: `MinStack(); push(3); push(1); push(2); get_min(); pop(); get_min(); top()`  
  returns: `[null,null,null,null,1,2,1,1]`

---

## Stub

```python
class MinStack:
    def __init__(self):
        """No constructor arguments."""
        pass

    def push(self, x):
        """push(x: int)"""
        raise NotImplementedError

    def pop(self):
        """pop() -> int"""
        raise NotImplementedError

    def top(self):
        """top() -> int"""
        raise NotImplementedError

    def get_min(self):
        """get_min() -> int"""
        raise NotImplementedError
```

## Tests

```json tests
{"function":"MinStack","kind":"ops","compare":"exact","fuzz":25,"perf":{"sizes":[50000,150000,300000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["MinStack",[]],["push",[3]],["push",[1]],["push",[2]],["get_min",[]],["pop",[]],["get_min",[]],["top",[]]]}},
{"name":"edge-duplicates-of-min","tags":["edge"],"args":{"calls":[["MinStack",[]],["push",[1]],["push",[1]],["pop",[]],["get_min",[]]]}},
{"name":"hidden-min-restored","tags":["hidden"],"args":{"calls":[["MinStack",[]],["push",[5]],["push",[2]],["push",[9]],["pop",[]],["pop",[]],["get_min",[]]]}}
]}
```

## Oracle

```python oracle
class MinStack:
    def __init__(self):
        self.items, self.mins = [], []

    def push(self, x):
        self.items.append(x)
        self.mins.append(x if not self.mins else min(x, self.mins[-1]))

    def pop(self):
        self.mins.pop()
        return self.items.pop()

    def top(self):
        return self.items[-1]

    def get_min(self):
        return self.mins[-1]

def gen_random(seed):
    rnd = random.Random(seed)
    calls, size = [["MinStack", []]], 0
    for _ in range(rnd.randint(4, 25)):
        c = rnd.random()
        if size == 0 or c < 0.45:
            calls.append(["push", [rnd.randint(-5, 5)]]); size += 1
        elif c < 0.65:
            calls.append(["pop", []]); size -= 1
        elif c < 0.85:
            calls.append(["top", []])
        else:
            calls.append(["get_min", []])
    return {"calls": calls}

def gen_perf(n):
    rnd = random.Random(216)
    calls, size = [["MinStack", []]], 0
    for _ in range(n):
        c = rnd.random()
        if size == 0 or c < 0.5:
            calls.append(["push", [rnd.randint(-10**9, 10**9)]]); size += 1
        elif c < 0.75:
            calls.append(["pop", []]); size -= 1
        elif c < 0.9:
            calls.append(["top", []])
        else:
            calls.append(["get_min", []])
    return {"calls": calls}
```

## Interviewer notes

- **Target complexity:** O(1) per operation, O(n) space
- **Scaling check:** sizes [50000, 150000, 300000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Is `pop` expected to return the value?  
    A: Yes.
- **Hint ladder:**
  - H0 (free): Recomputing the minimum on every call is O(n). What can you remember instead?
  - H1 (-5): The minimum as of each stack height.
  - H2 (-10): A second stack storing the running minimum.
  - H3 (-20): Push to both; pop from both.
- **Follow-ups:**
  - Use O(1) extra space with an encoded difference trick.
  - Add `get_max()`.
- **Mistakes the tests are built to catch:**
  - Updating one global minimum and never restoring it after pop.
  - Storing the min only when it changes but popping duplicates incorrectly.

---
