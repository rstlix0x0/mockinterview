---
id: lc-b21-validate-a-binary-search-tree
title: Validate a Binary Search Tree
type: live-coding
level: [junior, mid]
tags: [tree, bst, inorder]
time_minutes: 25
entry: validate_bst
kind: func
source: adapted
author: mockinterview
legacy_id: B21
---

# Validate a Binary Search Tree

## Statement

A binary tree is given in level-order with `null` for missing children (children of missing nodes are not listed). Return `true` if it is a valid **strict** binary search tree: for every node, all values in its left subtree are smaller and all values in its right subtree are larger (duplicates make it invalid). An empty tree is valid. The tree can be a chain 100000 nodes deep.

**Signature:** `validate_bst(tree: (int | null)[]) -> bool`

**Constraints:**
- 0 <= nodes <= 200000

**Examples:**

- **Example 1** - input: `{"tree":[2,1,3]}`  
  output: `true`
- **Example 2** - input: `{"tree":[5,1,4,null,null,3,6]}`  
  output: `false`

## Signature

```signature
validate_bst(tree: int?[]) -> bool
```

## Tests

```json tests
{"function":"validate_bst","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"tree":[2,1,3]},"expected":true},
{"name":"example-2","tags":["visible"],"args":{"tree":[5,1,4,null,null,3,6]},"expected":false},
{"name":"edge-empty","tags":["edge"],"args":{"tree":[]},"expected":true},
{"name":"edge-single","tags":["edge"],"args":{"tree":[7]},"expected":true},
{"name":"edge-duplicate-child","tags":["edge"],"args":{"tree":[2,2]},"expected":false},
{"name":"hidden-grandchild-violates-root","tags":["hidden"],"args":{"tree":[10,5,15,null,null,6,20]},"expected":false},
{"name":"hidden-right-chain","tags":["hidden"],"args":{"tree":[1,null,2,null,3]},"expected":true},
{"name":"random-1","tags":["hidden"],"args":{"tree":[19,2,32,1,7,20,null,0,null,null,16,null,null,null,null,11]},"expected":true},
{"name":"random-2","tags":["hidden"],"args":{"tree":[4,null,7,null,26,null,37,35]},"expected":true},
{"name":"random-3","tags":["hidden"],"args":{"tree":[14,6,20,2,null,null,32,0]},"expected":true},
{"name":"random-4","tags":["hidden"],"args":{"tree":[0,null,28,10]},"expected":true}
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
    if not tree:
        return True
    prev, stack, node = None, [], 0
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = left.get(node)
        node = stack.pop()
        if prev is not None and tree[node] <= prev:
            return False
        prev = tree[node]
        node = right.get(node)
    return True
```

## Interviewer notes

- **Target complexity:** O(n) time, O(h) space
- **Clarifying questions (answer verbatim):**
  - Q: Are duplicates allowed?  
    A: No.
- **Hint ladder:**
  - H0 (free): Checking only parent vs child is not enough. Why?
  - H1 (-5): A grandchild must respect every ancestor.
  - H2 (-10): Pass (low, high) bounds down, or use in-order traversal.
  - H3 (-20): In-order of a valid BST is strictly increasing: keep the previous value.
- **Follow-ups:**
  - Recover a BST with two swapped nodes.
  - k-th smallest element.
- **Mistakes the tests are built to catch:**
  - Comparing each node only with its direct children.
  - Using <= vs < incorrectly (duplicates).
  - Recursion depth on the chain.
