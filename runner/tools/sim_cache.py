#!/usr/bin/env python3
"""Cache hit ratio under skewed (Zipf) and uniform popularity.

    python runner/tools/sim_cache.py                         # 100000 items, alpha 0.0 / 0.8 / 1.0 / 1.2
    python runner/tools/sim_cache.py --items 50000 --requests 300000 --alpha 1.0 --fractions 0.01,0.05,0.2

Item with popularity rank x is requested with probability proportional to 1 / x^alpha [Zipf-like web traffic].
Prints the hit ratio of an LRU cache and of an ideal cache that always holds the most popular items,
for several cache sizes given as a fraction of the item count.
Use it to answer "how big must the cache be?" with a number, and to see why caching a uniform workload is pointless.
"""
import bisect
import itertools
import random
import sys
from collections import OrderedDict


def zipf_cdf(n, alpha):
    w = [1.0 / (x ** alpha) for x in range(1, n + 1)]
    total = sum(w)
    return list(itertools.accumulate(p / total for p in w)), [p / total for p in w]


def lru_hit_ratio(requests, capacity):
    cache, hits = OrderedDict(), 0
    for item in requests:
        if item in cache:
            hits += 1
            cache.move_to_end(item)
        else:
            cache[item] = True
            if len(cache) > capacity:
                cache.popitem(last=False)
    return hits / len(requests)


def experiment(items=100000, requests_n=200000, alpha=1.0, fractions=(0.001, 0.01, 0.05, 0.2), seed=7):
    rnd = random.Random(seed)
    cdf, probs = zipf_cdf(items, alpha)
    reqs = [bisect.bisect(cdf, rnd.random()) for _ in range(requests_n)]
    reqs = [min(r, items - 1) for r in reqs]
    rows = []
    for f in fractions:
        cap = max(1, int(items * f))
        rows.append({"fraction": f, "capacity": cap, "lru": lru_hit_ratio(reqs, cap), "ideal": sum(probs[:cap])})
    return rows


def main():
    a = sys.argv[1:]
    items, reqs, alphas, fr = 100000, 200000, (0.0, 0.8, 1.0, 1.2), (0.001, 0.01, 0.05, 0.2)
    i = 0
    while i < len(a):
        if a[i] == "--items":
            items = int(a[i + 1])
        elif a[i] == "--requests":
            reqs = int(a[i + 1])
        elif a[i] == "--alpha":
            alphas = tuple(float(x) for x in a[i + 1].split(","))
        elif a[i] == "--fractions":
            fr = tuple(float(x) for x in a[i + 1].split(","))
        i += 2
    for al in alphas:
        print("alpha = %.1f (%s), %d items, %d requests" % (al, "uniform" if al == 0 else "skewed", items, reqs))
        print("  %-16s %-10s %-10s" % ("cache size", "LRU hits", "ideal hits"))
        for r in experiment(items, reqs, al, fr):
            print("  %-16s %-10s %-10s" % ("%.1f%% (%d items)" % (100 * r["fraction"], r["capacity"]),
                                          "%.1f%%" % (100 * r["lru"]), "%.1f%%" % (100 * r["ideal"])))


if __name__ == "__main__":
    main()
