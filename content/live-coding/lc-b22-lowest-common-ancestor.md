---
id: lc-b22-lowest-common-ancestor
title: Lowest Common Ancestor of a Binary Tree
type: live-coding
level: [junior, mid]
tags: [tree, ancestors]
time_minutes: 30
languages: [python]
entry: lowest_common_ancestor
kind: func
runs_code: true
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

## Stub

```python
def lowest_common_ancestor(tree, p, q):
    """lowest_common_ancestor(tree: (int | null)[], p: int, q: int) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"lowest_common_ancestor","kind":"func","compare":"exact","fuzz":40,"perf":{"sizes":[10000,50000,100000],"limit_ms":4000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"tree":[3,5,1,6,2,0,8],"p":5,"q":1}},
{"name":"example-2","tags":["visible"],"args":{"tree":[3,5,1,6,2,0,8],"p":5,"q":2}},
{"name":"edge-same-node","tags":["edge"],"args":{"tree":[1,2,3],"p":2,"q":2}},
{"name":"edge-root-is-lca","tags":["edge"],"args":{"tree":[1,2,3],"p":2,"q":3}},
{"name":"hidden-deep","tags":["hidden"],"args":{"tree":[1,2,null,3,null,4],"p":4,"q":3}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    n = rnd.randint(2, 12)
    vals = rnd.sample(range(100), n)
    tree, dq, used = [vals[0]], deque([0]), 1
    while dq and used < n:
        dq.popleft()
        for _ in range(2):
            if used < n and rnd.random() < 0.75:
                tree.append(vals[used]); dq.append(len(tree) - 1); used += 1
            else:
                tree.append(None)
    while tree and tree[-1] is None:
        tree.pop()
    present = [v for v in tree if v is not None]
    return {"tree": tree, "p": rnd.choice(present), "q": rnd.choice(present)}

def gen_perf(n):
    tree = [0]
    for i in range(1, n):
        tree += [i, None]
    return {"tree": tree, "p": n - 1, "q": n // 2}
```

## Interviewer notes

- **Target complexity:** O(n) time
- **Scaling check:** sizes [10000, 50000, 100000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
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
