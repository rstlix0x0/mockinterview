---
id: lc-b25-connected-components
title: Connected Components
type: live-coding
level: [junior, mid]
tags: [graph, union-find]
time_minutes: 20
entry: count_components
kind: func
source: adapted
author: mockinterview
legacy_id: B25
---

# Connected Components

## Statement

An undirected graph has `n` nodes numbered `0..n-1` and a list of `edges`. Return the number of connected components. Self-loops and duplicate edges may occur.

**Signature:** `count_components(n: int, edges: int[][2]) -> int`

**Constraints:**
- 0 <= n <= 500000
- 0 <= len(edges) <= 500000

**Examples:**

- **Example 1** - input: `{"n":5,"edges":[[0,1],[1,2],[3,4]]}`  
  output: `2`
- **Example 2** - input: `{"n":4,"edges":[]}`  
  output: `4`

## Signature

```signature
count_components(n: int, edges: int[][]) -> int
```

## Tests

```json tests
{"function":"count_components","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"n":5,"edges":[[0,1],[1,2],[3,4]]},"expected":2},
{"name":"example-2","tags":["visible"],"args":{"n":4,"edges":[]},"expected":4},
{"name":"edge-zero-nodes","tags":["edge"],"args":{"n":0,"edges":[]},"expected":0},
{"name":"edge-self-loop-and-duplicates","tags":["edge"],"args":{"n":3,"edges":[[1,1],[0,2],[2,0]]},"expected":2},
{"name":"hidden-one-component","tags":["hidden"],"args":{"n":4,"edges":[[0,1],[1,2],[2,3]]},"expected":1},
{"name":"random-1","tags":["hidden"],"args":{"n":9,"edges":[[0,1],[0,0],[4,8],[5,2]]},"expected":6},
{"name":"random-2","tags":["hidden"],"args":{"n":5,"edges":[[0,3]]},"expected":4},
{"name":"random-3","tags":["hidden"],"args":{"n":6,"edges":[[0,4],[0,5],[2,0]]},"expected":3},
{"name":"random-4","tags":["hidden"],"args":{"n":3,"edges":[]},"expected":3}
]}
```

## Reference solution

```python reference
def solve(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    comps = n
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            comps -= 1
    return comps
```

## Interviewer notes

- **Target complexity:** O((n + m) * alpha(n)) with union-find; O(n + m) with BFS/DFS
- **Clarifying questions (answer verbatim):**
  - Q: Are isolated nodes components?  
    A: Yes.
- **Hint ladder:**
  - H0 (free): Two natural approaches: graph search or union-find.
  - H1 (-5): With union-find: start with n components, subtract one for every successful union.
  - H2 (-10): Union by size and path compression keep it near-linear.
  - H3 (-20): With DFS use an explicit stack for 500000 nodes.
- **Follow-ups:**
  - Detect the redundant edge that creates a cycle.
  - Dynamic edge additions with queries interleaved.
- **Mistakes the tests are built to catch:**
  - Recursive DFS overflowing.
  - Counting only the nodes that appear in edges.
