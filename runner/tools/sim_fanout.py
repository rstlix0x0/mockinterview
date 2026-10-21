#!/usr/bin/env python3
"""News feed fan-out: push (write) versus pull (read) versus hybrid, with a realistic follower skew.

    python runner/tools/sim_fanout.py
    python runner/tools/sim_fanout.py --users 200000 --top-followers 100000 --threshold 10000

Follower count of the user with popularity rank r is top_followers / r^skew (at least 1).
Every user posts `posts_per_day` times and opens the feed `reads_per_day` times.
  push   : a post is copied into every follower's timeline (write amplification), a read is one lookup
  pull   : a post is stored once, a read merges the recent posts of every followee (fan-in)
  hybrid : accounts above `threshold` followers are pulled at read time, everyone else is pushed
"""
import sys


def followers(users, top, skew):
    return [max(1, int(top / (r ** skew))) for r in range(1, users + 1)]


def analyse(users=100000, top=50000, skew=0.9, threshold=5000, posts_per_day=1.0, reads_per_day=10.0):
    f = followers(users, top, skew)
    edges = sum(f)
    avg_following = edges / users
    push_writes = posts_per_day * edges
    big = [x for x in f if x > threshold]
    small_edges = edges - sum(big)
    hybrid_writes = posts_per_day * small_edges
    big_edges_per_user = sum(big) / users              # average number of "celebrity" followees per reader
    return {
        "users": users, "edges": edges, "avg_following": avg_following, "celebrities": len(big),
        "push": {"writes_per_day": push_writes, "lookups_per_read": 1.0, "worst_post_fanout": max(f)},
        "pull": {"writes_per_day": posts_per_day * users, "lookups_per_read": avg_following, "worst_post_fanout": 1},
        "hybrid": {"writes_per_day": hybrid_writes, "lookups_per_read": 1.0 + big_edges_per_user,
                   "worst_post_fanout": max([x for x in f if x <= threshold] or [0])},
        "reads_per_day": users * reads_per_day,
    }


def main():
    a = sys.argv[1:]
    kw = {}
    names = {"--users": ("users", int), "--top-followers": ("top", int), "--skew": ("skew", float),
             "--threshold": ("threshold", int), "--posts": ("posts_per_day", float), "--reads": ("reads_per_day", float)}
    for i in range(0, len(a), 2):
        k, cast = names[a[i]]
        kw[k] = cast(a[i + 1])
    r = analyse(**kw)
    print("%d users, %d follow edges, %.1f accounts followed per user on average, %d accounts above the threshold" %
          (r["users"], r["edges"], r["avg_following"], r["celebrities"]))
    print("%-8s %-22s %-22s %-22s" % ("", "timeline writes / day", "lookups per feed read", "worst single post"))
    for k in ("push", "pull", "hybrid"):
        s = r[k]
        print("%-8s %-22.3g %-22.1f %-22d" % (k, s["writes_per_day"], s["lookups_per_read"], s["worst_post_fanout"]))
    print("feed reads per day: %.3g, so read lookups per day: push %.3g, pull %.3g, hybrid %.3g" %
          (r["reads_per_day"], r["reads_per_day"] * r["push"]["lookups_per_read"],
           r["reads_per_day"] * r["pull"]["lookups_per_read"], r["reads_per_day"] * r["hybrid"]["lookups_per_read"]))


if __name__ == "__main__":
    main()
