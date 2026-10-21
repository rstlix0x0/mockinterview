---
id: lc-c01-lru-cache
title: LRU Cache
type: live-coding
level: [mid, senior]
tags: [design, hash-map, linked-list]
time_minutes: 30
languages: [python]
entry: LRUCache
kind: ops
runs_code: true
source: adapted
author: mockinterview
legacy_id: C1
---

# LRU Cache

## Statement

Implement `LRUCache(capacity)`. `get(key)` returns the value or `-1` when absent and marks the key as most recently used. `put(key, value)` inserts or updates (also marking the key as most recently used) and, if the size would exceed `capacity`, evicts the least recently used key. Both operations must run in O(1) average time. Implement the ordering yourself with a hash map plus a doubly linked list; do not use a built-in ordered-dictionary type.

**Signature:** `class LRUCache { constructor(capacity: int); get(key: int) -> int; put(key: int, value: int) -> void }`

**Constraints:**
- 1 <= capacity <= 100000
- up to 300000 operations

**Examples:**

- **Example 1** - calls: `LRUCache(2); put(1, 1); put(2, 2); get(1); put(3, 3); get(2); put(4, 4); get(1); get(3); get(4)`  
  returns: `[null,null,null,1,null,-1,null,-1,3,4]`

## Stub

```python
class LRUCache:
    def __init__(self, capacity):
        """constructor(capacity: int)"""
        raise NotImplementedError

    def get(self, key):
        """get(key: int) -> int"""
        raise NotImplementedError

    def put(self, key, value):
        """put(key: int, value: int) -> void"""
        raise NotImplementedError
```

## Tests

```json tests
{"function":"LRUCache","kind":"ops","compare":"exact","fuzz":25,"perf":{"sizes":[20000,100000,300000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["LRUCache",[2]],["put",[1,1]],["put",[2,2]],["get",[1]],["put",[3,3]],["get",[2]],["put",[4,4]],["get",[1]],["get",[3]],["get",[4]]]}},
{"name":"edge-capacity-one","tags":["edge"],"args":{"calls":[["LRUCache",[1]],["put",[1,1]],["put",[2,2]],["get",[1]],["get",[2]]]}},
{"name":"edge-update-existing","tags":["edge"],"args":{"calls":[["LRUCache",[2]],["put",[1,1]],["put",[2,2]],["put",[1,10]],["put",[3,3]],["get",[1]],["get",[2]]]}},
{"name":"hidden-get-refreshes","tags":["hidden"],"args":{"calls":[["LRUCache",[2]],["put",[1,1]],["put",[2,2]],["get",[1]],["put",[3,3]],["get",[1]],["get",[2]],["get",[3]]]}}
]}
```

## Oracle

```python oracle
class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.d = OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        if key in self.d:
            self.d.move_to_end(key)
        self.d[key] = value
        if len(self.d) > self.cap:
            self.d.popitem(last=False)

def gen_random(seed):
    rnd = random.Random(seed)
    return rand_ops(rnd, ("LRUCache", rnd.randint(1, 4)), rnd.randint(5, 30),
                    [(3, lambda r: ("get", r.randint(0, 5))), (3, lambda r: ("put", r.randint(0, 5), r.randint(0, 99)))])

def gen_perf(n):
    rnd = random.Random(101)
    return rand_ops(rnd, ("LRUCache", 1000), n,
                    [(1, lambda r: ("get", r.randint(0, 2000))), (1, lambda r: ("put", r.randint(0, 2000), r.randint(0, 99)))])
```

## Interviewer notes

- **Target complexity:** O(1) per operation
- **Scaling check:** sizes [20000, 100000, 300000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Does updating an existing key refresh it?  
    A: Yes.
  - Q: Does a failed get change the order?  
    A: No.
- **Hint ladder:**
  - H0 (free): What two things must you find in O(1)?
  - H1 (-5): A key's entry, and the least recently used entry.
  - H2 (-10): Hash map from key to a list node, plus a doubly linked list ordered by recency.
  - H3 (-20): Sentinel head and tail nodes remove the special cases. On eviction, remove the node next to the tail sentinel and delete its key from the map.
- **Follow-ups:**
  - Make it thread-safe. Where are the lock boundaries? Would a single lock be enough?
  - Add a per-entry TTL.
  - LFU instead of LRU.
- **Mistakes the tests are built to catch:**
  - Forgetting to refresh recency on put-update.
  - Evicting before the update check, so an update of a full cache evicts something.
  - Not deleting the evicted key from the map.
