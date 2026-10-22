---
id: lc-b16-network-delay-time
title: Network Delay Time
type: live-coding
level: [junior, mid]
tags: [graph, dijkstra, heap]
time_minutes: 30
languages: [python]
entry: network_delay
kind: func
runs_code: true
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

## Stub

```python
def network_delay(times, n, k):
    """network_delay(times: int[][3], n: int, k: int) -> int"""
    raise NotImplementedError
```

## Signature

```signature
network_delay(times: int[][], n: int, k: int) -> int
```

## Tests

```json tests
{"function":"network_delay","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[10000,30000,60000],"limit_ms":6000,"max_exponent":1.7},"cases":[
{"name":"example-1","tags":["visible"],"args":{"times":[[2,1,1],[2,3,1],[3,4,1]],"n":4,"k":2}},
{"name":"example-2","tags":["visible"],"args":{"times":[[1,2,1]],"n":2,"k":2}},
{"name":"edge-single-node","tags":["edge"],"args":{"times":[],"n":1,"k":1}},
{"name":"edge-unreachable","tags":["edge"],"args":{"times":[[1,2,5]],"n":3,"k":1}},
{"name":"hidden-shorter-indirect","tags":["hidden"],"args":{"times":[[1,2,10],[1,3,1],[3,2,1]],"n":3,"k":1}},
{"name":"hidden-parallel-edges","tags":["hidden"],"args":{"times":[[1,2,9],[1,2,2]],"n":2,"k":1}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    n = rnd.randint(1, 6)
    times = [[rnd.randint(1, n), rnd.randint(1, n), rnd.randint(1, 9)] for _ in range(rnd.randint(0, 10))]
    times = [t for t in times if t[0] != t[1]]
    return {"times": times, "n": n, "k": rnd.randint(1, n)}

def gen_perf(n):
    rnd = random.Random(16)
    times = [[i, i + 1, rnd.randint(1, 100)] for i in range(1, n)]
    for _ in range(4 * n):
        u, v = rnd.randint(1, n), rnd.randint(1, n)
        if u != v:
            times.append([u, v, rnd.randint(1, 100)])
    return {"times": times, "n": n, "k": 1}
```

## Interviewer notes

- **Target complexity:** O((V + E) log V)
- **Scaling check:** sizes [10000, 30000, 60000], limit 6000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.7
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
