#!/usr/bin/env python3
"""Consistent hashing experiment: how uneven is the load, and how many keys move when a node joins?

    python runner/tools/sim_hashring.py                       # 10 nodes, vnodes 1,10,100,500, 100000 keys
    python runner/tools/sim_hashring.py --nodes 20 --vnodes 1,50,200 --keys 200000

Compares a hash ring with virtual nodes against the naive `hash(key) % N` scheme.
Verifies the claims people make in interviews:
  * a ring with one point per node is badly unbalanced; many virtual nodes fix that
  * adding a node moves about 1/(N+1) of the keys on a ring, but almost all keys with `% N`
"""
import bisect
import hashlib
import statistics
import sys


def h(s):
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")


class Ring:
    def __init__(self, nodes, vnodes):
        self.vnodes = vnodes
        self.points = []   # sorted list of (hash, node)
        for n in nodes:
            self.add(n)

    def add(self, node):
        for i in range(self.vnodes):
            bisect.insort(self.points, (h("%s#%d" % (node, i)), node))

    def get(self, key):
        i = bisect.bisect(self.points, (h(key), chr(0x10FFFF)))
        return self.points[i % len(self.points)][1]


def loads(assign, nodes):
    counts = {n: 0 for n in nodes}
    for n in assign:
        counts[n] += 1
    return counts


def experiment(nodes_n=10, vnodes_list=(1, 10, 100, 500), keys_n=100000):
    nodes = ["node%d" % i for i in range(nodes_n)]
    keys = ["key%d" % i for i in range(keys_n)]
    rows = []
    for v in vnodes_list:
        ring = Ring(nodes, v)
        before = [ring.get(k) for k in keys]
        c = loads(before, nodes)
        mean = keys_n / nodes_n
        ring.add("node%d" % nodes_n)
        after = [ring.get(k) for k in keys]
        moved = sum(1 for a, b in zip(before, after) if a != b) / keys_n
        # monotonicity: a key may only move to the NEW node
        only_to_new = all(b == "node%d" % nodes_n for a, b in zip(before, after) if a != b)
        rows.append({"vnodes": v, "max_over_mean": max(c.values()) / mean, "min_over_mean": min(c.values()) / mean,
                     "cv": statistics.pstdev(c.values()) / mean, "moved": moved, "only_to_new": only_to_new})
    mod_before = [h(k) % nodes_n for k in keys]
    mod_after = [h(k) % (nodes_n + 1) for k in keys]
    mod_moved = sum(1 for a, b in zip(mod_before, mod_after) if a != b) / keys_n
    return rows, mod_moved, 1.0 / (nodes_n + 1)


def main():
    a = sys.argv[1:]
    nodes_n, keys_n, vn = 10, 100000, (1, 10, 100, 500)
    i = 0
    while i < len(a):
        if a[i] == "--nodes":
            nodes_n = int(a[i + 1])
        elif a[i] == "--keys":
            keys_n = int(a[i + 1])
        elif a[i] == "--vnodes":
            vn = tuple(int(x) for x in a[i + 1].split(","))
        i += 2
    rows, mod_moved, ideal = experiment(nodes_n, vn, keys_n)
    print("%d nodes, %d keys; ideal share per node = %.1f%%; ideal keys moved when one node joins = %.1f%%" %
          (nodes_n, keys_n, 100.0 / nodes_n, 100 * ideal))
    print("%-8s %-14s %-14s %-10s %-12s %s" % ("vnodes", "max/mean load", "min/mean load", "stdev/mean", "keys moved", "moved only to new node"))
    for r in rows:
        print("%-8d %-14.2f %-14.2f %-10.3f %-12s %s" % (r["vnodes"], r["max_over_mean"], r["min_over_mean"], r["cv"],
                                                          "%.1f%%" % (100 * r["moved"]), r["only_to_new"]))
    print("hash %% N  -> hash %% (N+1): %.1f%% of keys moved" % (100 * mod_moved))


if __name__ == "__main__":
    main()
