---
id: lc-b20-reverse-k-groups
title: Reverse Nodes in k-Groups
type: live-coding
level: [mid, senior]
tags: [linked-list, pointers]
time_minutes: 35
languages: [python]
entry: reverse_k_group
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B20
---

# Reverse Nodes in k-Groups

## Statement

Reverse a linked list `k` nodes at a time and return its values. If fewer than `k` nodes remain at the end, leave them in their original order. The list is given as an array `values`; for real practice, build the nodes yourself and relink them (do not just reverse array slices), using O(1) extra space.

**Signature:** `reverse_k_group(values: int[], k: int) -> int[]`

**Constraints:**
- 0 <= len(values) <= 500000
- 1 <= k <= 500000

**Examples:**

- **Example 1** - input: `{"values":[1,2,3,4,5],"k":2}`  
  output: `[2,1,4,3,5]`
- **Example 2** - input: `{"values":[1,2,3,4,5],"k":3}`  
  output: `[3,2,1,4,5]`

## Stub

```python
def reverse_k_group(values, k):
    """reverse_k_group(values: int[], k: int) -> int[]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"reverse_k_group","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[50000,200000,500000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"values":[1,2,3,4,5],"k":2}},
{"name":"example-2","tags":["visible"],"args":{"values":[1,2,3,4,5],"k":3}},
{"name":"edge-empty","tags":["edge"],"args":{"values":[],"k":3}},
{"name":"edge-k-one","tags":["edge"],"args":{"values":[1,2,3],"k":1}},
{"name":"edge-k-larger-than-list","tags":["edge"],"args":{"values":[1,2],"k":5}},
{"name":"hidden-exact-multiple","tags":["hidden"],"args":{"values":[1,2,3,4],"k":2}}
]}
```

## Oracle

```python oracle
def solve(values, k):
    out = []
    i = 0
    while i < len(values):
        group = values[i:i + k]
        out.extend(reversed(group) if len(group) == k else group)
        i += k
    return out

def gen_random(seed):
    rnd = random.Random(seed)
    return {"values": [rnd.randint(0, 99) for _ in range(rnd.randint(0, 12))], "k": rnd.randint(1, 5)}

def gen_perf(n):
    rnd = random.Random(220)
    return {"values": [rnd.randint(0, 10**6) for _ in range(n)], "k": 3}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) extra space
- **Scaling check:** sizes [50000, 200000, 500000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Do node values change?  
    A: No. Only the links are rearranged.
- **Hint ladder:**
  - H0 (free): How do you reverse a whole list?
  - H1 (-5): Reverse the first k nodes, remember their new tail.
  - H2 (-10): Check that k nodes exist before reversing a group.
  - H3 (-20): Connect the previous group's tail to the new group's head with a dummy node.
- **Follow-ups:**
  - Reverse only between positions m and n.
  - Recursive version: what is the stack depth?
- **Mistakes the tests are built to catch:**
  - Reversing a short final group.
  - Losing the connection between groups.
  - Slicing arrays (fine for tests, not the exercise).
