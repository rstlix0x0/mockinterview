#!/usr/bin/env python3
"""Queueing experiment: Little's law, why 95% utilisation hurts, and how fast a backlog grows or drains.

    python runner/tools/sim_queue.py                                   # utilisation sweep for 10 workers, 100 ms service time
    python runner/tools/sim_queue.py --servers 10 --service-ms 100 --lambda 80 --seconds 600
    python runner/tools/sim_queue.py --overload --servers 10 --service-ms 100 --lambda 120 --seconds 60

Model: Poisson arrivals at `lambda` per second, `servers` identical workers, exponential service times with the
given mean, one shared FIFO queue (an M/M/c queue). Little's law says L = lambda * W [Little]:
  L = average number of requests in the system (waiting plus being served), W = average time in the system.
"""
import heapq
import random
import sys


def simulate(lam, servers, service_s, seconds, seed=11):
    rnd = random.Random(seed)
    free = [0.0] * servers           # time each worker becomes free
    heapq.heapify(free)
    t, events, waits, total_time = 0.0, [], [], []
    while True:
        t += rnd.expovariate(lam)
        if t > seconds:
            break
        start = max(t, heapq.heappop(free))
        done = start + rnd.expovariate(1.0 / service_s)
        heapq.heappush(free, done)
        events.append((t, 1))
        events.append((done, -1))
        waits.append(start - t)
        total_time.append(done - t)
    events.sort()
    area, n, last = 0.0, 0, 0.0
    for when, d in events:
        if when > seconds:
            area += n * (seconds - last)
            last = seconds
            break
        area += n * (when - last)
        n += d
        last = when
    else:
        area += n * (seconds - last)
    in_system_at_end = sum(1 for _, d in events if d == -1 and _ > seconds)
    total_time_sorted = sorted(total_time)
    k = len(total_time_sorted)
    return {"arrivals": k, "lambda_obs": k / seconds, "L": area / seconds,
            "W": sum(total_time) / k, "p50": total_time_sorted[k // 2], "p99": total_time_sorted[int(k * 0.99)],
            "mean_wait": sum(waits) / k, "backlog_end": in_system_at_end}


def main():
    a = sys.argv[1:]
    opt = {"--lambda": None, "--servers": 10, "--service-ms": 100.0, "--seconds": 600.0}
    overload = "--overload" in a
    a = [x for x in a if x != "--overload"]
    for i in range(0, len(a), 2):
        opt[a[i]] = float(a[i + 1])
    servers, svc, secs = int(opt["--servers"]), opt["--service-ms"] / 1000.0, opt["--seconds"]
    cap = servers / svc
    if opt["--lambda"] is None:
        print("%d workers, mean service %.0f ms -> capacity %.0f requests/s" % (servers, svc * 1000, cap))
        print("%-12s %-10s %-10s %-12s %-10s %-10s" % ("utilisation", "lambda/s", "L", "lambda*W", "mean ms", "p99 ms"))
        for rho in (0.5, 0.7, 0.8, 0.9, 0.95):
            r = simulate(rho * cap, servers, svc, secs)
            print("%-12.2f %-10.0f %-10.2f %-12.2f %-10.0f %-10.0f" % (rho, rho * cap, r["L"], r["lambda_obs"] * r["W"], r["W"] * 1000, r["p99"] * 1000))
        return
    lam = opt["--lambda"]
    r = simulate(lam, servers, svc, secs)
    print("lambda=%.0f/s capacity=%.0f/s utilisation=%.2f" % (lam, cap, lam / cap))
    print("L=%.2f  lambda*W=%.2f  mean latency %.0f ms  p99 %.0f ms" % (r["L"], r["lambda_obs"] * r["W"], r["W"] * 1000, r["p99"] * 1000))
    if overload or lam > cap:
        print("requests still unfinished at the end: %d; formula (lambda - capacity) * T = %.0f" % (r["backlog_end"], (lam - cap) * secs))
    else:
        print("drain time for a burst of B extra requests = B / (capacity - lambda); for B = 1000: %.1f s" % (1000 / (cap - lam)))


if __name__ == "__main__":
    main()
