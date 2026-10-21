---
id: lc-b05-course-order
title: Course Order (Lexicographically Smallest Topological Sort)
type: live-coding
level: [junior, mid]
tags: [graph, topological-sort, heap]
time_minutes: 30
languages: [python]
entry: topo_order
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B5
---

# Course Order (Lexicographically Smallest Topological Sort)

## Statement

There are `n` tasks numbered `0..n-1`. Each edge `[u, v]` means task `u` must come before task `v`. Return an ordering of all tasks that respects every edge. When several tasks are available, always pick the smallest number first, so the answer is unique. If the dependencies contain a cycle, return an empty list. Duplicate edges are possible.

**Signature:** `topo_order(n: int, edges: int[][2]) -> int[]`

**Constraints:**
- 1 <= n <= 100000
- 0 <= len(edges) <= 300000
- no self loops

**Examples:**

- **Example 1** - input: `{"n":4,"edges":[[1,0],[2,0],[3,1],[3,2]]}`  
  output: `[3,1,2,0]`
- **Example 2** - input: `{"n":2,"edges":[[0,1],[1,0]]}`  
  output: `[]`

## Stub

```python
def topo_order(n, edges):
    """topo_order(n: int, edges: int[][2]) -> int[]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"topo_order","kind":"func","compare":"exact","fuzz":20,"perf":{"sizes":[10000,50000,100000],"limit_ms":4000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"n":4,"edges":[[1,0],[2,0],[3,1],[3,2]]}},
{"name":"example-2","tags":["visible"],"args":{"n":2,"edges":[[0,1],[1,0]]}},
{"name":"edge-single","tags":["edge"],"args":{"n":1,"edges":[]}},
{"name":"edge-no-edges","tags":["edge"],"args":{"n":4,"edges":[]}},
{"name":"edge-duplicate-edges","tags":["edge"],"args":{"n":3,"edges":[[0,1],[0,1],[1,2]]}},
{"name":"hidden-cycle-with-tail","tags":["hidden"],"args":{"n":4,"edges":[[0,1],[1,2],[2,1],[2,3]]}},
{"name":"hidden-reverse-numbering","tags":["hidden"],"args":{"n":4,"edges":[[3,2],[2,1],[1,0]]}}
]}
```

## Oracle

```python oracle
def solve(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    heap = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return order if len(order) == n else []

def gen_random(seed):
    rnd = random.Random(seed)
    n = rnd.randint(1, 6)
    edges = []
    for _ in range(rnd.randint(0, 8)):
        u, v = rnd.randrange(n), rnd.randrange(n)
        if u != v and (seed % 3 or u < v):
            edges.append([u, v])
    return {"n": n, "edges": edges}

def gen_perf(n):
    rnd = random.Random(5)
    edges = [[i, i + 1] for i in range(n - 1)]
    for _ in range(2 * n):
        a, b = sorted(rnd.sample(range(n), 2))
        edges.append([a, b])
    return {"n": n, "edges": edges}
```

## Interviewer notes

- **Target complexity:** O((V + E) log V) time
- **Scaling check:** sizes [10000, 50000, 100000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: Is the graph connected?  
    A: Not necessarily.
- **Hint ladder:**
  - H0 (free): What does a task with no unmet dependency look like?
  - H1 (-5): Track the number of unmet dependencies (in-degree).
  - H2 (-10): Kahn's algorithm. Which data structure gives you the smallest available task?
  - H3 (-20): If fewer than n tasks come out, there is a cycle.
- **Follow-ups:**
  - Report one concrete cycle.
  - Tasks have durations: compute the earliest finish of every task (critical path).
- **Mistakes the tests are built to catch:**
  - A plain queue gives a valid but not the required order.
  - Not detecting cycles when some tasks are still processable.
  - Recursion overflow with DFS on a 100000-long chain.
