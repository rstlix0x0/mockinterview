---
id: lc-b16-network-delay-time
title: Network Delay Time
type: live-coding
level: [junior, mid]
tags: [graph, dijkstra, heap]
time_minutes: 30
entry: network_delay
kind: func
source: adapted
author: mockinterview
legacy_id: B16
---

# Network Delay Time

## Statement

A directed weighted network has nodes `1..n`. Each entry `[u, v, w]` in `times` is a link taking `w` time units from `u` to `v`. A signal starts at node `k`. Return the time for all nodes to receive it, or `-1` if some node is unreachable.

**Signature:** `network_delay(times: int[][3], n: int, k: int) -> int`

**Constraints:**
- 1 <= n <= 100000
- 0 <= len(times) <= 500000
- 1 <= w <= 100

**Examples:**

- **Example 1** - input: `{"times":[[2,1,1],[2,3,1],[3,4,1]],"n":4,"k":2}`  
  output: `2`
- **Example 2** - input: `{"times":[[1,2,1]],"n":2,"k":2}`  
  output: `-1`

## Signature

```signature
network_delay(times: int[][], n: int, k: int) -> int
```

## Tests

```json tests
{"function":"network_delay","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"times":[[2,1,1],[2,3,1],[3,4,1]],"n":4,"k":2},"expected":2},
{"name":"example-2","tags":["visible"],"args":{"times":[[1,2,1]],"n":2,"k":2},"expected":-1},
{"name":"edge-single-node","tags":["edge"],"args":{"times":[],"n":1,"k":1},"expected":0},
{"name":"edge-unreachable","tags":["edge"],"args":{"times":[[1,2,5]],"n":3,"k":1},"expected":-1},
{"name":"hidden-shorter-indirect","tags":["hidden"],"args":{"times":[[1,2,10],[1,3,1],[3,2,1]],"n":3,"k":1},"expected":2},
{"name":"hidden-parallel-edges","tags":["hidden"],"args":{"times":[[1,2,9],[1,2,2]],"n":2,"k":1},"expected":2},
{"name":"random-1","tags":["hidden"],"args":{"times":[[1,3,9],[3,2,2],[5,4,1]],"n":5,"k":3},"expected":-1},
{"name":"random-2","tags":["hidden"],"args":{"times":[[1,2,7]],"n":3,"k":3},"expected":-1},
{"name":"random-3","tags":["hidden"],"args":{"times":[[1,3,4],[3,2,6]],"n":4,"k":4},"expected":-1},
{"name":"random-4","tags":["hidden"],"args":{"times":[],"n":2,"k":2},"expected":-1}
]}
```

## Reference solution

```python reference
import heapq
from collections import defaultdict

def solve(times, n, k):
    adj = defaultdict(list)
    for u, v, w in times:
        adj[u].append((v, w))
    dist = {k: 0}
    pq = [(0, k)]
    done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v, w in adj[u]:
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return max(dist.values()) if len(dist) == n else -1
```

## Interviewer notes

- **Target complexity:** O((V + E) log V)
- **Clarifying questions (answer verbatim):**
  - Q: Negative weights?  
    A: No.
  - Q: Multiple edges between the same pair?  
    A: Possible.
- **Hint ladder:**
  - H0 (free): Which algorithm for single-source shortest paths with non-negative weights?
  - H1 (-5): Dijkstra with a min-heap.
  - H2 (-10): The answer is the largest shortest distance; check that every node was reached.
  - H3 (-20): Skip stale heap entries.
- **Follow-ups:**
  - Negative weights (Bellman-Ford).
  - Return the node that is reached last.
- **Mistakes the tests are built to catch:**
  - BFS (ignores weights).
  - Returning the sum of distances.
  - Forgetting the unreachable check.
