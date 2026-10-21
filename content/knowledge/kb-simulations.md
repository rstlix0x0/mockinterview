---
id: kb-simulations
title: System Design Simulations
type: knowledge
level: [junior, mid, senior, staff]
tags: [system-design, simulation, consistent-hashing, caching, queues, rate-limiting]
source: adapted
author: mockinterview
time_minutes: 5
---

# System Design: Simulations to Test Your Own Claims

Part of the mockinterview plugin. This file is for you to read. Each simulation is a small, deterministic program (fixed random seeds). The agent runs them on request (tell it "let's check that"), and the results below were produced by the shipped tools. Check a claim before you state a number in an interview-style answer; the point is to know which claims hold and by how much. All outputs below were produced by the shipped tools.

## 1. Consistent hashing: balance and movement ([5], [6])

Command: `python3 runner/tools/sim_hashring.py` (options: `--nodes`, `--vnodes 1,10,100`, `--keys`).

```text
10 nodes, 100000 keys; ideal share per node = 10.0%; ideal keys moved when one node joins = 9.1%
vnodes   max/mean load  min/mean load  stdev/mean keys moved   moved only to new node
1        3.39           0.01           1.027      22.3%        True
10       1.42           0.53           0.327      7.6%         True
100      1.16           0.86           0.086      9.2%         True
500      1.14           0.94           0.061      9.0%         True
hash % N  -> hash % (N+1): 90.8% of keys moved
```

What to conclude: with one point per node the busiest node holds 3.4x its fair share and the least busy almost nothing; with 100 virtual nodes per machine the spread tightens to 1.16x; adding an eleventh node moves 9.2% of the keys with 100 virtual nodes (ideal 9.1%), every moved key goes to the new node, and modulo hashing would move 91% of all keys. Costs to mention: more points means more metadata and more sources to stream from when a node joins or leaves.

## 2. Cache hit ratio under skewed and uniform traffic ([8])

Command: `python3 runner/tools/sim_cache.py --alpha 0.0,1.0` (options: `--items`, `--requests`, `--fractions`). Request popularity follows a Zipf-like law, where the item of rank x is requested with probability proportional to 1/x^alpha, a common model for web content [8]. The tool compares an LRU cache with an ideal cache that always holds the most popular items.

```text
alpha = 0.0 (uniform), 100000 items, 200000 requests
  cache size       LRU hits   ideal hits
  0.1% (100 items) 0.1%       0.1%      
  1.0% (1000 items) 1.0%       1.0%      
  5.0% (5000 items) 4.9%       5.0%      
  20.0% (20000 items) 18.9%      20.0%     
alpha = 1.0 (skewed), 100000 items, 200000 requests
  cache size       LRU hits   ideal hits
  0.1% (100 items) 29.1%      42.9%     
  1.0% (1000 items) 50.6%      61.9%     
  5.0% (5000 items) 66.1%      75.2%     
  20.0% (20000 items) 78.3%      86.7%
```

What to conclude: with uniform traffic a cache of 1% of the items gives about a 1% hit ratio, so caching is pointless; with alpha = 1.0, a cache of 1% of the items gives 51% (LRU) and 5% gives 66%, and 20% gives 78%. The famous "20% of the data serves 80% of the requests" holds only for some workloads: measure or state the skew you assume. LRU lands below the ideal cache because it must learn popularity.

## 3. Queues: Little's law, utilisation and backlog ([7])

Commands: `python3 runner/tools/sim_queue.py` (utilisation sweep), `python3 runner/tools/sim_queue.py --lambda 120 --seconds 60 --overload` (arrival rate above capacity). Little's law says that in a stable system the average number of items in the system equals the arrival rate times the average time each spends in it, L = lambda x W; it needs no assumption about the arrival or service distributions, but it does require steady state, and it gives averages only, not tail latency [7].

```text
10 workers, mean service 100 ms -> capacity 100 requests/s
utilisation  lambda/s   L          lambda*W     mean ms    p99 ms    
0.50         50         5.01       5.02         100        462       
0.70         70         7.51       7.51         107        466       
0.80         80         9.63       9.63         120        487       
0.90         90         14.84      14.84        164        595       
0.95         95         23.19      23.23        244        876
```

```text
lambda=120/s capacity=100/s utilisation=1.20
L=616.14  lambda*W=744.67  mean latency 6154 ms  p99 12630 ms
requests still unfinished at the end: 1220; formula (lambda - capacity) * T = 1200
```

