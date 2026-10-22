---
id: lc-b20-reverse-k-groups
title: Reverse Nodes in k-Groups
type: live-coding
level: [mid, senior]
tags: [linked-list, pointers]
time_minutes: 35
entry: reverse_k_group
kind: func
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

## Signature

```signature
reverse_k_group(values: int[], k: int) -> int[]
```

## Tests

```json tests
{"function":"reverse_k_group","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"values":[1,2,3,4,5],"k":2},"expected":[2,1,4,3,5]},
{"name":"example-2","tags":["visible"],"args":{"values":[1,2,3,4,5],"k":3},"expected":[3,2,1,4,5]},
{"name":"edge-empty","tags":["edge"],"args":{"values":[],"k":3},"expected":[]},
{"name":"edge-k-one","tags":["edge"],"args":{"values":[1,2,3],"k":1},"expected":[1,2,3]},
{"name":"edge-k-larger-than-list","tags":["edge"],"args":{"values":[1,2],"k":5},"expected":[1,2]},
{"name":"hidden-exact-multiple","tags":["hidden"],"args":{"values":[1,2,3,4],"k":2},"expected":[2,1,4,3]},
{"name":"random-1","tags":["hidden"],"args":{"values":[97,38,4,88,15,90,3,83,98],"k":1},"expected":[97,38,4,88,15,90,3,83,98]},
{"name":"random-2","tags":["hidden"],"args":{"values":[8,15,53,74,52],"k":1},"expected":[8,15,53,74,52]},
{"name":"random-3","tags":["hidden"],"args":{"values":[29,13,76,4,89,40],"k":1},"expected":[29,13,76,4,89,40]},
{"name":"random-4","tags":["hidden"],"args":{"values":[0,53,21],"k":4},"expected":[0,53,21]}
]}
```

## Reference solution

```python reference
def solve(values, k):
    out = []
    i = 0
    while i < len(values):
        group = values[i:i + k]
        out.extend(reversed(group) if len(group) == k else group)
        i += k
    return out
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) extra space
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
