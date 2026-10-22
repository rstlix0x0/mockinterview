---
id: lc-a16-stack-with-minimum
title: Stack With Minimum
type: live-coding
level: [junior]
tags: [design, stack]
time_minutes: 15
entry: MinStack
kind: ops
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

## Signature

```signature
MinStack()
push(x: int) -> void
pop() -> int
top() -> int
get_min() -> int
```

## Tests

```json tests
{"function":"MinStack","kind":"ops","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["MinStack",[]],["push",[3]],["push",[1]],["push",[2]],["get_min",[]],["pop",[]],["get_min",[]],["top",[]]]},"expected":[null,null,null,null,1,2,1,1]},
{"name":"edge-duplicates-of-min","tags":["edge"],"args":{"calls":[["MinStack",[]],["push",[1]],["push",[1]],["pop",[]],["get_min",[]]]},"expected":[null,null,null,1,1]},
{"name":"hidden-min-restored","tags":["hidden"],"args":{"calls":[["MinStack",[]],["push",[5]],["push",[2]],["push",[9]],["pop",[]],["pop",[]],["get_min",[]]]},"expected":[null,null,null,null,9,2,5]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["MinStack",[]],["push",[-1]],["get_min",[]],["top",[]],["top",[]],["top",[]],["pop",[]],["push",[3]],["push",[-4]],["top",[]],["pop",[]],["top",[]],["get_min",[]],["push",[-2]],["get_min",[]],["push",[4]],["push",[3]],["pop",[]],["top",[]],["top",[]],["push",[1]],["top",[]],["get_min",[]]]},"expected":[null,null,-1,-1,-1,-1,-1,null,null,-4,-4,3,3,null,-2,null,null,3,4,4,null,1,-2]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["MinStack",[]],["push",[-4]],["push",[1]],["pop",[]],["pop",[]],["push",[-1]],["push",[-1]],["push",[0]],["pop",[]],["get_min",[]],["push",[2]],["top",[]],["pop",[]],["pop",[]],["push",[2]],["push",[4]]]},"expected":[null,null,null,1,-4,null,null,null,0,-1,null,2,2,-1,null,null]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["MinStack",[]],["push",[4]],["push",[0]],["push",[-1]],["top",[]],["top",[]],["push",[4]],["push",[0]],["pop",[]],["push",[-1]],["push",[5]],["push",[-2]],["push",[4]],["push",[3]],["push",[-5]],["push",[-1]],["push",[-4]]]},"expected":[null,null,null,null,-1,-1,null,null,0,null,null,null,null,null,null,null,null]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["MinStack",[]],["push",[-3]],["push",[-1]],["push",[-1]],["pop",[]],["push",[-4]],["push",[5]],["get_min",[]],["get_min",[]],["get_min",[]],["push",[4]]]},"expected":[null,null,null,null,-1,null,null,-4,-4,-4,null]}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(1) per operation, O(n) space
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
