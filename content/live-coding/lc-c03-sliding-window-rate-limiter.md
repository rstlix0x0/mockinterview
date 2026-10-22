---
id: lc-c03-sliding-window-rate-limiter
title: Sliding-Window Rate Limiter
type: live-coding
level: [mid, senior]
tags: [design, queue, sliding-window]
time_minutes: 35
languages: [python]
entry: RateLimiter
kind: ops
runs_code: true
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

## Stub

```python
class RateLimiter:
    def __init__(self, limit, window):
        """constructor(limit: int, window: int)"""
        raise NotImplementedError

    def allow(self, key, ts):
        """allow(key, ts: int) -> bool"""
        raise NotImplementedError
```

## Signature

```signature
RateLimiter(limit: int, window: int)
allow(key: string, ts: int) -> bool
```

## Tests

```json tests
{"function":"RateLimiter","kind":"ops","compare":"exact","fuzz":30,"perf":{"sizes":[20000,100000,300000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["RateLimiter",[2,10]],["allow",["u",1]],["allow",["u",2]],["allow",["u",3]],["allow",["u",11]],["allow",["u",12]]]}},
{"name":"edge-boundary-exact","tags":["edge"],"args":{"calls":[["RateLimiter",[1,5]],["allow",["k",0]],["allow",["k",4]],["allow",["k",5]]]}},
{"name":"edge-independent-keys","tags":["edge"],"args":{"calls":[["RateLimiter",[1,100]],["allow",["a",1]],["allow",["b",1]],["allow",["a",2]],["allow",["b",2]]]}},
{"name":"hidden-same-timestamp","tags":["hidden"],"args":{"calls":[["RateLimiter",[3,10]],["allow",["k",7]],["allow",["k",7]],["allow",["k",7]],["allow",["k",7]]]}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    calls = [["RateLimiter", [rnd.randint(1, 3), rnd.randint(1, 5)]]]
    ts = 0
    for _ in range(rnd.randint(5, 30)):
        ts += rnd.randint(0, 3)
        calls.append(["allow", [rnd.choice("xyz"), ts]])
    return {"calls": calls}

def gen_perf(n):
    rnd = random.Random(103)
    calls = [["RateLimiter", [5, 1000]]]
    ts = 0
    for _ in range(n):
        ts += rnd.randint(0, 40)
        calls.append(["allow", ["k%d" % rnd.randint(0, 50), ts]])
    return {"calls": calls}
```

## Interviewer notes

- **Target complexity:** O(1) amortised per call, O(limit) memory per key
- **Scaling check:** sizes [20000, 100000, 300000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
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
