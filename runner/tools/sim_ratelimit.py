#!/usr/bin/env python3
"""Rate limiting algorithms side by side, on the traffic pattern that separates them.

    python runner/tools/sim_ratelimit.py

All limiters allow `limit` requests per `window` seconds for one client. The scenario: the client is idle,
sends a burst of `limit` requests just before a window boundary and another burst just after it.
A good limiter lets about `limit` through in that short span; a fixed window lets about twice as many.
Memory per client: fixed window 1 counter; sliding log up to `limit` timestamps; sliding counter 2 counters;
token bucket 2 numbers (tokens, last refill time).
"""
from collections import deque


class FixedWindow:
    name = "fixed window counter"

    def __init__(self, limit, window):
        self.limit, self.window, self.win, self.count = limit, window, None, 0

    def allow(self, t):
        w = int(t // self.window)
        if w != self.win:
            self.win, self.count = w, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


class SlidingLog:
    name = "sliding window log"

    def __init__(self, limit, window):
        self.limit, self.window, self.log = limit, window, deque()

    def allow(self, t):
        while self.log and self.log[0] <= t - self.window:
            self.log.popleft()
        if len(self.log) < self.limit:
            self.log.append(t)
            return True
        return False


class SlidingCounter:
    name = "sliding window counter (weighted)"

    def __init__(self, limit, window):
        self.limit, self.window, self.win, self.cur, self.prev = limit, window, None, 0, 0

    def allow(self, t):
        w = int(t // self.window)
        if w != self.win:
            self.prev = self.cur if self.win == w - 1 else 0
            self.win, self.cur = w, 0
        frac = (t - w * self.window) / self.window
        if self.prev * (1 - frac) + self.cur + 1 <= self.limit:
            self.cur += 1
            return True
        return False


class TokenBucket:
    name = "token bucket"

    def __init__(self, limit, window):
        self.capacity, self.rate = float(limit), limit / window
        self.tokens, self.last = float(limit), None

    def allow(self, t):
        if self.last is not None:
            self.tokens = min(self.capacity, self.tokens + (t - self.last) * self.rate)
        self.last = t
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


ALGOS = [FixedWindow, SlidingLog, SlidingCounter, TokenBucket]


def boundary_burst(limit=100, window=60.0):
    """Burst of `limit` requests ending at t = window - 0.1 and another of `limit` starting at t = window + 0.1."""
    times = [window - 0.1 - 0.05 * (limit - 1 - i) / limit for i in range(limit)]
    times += [window + 0.1 + 0.05 * i / limit for i in range(limit)]
    out = {}
    for cls in ALGOS:
        lim = cls(limit, window)
        out[cls.name] = sum(1 for t in times if lim.allow(t))
    return out


def sustained(limit=100, window=60.0, factor=2.0, seconds=600.0):
    """Evenly spaced traffic at `factor` times the allowed rate for `seconds`."""
    n = int(limit / window * factor * seconds)
    out = {}
    for cls in ALGOS:
        lim = cls(limit, window)
        out[cls.name] = sum(1 for i in range(n) if lim.allow(i * seconds / n))
    return out, limit / window * seconds


def main():
    print("boundary burst: 100 requests just before t=60 s and 100 just after, limit 100 per 60 s")
    for k, v in boundary_burst().items():
        print("  %-36s allowed %d of 200" % (k, v))
    out, ideal = sustained()
    print("sustained 2x overload for 600 s (a perfect limiter allows about %.0f)" % ideal)
    for k, v in out.items():
        print("  %-36s allowed %d" % (k, v))


if __name__ == "__main__":
    main()
