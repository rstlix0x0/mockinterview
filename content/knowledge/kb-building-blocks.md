---
id: kb-building-blocks
title: System Design Building Blocks
type: knowledge
level: [junior, mid, senior, staff]
tags: [system-design, caching, queues, databases, sharding]
source: adapted
author: mockinterview
time_minutes: 5
---

# System Design: Building-Block and Trade-off Cheat Sheets

Part of the mockinterview plugin. This file is for you to read. These sheets are quick references to name the right tool and its cost. For the underlying theory, see sections 9.3 to 9.5 of the `kb-cs-fundamentals` document.

## 1. Choosing storage

| Need | Good fit | Watch out for |
|---|---|---|
| Transactions, joins, constraints, moderate scale | Relational database (single primary, read replicas, later sharding) | Write throughput of one primary; cross-shard transactions |
| Simple key lookups at very large scale, high availability | Key-value or wide-column store | Limited queries; consistency options; hot keys |
| Large immutable blobs (video, images, backups) | Object storage plus CDN | Metadata lives elsewhere; consistency of listings |
| Full-text and ranked search | Search index | Eventually consistent with the source of truth; rebuild plans |
| Time series | Time-series store with compression and downsampling | Cardinality; retention |
| Ephemeral, fast shared state (counters, sessions, presence) | In-memory store with TTL | Data loss on failure; memory cost |
| Nearest-neighbour search over embeddings | Vector index (approximate) | Recall versus latency; filtered search; re-embedding on model change |

## 2. Caching

| Pattern | How | Good for | Risk |
|---|---|---|---|
| Cache-aside | App reads cache, on miss reads store and fills cache | Most read-heavy workloads | Stale data; stampede on a popular key expiring |
| Read-through | Cache layer fetches on miss | Simpler callers | Same as above |
| Write-through | Write to cache and store together | Read-after-write consistency | Slower writes |
| Write-back | Write to cache, flush later | Write-heavy bursts | Data loss if the cache fails |
| Refresh-ahead | Reload hot entries before expiry | Hot keys with predictable access | Wasted work on cold keys |

Hard parts: invalidation (prefer short TTLs and versioned keys over clever invalidation), stampede (request coalescing, jittered TTLs), hot keys (local replicas), and negative caching of misses. Use `runner/tools/sim_cache.py` before claiming a hit ratio.

## 3. Queues and delivery

| Guarantee | Meaning | How to get it |
|---|---|---|
| At most once | May lose, never duplicates | Fire and forget |
| At least once | Never loses, may duplicate | Acknowledge after processing; retry on timeout |
| Effectively exactly once | Duplicates occur but have no extra effect | At least once plus **idempotent consumers** (idempotency key, unique constraint, conditional update) |

Also decide: partition key (ordering is per partition), consumer groups, backpressure (bounded queues, reject or shed), retry policy (exponential backoff with jitter), dead-letter queue, and what happens to a queue that grows faster than it drains (see `runner/tools/sim_queue.py`).

## 4. Consistency and replication

- With N replicas, a write acknowledged by W and a read from R replicas see the latest acknowledged write when **R + W > N** [6]. Latency follows the slowest of the replicas needed [6].
- Sloppy quorums and hinted handoff trade strictness for availability during failures; conflicting versions need a policy: last-write-wins (simple, can lose updates), version vectors with application merge, or conflict-free data types [6].
- Linearizability needs consensus (Raft or Paxos) with a leader; it costs latency and availability on the minority side of a partition.
- Read-your-writes and monotonic reads can often be provided cheaply (route a user's reads to the replica or version they wrote to) without full strong consistency.

## 5. Partitioning

| Scheme | Strength | Weakness |
|---|---|---|
| Range | Range scans, easy to reason about | Hot ranges (time, alphabet) |
| Hash modulo N | Even spread | Changing N moves almost everything |
| Consistent hashing with virtual nodes | Minimal movement when nodes change; even load with enough virtual nodes [5][6] | Metadata; no range scans |
| Directory (lookup service) | Flexible, supports rebalancing | The directory is a dependency and must be highly available |

Pick the partition key from the dominant access pattern, then ask what happens to the one huge tenant, user or key.

## 6. Correctness under concurrency

| Problem | Tool |
|---|---|
| Two writers, one resource (inventory, seats, driver assignment) | Conditional update (`WHERE remaining > 0`), unique constraint, or optimistic version number; never check-then-write in application code |
| Duplicate requests from retries | Idempotency key stored with the result, unique per caller |
| Database and message bus must agree | Transactional outbox plus an at-least-once relay |
| Exclusive ownership of a partition or job | Lease with expiry and a **fencing token**, so a paused old owner cannot do damage |
| Long multi-step business process | State machine with persisted transitions; compensating actions instead of distributed transactions |

## 7. Reliability patterns

Timeouts on every remote call; retries only for idempotent operations, with exponential backoff and jitter; circuit breakers to stop hammering a failing dependency; bulkheads (separate pools) so one tenant or one dependency cannot exhaust everything; load shedding and priorities under overload; graceful degradation (serve stale or partial data); health checks and gradual rollouts with fast rollback; and an answer to "how do we know it is broken?" (metrics, logs, traces, alerts).

---

## References

5. Karger, Lehman, Leighton, Levine, Lewin, Panigrahy. "Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the World Wide Web", MIT (balance, monotonicity, spread, load). <https://cs.brown.edu/courses/csci2950-u/f09/papers/chash97stoc.pdf>
6. DeCandia et al. "Dynamo: Amazon's Highly Available Key-value Store" (consistent hashing with virtual nodes, (N, R, W) quorums with R + W > N, sloppy quorum and hinted handoff, vector clocks). Course copy of the paper. <https://courses.grainger.illinois.edu/cs525/sp2010/Dynamo_paper_CS525.pdf>

All links were opened while writing these documents (October 2026). Numbers and demonstrations were produced by running the tools in `runner/tools/`, not copied from the sources.
