---
id: lc-b25-connected-components
title: Connected Components
type: live-coding
level: [junior, mid]
tags: [graph, union-find]
time_minutes: 20
languages: [python]
entry: count_components
kind: func
runs_code: true
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

## Stub

```python
def count_components(n, edges):
    """count_components(n: int, edges: int[][2]) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"count_components","kind":"func","compare":"exact","fuzz":30,"perf":{"sizes":[50000,150000,300000],"limit_ms":6000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"n":5,"edges":[[0,1],[1,2],[3,4]]}},
{"name":"example-2","tags":["visible"],"args":{"n":4,"edges":[]}},
{"name":"edge-zero-nodes","tags":["edge"],"args":{"n":0,"edges":[]}},
{"name":"edge-self-loop-and-duplicates","tags":["edge"],"args":{"n":3,"edges":[[1,1],[0,2],[2,0]]}},
{"name":"hidden-one-component","tags":["hidden"],"args":{"n":4,"edges":[[0,1],[1,2],[2,3]]}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    n = rnd.randint(0, 9)
    edges = [[rnd.randrange(n), rnd.randrange(n)] for _ in range(rnd.randint(0, 8))] if n else []
    return {"n": n, "edges": edges}

def gen_perf(n):
    rnd = random.Random(225)
    return {"n": n, "edges": [[rnd.randrange(n), rnd.randrange(n)] for _ in range(n)]}
```

## Interviewer notes

- **Target complexity:** O((n + m) * alpha(n)) with union-find; O(n + m) with BFS/DFS
- **Scaling check:** sizes [50000, 150000, 300000], limit 6000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
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
