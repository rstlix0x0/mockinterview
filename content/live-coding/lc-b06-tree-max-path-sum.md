---
id: lc-b06-tree-max-path-sum
title: Binary Tree Maximum Path Sum
type: live-coding
level: [mid, senior]
tags: [tree, dfs, dp-on-trees]
time_minutes: 35
entry: max_path_sum
kind: func
source: adapted
author: mockinterview
legacy_id: B6
---

# Binary Tree Maximum Path Sum

## Statement

A binary tree is given in level-order as a list where `null` marks a missing child (the usual LeetCode serialization: children of missing nodes are not listed). A path is any sequence of connected nodes that goes up and then down at most once; it does not need to pass through the root and must contain at least one node. Return the maximum sum of node values over all paths. Node values can be negative.

**Signature:** `max_path_sum(tree: (int | null)[]) -> int`

**Constraints:**
- 1 <= nodes <= 100000
- -1000 <= value <= 1000
- the tree can be a chain 100000 nodes deep

**Examples:**

- **Example 1** - input: `{"tree":[1,2,3]}`  
  output: `6`
- **Example 2** - input: `{"tree":[-10,9,20,null,null,15,7]}`  
  output: `42`

## Signature

```signature
max_path_sum(tree: int?[]) -> int
```

## Tests

```json tests
{"function":"max_path_sum","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"tree":[1,2,3]},"expected":6},
{"name":"example-2","tags":["visible"],"args":{"tree":[-10,9,20,null,null,15,7]},"expected":42},
{"name":"edge-single-negative","tags":["edge"],"args":{"tree":[-3]},"expected":-3},
{"name":"edge-all-negative","tags":["edge"],"args":{"tree":[-2,-1,-3]},"expected":-1},
{"name":"hidden-path-skips-root","tags":["hidden"],"args":{"tree":[-5,4,4,3,null,null,3]},"expected":9},
{"name":"hidden-left-chain","tags":["hidden"],"args":{"tree":[1,2,null,3,null,4]},"expected":10},
{"name":"random-1","tags":["hidden"],"args":{"tree":[-1,null,-10,10,null,6,-7,8,-10,null,-3,null,8,6]},"expected":32},
{"name":"random-2","tags":["hidden"],"args":{"tree":[-8,null,8,-8,-6,-2,-1]},"expected":8},
{"name":"random-3","tags":["hidden"],"args":{"tree":[-3,-9,null,6,null,null,1,-6,null,2,null,null,10]},"expected":13},
{"name":"random-4","tags":["hidden"],"args":{"tree":[-10,3,4,null,2]},"expected":5}
]}
```

## Reference solution

```python reference
from collections import deque

def solve(tree):
    left, right = {}, {}
    q = deque([0])
    i = 1
    while q and i < len(tree):
        u = q.popleft()
        if i < len(tree) and tree[i] is not None:
            left[u] = i
            q.append(i)
        i += 1
        if i < len(tree) and tree[i] is not None:
            right[u] = i
            q.append(i)
        i += 1
    order, stack = [], [0]
    while stack:
        u = stack.pop()
        order.append(u)
        for ch in (left.get(u), right.get(u)):
            if ch is not None:
                stack.append(ch)
    gain, best = {}, tree[0]
    for u in reversed(order):
        l = max(0, gain[left[u]]) if u in left else 0
        r = max(0, gain[right[u]]) if u in right else 0
        best = max(best, tree[u] + l + r)
        gain[u] = tree[u] + max(l, r)
    return best
```

## Interviewer notes

- **Target complexity:** O(n) time, O(h) extra space (O(n) for the chain)
- **Clarifying questions (answer verbatim):**
  - Q: Must the path include the root?  
    A: No.
  - Q: May a path be a single node?  
    A: Yes.
- **Hint ladder:**
  - H0 (free): For each node, what is the best path that bends at that node?
  - H1 (-5): You need the best downward gain from each child.
  - H2 (-10): Post-order: gain(node) = value + max(0, best child gain). The bent path adds both child gains.
  - H3 (-20): Update a global maximum at every node; return only the one-sided gain to the parent.
- **Follow-ups:**
  - Return the path nodes.
  - Handle the 100000-deep chain without recursion.
- **Mistakes the tests are built to catch:**
  - Returning the bent path to the parent.
  - Not clamping negative child gains to zero.
  - Initialising the answer to 0 (wrong when all values are negative).
  - Stack overflow on the deep chain.
