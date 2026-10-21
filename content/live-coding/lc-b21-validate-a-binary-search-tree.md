---
id: lc-b21-validate-a-binary-search-tree
title: Validate a Binary Search Tree
type: live-coding
level: [junior, mid]
tags: [tree, bst, inorder]
time_minutes: 25
languages: [python]
entry: validate_bst
kind: func
runs_code: true
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

## Stub

```python
def validate_bst(tree):
    """validate_bst(tree: (int | null)[]) -> bool"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"validate_bst","kind":"func","compare":"exact","fuzz":40,"perf":{"sizes":[10000,50000,100000],"limit_ms":4000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"tree":[2,1,3]}},
{"name":"example-2","tags":["visible"],"args":{"tree":[5,1,4,null,null,3,6]}},
{"name":"edge-empty","tags":["edge"],"args":{"tree":[]}},
{"name":"edge-single","tags":["edge"],"args":{"tree":[7]}},
{"name":"edge-duplicate-child","tags":["edge"],"args":{"tree":[2,2]}},
{"name":"hidden-grandchild-violates-root","tags":["hidden"],"args":{"tree":[10,5,15,null,null,6,20]}},
{"name":"hidden-right-chain","tags":["hidden"],"args":{"tree":[1,null,2,null,3]}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    root, kids = None, {}
    for v in rnd.sample(range(40), rnd.randint(0, 9)):
        if root is None:
            root = v
            continue
        cur = root
        while True:
            side = 0 if v < cur else 1
            if (cur, side) in kids:
                cur = kids[(cur, side)]
            else:
                kids[(cur, side)] = v
                break
    ser, q = [], deque([root])
    while q:
        node = q.popleft()
        if node is None:
            ser.append(None)
        else:
            ser.append(node)
            q.append(kids.get((node, 0)))
            q.append(kids.get((node, 1)))
    while ser and ser[-1] is None:
        ser.pop()
    if ser and rnd.random() < 0.5:
        j = rnd.randrange(len(ser))
        if ser[j] is not None:
            ser[j] = rnd.randint(0, 40)
    return {"tree": ser}

def gen_perf(n):
    tree = [0]
    for i in range(1, n):
        tree += [None, i]
    return {"tree": tree}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(h) space
- **Scaling check:** sizes [10000, 50000, 100000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
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
