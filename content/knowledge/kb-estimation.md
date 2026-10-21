---
id: kb-estimation
title: Estimation Toolkit
type: knowledge
level: [junior, mid, senior, staff]
tags: [system-design, estimation, back-of-envelope]
source: adapted
author: mockinterview
time_minutes: 10
---

# System Design: Estimation Toolkit

Part of the mockinterview plugin. This file is for you to read. The numbers in it are the ones worth knowing by heart; the drills in section 4 are for practice with the agent.

## 1. Numbers worth memorising

Powers of two and decimal approximations [1]:

| Power | Approximate value | Name |
|---|---|---|
| 10 | 1 thousand | 1 KB |
| 20 | 1 million | 1 MB |
| 30 | 1 billion | 1 GB |
| 40 | 1 trillion | 1 TB |
| 50 | 1 quadrillion | 1 PB |

Latency numbers [1] (they originate from Jeff Dean's 2010 talk and are *old*: use them for orders of magnitude and ratios, not absolute values; networks and SSDs are much faster today than the disk seeks listed here):

| Operation | Time |
|---|---|
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 100 ns |
| Main memory reference | 100 ns |
| Compress 1 KB | 10 µs |
| Send 2 KB over 1 Gbps network | 20 µs |
| Read 1 MB sequentially from memory | 250 µs |
| Round trip within the same datacenter | 500 µs |
| Disk seek | 10 ms |
| Read 1 MB sequentially from the network | 10 ms |
| Read 1 MB sequentially from disk | 30 ms |
| Packet round trip California to Netherlands and back | 150 ms |

The lasting lessons from this table: memory is orders of magnitude faster than disk; sequential access is far cheaper than random access; a cross-continent round trip costs more than a million memory references; and compressing before sending is often worth it.

Availability targets [1]:

| Availability | Downtime per year | Per month | Per day |
|---|---|---|---|
| 99% | 3.65 days | 7.31 hours | 14.4 minutes |
| 99.99% | 52.6 minutes | 4.38 minutes | 8.64 seconds |
| 99.999% | 5.26 minutes | 26.3 seconds | 0.86 seconds |

Handy conversions (computed, then rounded): one day is 86,400 seconds, so about 10^5. **1 million requests per day is about 12 per second; 1 billion per day is about 11,600 per second.** 1 million records of 1 KB are 1 GB; 1 billion records of 1 KB are 1 TB.

## 2. The method

1. **Assumptions first, in writing, with units.** Daily active users, actions per user per day, bytes per action, read/write ratio, retention, replication. Source guidance: round aggressively, write assumptions down, label every unit, and practise the standard quantities: QPS, peak QPS, storage, cache size and server count [1].
2. **QPS**: `users x actions per day / 86,400`. **Peak**: multiply by a factor (2 to 3 for smooth consumer traffic; much more for events, see S12 and S6).
3. **Storage**: `bytes per record x records per day x 365 x years x replication`; adjust for overwrites and compression.
4. **Bandwidth**: `peak QPS x bytes per request`.
5. **Memory for caches**: the hot fraction of the daily read volume is an *upper bound*; repeated reads of popular items shrink it (see `runner/tools/sim_cache.py`).
6. **Servers**: peak QPS divided by what one server sustains, which is itself an assumption you must state.
7. **Say what the numbers decide**: "this is 3 TB, so one database holds it; we shard for throughput and failure isolation, not size."

## 3. The calculator

The agent's calculator (`runner/tools/estimate.py calc assumptions.json`) prints every derived quantity; `runner/tools/estimate.py check REFERENCE CANDIDATE` compares a candidate's claims with their own assumptions and with a reference. Units are decimal (1 KB = 1,000 bytes). A worked example using the numbers from the published back-of-the-envelope chapter [1] (300 million monthly users, half active daily, two posts per day, 10% of posts carry a 1 MB media file; the source says these are exercise numbers, not real ones):

Assumptions (`tweets.json`):

```json
{"mau": 300000000, "dau_ratio": 0.5, "writes_per_user_day": 2, "bytes_per_write": 100000, "peak_factor": 2, "retention_years": 5, "replication": 1}
```

`python3 runner/tools/estimate.py calc tweets.json` prints:

```text
write_qps              3.47 K
read_qps               0
peak_write_qps         6.94 K
peak_read_qps          0
daily_write_bytes      30 TB
total_storage_bytes    54.8 PB
ingress_bytes_per_s    694 MB/s
egress_bytes_per_s     0 B/s
cache_bytes            0 B
```

The chapter's answers are about 3,500 QPS, 7,000 at peak, 30 TB of media per day and about 55 PB over 5 years; the tool agrees [1].

## 4. Estimation drills

Do each drill in 5 to 10 minutes: write assumptions, compute by hand, write `.mockinterview/work/estimate-Dn.json`, then ask the agent to check it. The reference assumptions are in the appendix at the end of this document; look at them only after your attempt.

| Drill | Prompt |
|---|---|
| D1 | A photo-sharing app: 50 million daily users upload 2 photos a day (2 MB each) and view 50 photos a day (200 KB each). Keep photos for 10 years with 3 copies. Peak is 2x the average. How much storage, and what is the peak read bandwidth? |
| D2 | A messaging app: 10 million daily users send 30 messages a day, 200 bytes each. Keep messages for 3 years with 3 copies. Peak is 3x the average. |
| D3 | A web analytics service receives 500 million events a day of 300 bytes each and keeps them for a year with 2 copies. |
| D4 | A video site: 20 million daily users watch 3 videos a day, 50 MB each. Peak is 2x the average. What is the peak egress? |
| D5 | Search suggestions: 30 million daily users run 8 searches a day, each producing 4 suggestion requests. Peak is 2x the average. |
| D6 | A log pipeline: 5,000 servers each write 200 lines a second of 300 bytes. Keep 30 days with 2 copies. |

## 5. How to write your estimate file

The agent's checker reads a small JSON file in `.mockinterview/work/`. Write your assumptions, then the numbers you computed by hand (the claims). The checker tells you whether your claims follow from your own assumptions, and whether they are within 10x of the reference.

```json
{
  "assumptions": {"dau": 2e8, "writes_per_user_day": 0.5, "reads_per_user_day": 10,
                  "bytes_per_write": 1000, "bytes_per_read": 20000, "peak_factor": 3,
                  "retention_years": 5, "replication": 3},
  "claims": {"write_qps": 1200, "peak_read_qps": 70000, "total_storage_bytes": 5.5e14}
}
```

---

## Appendix: reference assumptions for the drills

Look at these only after you have written your own estimate. They are the assumptions the agent checks your claims against (the `check` command of `runner/tools/estimate.py` compares your claims with your own assumptions, and with these within a 10x band). They restate the drill prompts in section 4 as numbers.

**D1**

```json
{"dau": 50000000.0, "writes_per_user_day": 2, "reads_per_user_day": 50, "bytes_per_write": 2000000.0, "bytes_per_read": 200000.0, "peak_factor": 2, "retention_years": 10, "replication": 3}
```

**D2**

```json
{"dau": 10000000.0, "writes_per_user_day": 30, "reads_per_user_day": 0, "bytes_per_write": 200, "peak_factor": 3, "retention_years": 3, "replication": 3}
```

**D3**

```json
{"dau": 500000000.0, "writes_per_user_day": 1, "bytes_per_write": 300, "peak_factor": 2, "retention_years": 1, "replication": 2}
```

**D4**

```json
{"dau": 20000000.0, "reads_per_user_day": 3, "bytes_per_read": 50000000.0, "peak_factor": 2}
```

**D5**

```json
{"dau": 30000000.0, "reads_per_user_day": 32, "bytes_per_read": 300, "peak_factor": 2}
```

**D6**

```json
{"dau": 5000, "writes_per_user_day": 17280000, "bytes_per_write": 300, "peak_factor": 1.5, "retention_years": 0.0822, "replication": 2}
```

## References

1. ByteByteGo. "Back-of-the-Envelope Estimation", System Design Interview course chapter (latency numbers, powers of two, availability table, worked QPS and storage example, estimation tips). <https://bytebytego.com/courses/system-design-interview/back-of-the-envelope-estimation>

All links were opened while writing these documents (October 2026). Numbers and demonstrations were produced by running the tools in `runner/tools/`, not copied from the sources.
