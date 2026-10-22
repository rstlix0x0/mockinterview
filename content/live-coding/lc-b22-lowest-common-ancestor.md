---
id: lc-b22-lowest-common-ancestor
title: Lowest Common Ancestor of a Binary Tree
type: live-coding
level: [junior, mid]
tags: [tree, ancestors]
time_minutes: 30
entry: lowest_common_ancestor
kind: func
source: adapted
author: mockinterview
legacy_id: B22
---

# Lowest Common Ancestor of a Binary Tree

## Statement

A binary tree with **distinct** values is given in level-order with `null` for missing children. `p` and `q` are values present in the tree (they may be equal). Return the value of their lowest common ancestor: the deepest node that has both as descendants, where a node counts as a descendant of itself. The tree is not necessarily a search tree and can be a chain 100000 nodes deep.

**Signature:** `lowest_common_ancestor(tree: (int | null)[], p: int, q: int) -> int`

**Constraints:**
- 2 <= nodes <= 200000

**Examples:**

- **Example 1** - input: `{"tree":[3,5,1,6,2,0,8],"p":5,"q":1}`  
  output: `3`
- **Example 2** - input: `{"tree":[3,5,1,6,2,0,8],"p":5,"q":2}`  
  output: `5`

## Signature

```signature
lowest_common_ancestor(tree: int?[], p: int, q: int) -> int
```

## Tests

```json tests
{"function":"lowest_common_ancestor","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"tree":[3,5,1,6,2,0,8],"p":5,"q":1},"expected":3},
{"name":"example-2","tags":["visible"],"args":{"tree":[3,5,1,6,2,0,8],"p":5,"q":2},"expected":5},
{"name":"edge-same-node","tags":["edge"],"args":{"tree":[1,2,3],"p":2,"q":2},"expected":2},
{"name":"edge-root-is-lca","tags":["edge"],"args":{"tree":[1,2,3],"p":2,"q":3},"expected":1},
{"name":"hidden-deep","tags":["hidden"],"args":{"tree":[1,2,null,3,null,4],"p":4,"q":3},"expected":3},
{"name":"random-1","tags":["hidden"],"args":{"tree":[97,38,null,4],"p":4,"q":4},"expected":4},
{"name":"random-2","tags":["hidden"],"args":{"tree":[8,15,53,null,74,52,82,9],"p":9,"q":53},"expected":8},
{"name":"random-3","tags":["hidden"],"args":{"tree":[29,null,13,76,4,89,40,1,null,64],"p":89,"q":29},"expected":29},
{"name":"random-4","tags":["hidden"],"args":{"tree":[0,53,21,50,38],"p":0,"q":0},"expected":0}
]}
```

## Reference solution

```python reference
from collections import deque

def solve(tree, p, q):
    parent, left, right, value_at = {}, {}, {}, {}
    dq = deque([0])
    i = 1
    while dq and i < len(tree):
        u = dq.popleft()
        for side in (left, right):
            if i < len(tree) and tree[i] is not None:
                side[u] = i
                parent[i] = u
                dq.append(i)
            i += 1
    idx = {v: k for k, v in enumerate(tree) if v is not None}
    anc = set()
    x = idx[p]
    while True:
        anc.add(x)
        if x not in parent:
            break
        x = parent[x]
    y = idx[q]
    while y not in anc:
        y = parent[y]
    return tree[y]
```

## Interviewer notes

- **Target complexity:** O(n) time
- **Clarifying questions (answer verbatim):**
  - Q: Is the tree a BST?  
    A: No.
- **Hint ladder:**
  - H0 (free): Where can the two nodes be relative to a candidate ancestor?
  - H1 (-5): In different subtrees, or one is the candidate itself.
  - H2 (-10): Recursive: return the node if it is p or q, combine left and right results.
  - H3 (-20): Alternative: parent pointers and an ancestor set; mind the depth limit.
- **Follow-ups:**
  - The tree is a BST: O(h) without visiting everything.
  - Nodes are not guaranteed to exist.
- **Mistakes the tests are built to catch:**
  - Treating a node as not its own descendant.
  - Recursion depth on the chain.