What to conclude: at 70% utilisation the mean latency is 107 ms and p99 466 ms; at 95% the mean is 244 ms and p99 876 ms for the same service time, so a system run near full utilisation has terrible tails. Under overload (120 requests/s against a capacity of 100/s) the unfinished work after 60 s is about 1220 against the formula (lambda - capacity) x T = 1,200, and L no longer equals lambda x W because the system is not in steady state. Drain time after a burst is the backlog divided by the spare capacity (capacity minus arrival rate).

## 4. Rate limiting algorithms at a window boundary

Command: `python3 runner/tools/sim_ratelimit.py`. A client idles, sends 100 requests just before a window boundary and 100 just after, against a limit of 100 per 60 seconds.

```text
boundary burst: 100 requests just before t=60 s and 100 just after, limit 100 per 60 s
  fixed window counter                 allowed 200 of 200
  sliding window log                   allowed 100 of 200
  sliding window counter (weighted)    allowed 100 of 200
  token bucket                         allowed 100 of 200
sustained 2x overload for 600 s (a perfect limiter allows about 1000)
  fixed window counter                 allowed 1000
  sliding window log                   allowed 1000
  sliding window counter (weighted)    allowed 991
  token bucket                         allowed 1099
```

What to conclude: the fixed window counter lets 200 requests through in a fraction of a second, twice the limit; the log, the weighted counter and the token bucket allow 100. The sustained-overload run shows the token bucket admitting a few extra requests from its initial burst allowance and the weighted counter slightly under the ideal, which is the accuracy you give up for two counters per key instead of a timestamp per request.

## 5. News feed fan-out

Command: `python3 runner/tools/sim_fanout.py` (options: `--users`, `--top-followers`, `--skew`, `--threshold`, `--posts`, `--reads`). Followers follow a power law: a handful of accounts have tens of thousands of followers.

```text
100000 users, 1056832 follow edges, 10.6 accounts followed per user on average, 12 accounts above the threshold
         timeline writes / day  lookups per feed read  worst single post     
push     1.06e+06               1.0                    50000                 
pull     1e+05                  10.6                   1                     
hybrid   8.85e+05               2.7                    4970                  
feed reads per day: 1e+06, so read lookups per day: push 1e+06, pull 1.06e+07, hybrid 2.72e+06
```

What to conclude: pure push makes the biggest account's single post cost 50000 timeline writes; pure pull makes every feed read perform about 10.6 lookups; the hybrid caps a post at 4970 writes and reads at about 2.7 lookups. The hybrid saves only 16% of total timeline writes here, because most edges belong to ordinary accounts; its value is bounding the worst case, not the average.

## 6. Double booking under concurrency

Command: `python3 runner/tools/sim_booking.py` (options: `--rooms`, `--buyers`). Real threads and real SQLite connections race for 5 rooms. The exact oversell count varies from run to run, because the race window depends on thread timing.

```text
5 rooms, 20 buyers racing
  check-then-act       bookings made: 20  OVERSOLD by 15
  conditional-update   bookings made: 5   ok
  unique-insert        bookings made: 5   ok
```

What to conclude: reading the remaining count and then writing it back sells more rooms than exist (the unsafe variant sleeps 5 ms between the two steps to make the race reliable, but real races need no sleep, they just happen less often). A conditional update (`... WHERE remaining > 0` and check the affected row count) or a unique constraint on the concrete unit makes the database arbitrate, and sells exactly 5. The same idea fixes seat sales (S12), driver assignment (S11) and job triggering (S13).

---

## References

5. Karger, Lehman, Leighton, Levine, Lewin, Panigrahy. "Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the World Wide Web", MIT (balance, monotonicity, spread, load). <https://cs.brown.edu/courses/csci2950-u/f09/papers/chash97stoc.pdf>
6. DeCandia et al. "Dynamo: Amazon's Highly Available Key-value Store" (consistent hashing with virtual nodes, (N, R, W) quorums with R + W > N, sloppy quorum and hinted handoff, vector clocks). Course copy of the paper. <https://courses.grainger.illinois.edu/cs525/sp2010/Dynamo_paper_CS525.pdf>
7. Greg Wilson. "Little's Law" (statement, steady-state assumption, connection pool example). <https://third-bit.com/2026/05/30/littles-law/>
8. Doyle et al., USENIX USITS 2003 (section on Web workload: Zipf-like popularity of static objects and the resulting cache hit-ratio model). <https://static.usenix.org/event/usits03/tech/full_papers/doyle/doyle_html/node4.html>

All links were opened while writing these documents (October 2026). Numbers and demonstrations were produced by running the tools in `runner/tools/`, not copied from the sources.
