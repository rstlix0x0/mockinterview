---
id: lc-b05-course-order
title: Course Order (Lexicographically Smallest Topological Sort)
type: live-coding
level: [junior, mid]
tags: [graph, topological-sort, heap]
time_minutes: 30
entry: topo_order
kind: func
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

## Signature

```signature
topo_order(n: int, edges: int[][]) -> int[]
```

## Tests

```json tests
{"function":"topo_order","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"n":4,"edges":[[1,0],[2,0],[3,1],[3,2]]},"expected":[3,1,2,0]},
{"name":"example-2","tags":["visible"],"args":{"n":2,"edges":[[0,1],[1,0]]},"expected":[]},
{"name":"edge-single","tags":["edge"],"args":{"n":1,"edges":[]},"expected":[0]},
{"name":"edge-no-edges","tags":["edge"],"args":{"n":4,"edges":[]},"expected":[0,1,2,3]},
{"name":"edge-duplicate-edges","tags":["edge"],"args":{"n":3,"edges":[[0,1],[0,1],[1,2]]},"expected":[0,1,2]},
{"name":"hidden-cycle-with-tail","tags":["hidden"],"args":{"n":4,"edges":[[0,1],[1,2],[2,1],[2,3]]},"expected":[]},
{"name":"hidden-reverse-numbering","tags":["hidden"],"args":{"n":4,"edges":[[3,2],[2,1],[1,0]]},"expected":[3,2,1,0]},
{"name":"random-1","tags":["hidden"],"args":{"n":5,"edges":[[2,4],[2,1]]},"expected":[0,2,1,3,4]},
{"name":"random-2","tags":["hidden"],"args":{"n":3,"edges":[[0,1]]},"expected":[0,1,2]},
{"name":"random-3","tags":["hidden"],"args":{"n":2,"edges":[]},"expected":[0,1]},
{"name":"random-4","tags":["hidden"],"args":{"n":5,"edges":[[0,4],[2,3],[0,4],[0,4],[4,1]]},"expected":[0,2,3,4,1]}
]}
```

## Reference solution

```python reference
import heapq

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
```

## Interviewer notes

- **Target complexity:** O((V + E) log V) time
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
