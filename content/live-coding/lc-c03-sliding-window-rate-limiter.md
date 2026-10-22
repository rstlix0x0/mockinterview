---
id: lc-c03-sliding-window-rate-limiter
title: Sliding-Window Rate Limiter
type: live-coding
level: [mid, senior]
tags: [design, queue, sliding-window]
time_minutes: 35
entry: RateLimiter
kind: ops
source: adapted
author: mockinterview
legacy_id: C3
---

# Sliding-Window Rate Limiter

## Statement

Implement `RateLimiter(limit, window)`. `allow(key, ts)` returns `true` and records the request if fewer than `limit` requests for `key` were **allowed** in the half-open window `(ts - window, ts]`; otherwise it returns `false` and records nothing. Timestamps are integers and never decrease across calls. Memory used per key must stay bounded by `limit` entries.

**Signature:** `class RateLimiter { constructor(limit: int, window: int); allow(key, ts: int) -> bool }`

**Constraints:**
- 1 <= limit <= 1000
- 1 <= window <= 10^9
- timestamps non-decreasing across all calls
- up to 300000 calls

**Examples:**

- **Example 1** - calls: `RateLimiter(2, 10); allow("u", 1); allow("u", 2); allow("u", 3); allow("u", 11); allow("u", 12)`  
  returns: `[null,true,true,false,true,true]`

## Signature

```signature
RateLimiter(limit: int, window: int)
allow(key: string, ts: int) -> bool
```

## Tests

```json tests
{"function":"RateLimiter","kind":"ops","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["RateLimiter",[2,10]],["allow",["u",1]],["allow",["u",2]],["allow",["u",3]],["allow",["u",11]],["allow",["u",12]]]},"expected":[null,true,true,false,true,true]},
{"name":"edge-boundary-exact","tags":["edge"],"args":{"calls":[["RateLimiter",[1,5]],["allow",["k",0]],["allow",["k",4]],["allow",["k",5]]]},"expected":[null,true,false,true]},
{"name":"edge-independent-keys","tags":["edge"],"args":{"calls":[["RateLimiter",[1,100]],["allow",["a",1]],["allow",["b",1]],["allow",["a",2]],["allow",["b",2]]]},"expected":[null,true,true,false,false]},
{"name":"hidden-same-timestamp","tags":["hidden"],"args":{"calls":[["RateLimiter",[3,10]],["allow",["k",7]],["allow",["k",7]],["allow",["k",7]],["allow",["k",7]]]},"expected":[null,true,true,true,false]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["RateLimiter",[3,3]],["allow",["z",0]],["allow",["z",0]],["allow",["y",0]],["allow",["x",2]],["allow",["z",2]],["allow",["x",5]]]},"expected":[null,true,true,true,true,true,true]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["RateLimiter",[2,1]],["allow",["z",3]],["allow",["z",6]],["allow",["z",6]],["allow",["x",8]],["allow",["y",8]],["allow",["y",8]],["allow",["x",10]],["allow",["y",11]]]},"expected":[null,true,true,true,true,true,true,true,true]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["RateLimiter",[2,2]],["allow",["z",0]],["allow",["x",2]],["allow",["z",4]],["allow",["y",5]],["allow",["z",6]],["allow",["z",8]],["allow",["z",11]],["allow",["x",13]]]},"expected":[null,true,true,true,true,true,true,true,true]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["RateLimiter",[3,4]],["allow",["y",2]],["allow",["z",4]],["allow",["y",4]],["allow",["y",4]],["allow",["x",4]],["allow",["x",7]],["allow",["z",7]]]},"expected":[null,true,true,true,true,true,true,true]}
]}
```

## Reference solution

```python reference
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, limit, window):
        self.limit, self.window = limit, window
        self.log = defaultdict(deque)

    def allow(self, key, ts):
        dq = self.log[key]
        while dq and dq[0] <= ts - self.window:
            dq.popleft()
        if len(dq) < self.limit:
            dq.append(ts)
            return True
        return False
```

## Interviewer notes

- **Target complexity:** O(1) amortised per call, O(limit) memory per key
- **Clarifying questions (answer verbatim):**
  - Q: Do rejected requests count toward the limit?  
    A: No.
  - Q: Is the window boundary inclusive?  
    A: (ts - window, ts]: a request exactly `window` ago has expired.
- **Hint ladder:**
  - H0 (free): What do you need to remember per key?
  - H1 (-5): Only the timestamps of allowed requests that are still inside the window.
  - H2 (-10): They arrive in order, so a queue per key works.
  - H3 (-20): Before deciding, drop the front while front <= ts - window.
- **Follow-ups:**
  - Memory for millions of idle keys: how do you evict them?
  - Token bucket instead of a log. What changes for bursts?
  - Distributed version over Redis: atomicity (Lua / INCR+EXPIRE) and clock skew.
  - Fixed-window counter vs sliding-window log vs sliding-window counter: accuracy and memory.
- **Mistakes the tests are built to catch:**
  - Counting rejected requests.
  - Off-by-one at the window edge.
  - Storing every request forever.
  - A fixed-window counter (allows 2x bursts at boundaries).
