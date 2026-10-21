---
id: sd-fx-shortener
title: URL shortener (fixture)
type: system-design
level: [mid, senior]
tags: [caching, storage]
time_minutes: 20
source: original
author: tests
---
# URL shortener (fixture)

## Statement

> Design a service that turns long URLs into short links.

## Self-check questions

- How long must a code be?

## Interviewer notes

**Clarifying questions and answers** (give only what is asked)

| Question | Answer |
|---|---|
| Scale? | 100 million new links per month. |

### Reference design

One service, one key-value store, a cache in front.

### Deep-dive probes

- What breaks first when the cache disappears?

### Common mistakes

- Using sequential ids that can be guessed.

### Probe ladder

- P0 (free): What happens when this component fails?
- P1 (-5): Which request path is hottest?
- P2 (-10): Where would you add a cache and why?
- P3 (-20): Describe a direction in words: cache the redirect lookup.

## Reference estimate

```json estimate
{"dau": 3330000.0, "writes_per_user_day": 1, "reads_per_user_day": 100, "bytes_per_write": 500, "bytes_per_read": 500, "peak_factor": 2, "retention_years": 5, "replication": 3, "server_qps": 2000}
```
