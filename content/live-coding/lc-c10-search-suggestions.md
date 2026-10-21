---
id: lc-c10-search-suggestions
title: Search Suggestions
type: live-coding
level: [senior]
tags: [design, trie, binary-search, sorting]
time_minutes: 35
languages: [python]
entry: Autocomplete
kind: ops
runs_code: true
source: adapted
author: mockinterview
legacy_id: C10
---

# Search Suggestions

## Statement

Implement `Autocomplete`. `add(text, count)` adds `count` to the popularity of `text` (creating it if new). `suggest(prefix, k)` returns up to `k` known texts that start with `prefix` (the empty prefix matches everything), ordered by popularity descending, then alphabetically ascending. Matching is case-sensitive and plain code-point order is used for alphabetical ties.

**Signature:** `class Autocomplete { add(text: string, count: int); suggest(prefix: string, k: int) -> string[] }`

**Constraints:**
- up to 200000 operations
- 1 <= k <= 10
- the typical prefix matches few texts, but the empty prefix is allowed

**Examples:**

- **Example 1** - calls: `Autocomplete(); add("car", 5); add("card", 5); add("care", 9); add("cat", 1); suggest("car", 2); add("cat", 20); suggest("ca", 2); suggest("x", 3)`  
  returns: `[null,null,null,null,null,["care","car"],null,["cat","care"],[]]`

## Stub

```python
class Autocomplete:
    def __init__(self):
        """No constructor arguments."""
        pass

    def add(self, text, count):
        """add(text: string, count: int)"""
        raise NotImplementedError

    def suggest(self, prefix, k):
        """suggest(prefix: string, k: int) -> string[]"""
        raise NotImplementedError
```

## Tests

```json tests
{"function":"Autocomplete","kind":"ops","compare":"exact","fuzz":40,"perf":{"sizes":[20000,60000,120000],"limit_ms":6000,"max_exponent":1.6},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["Autocomplete",[]],["add",["car",5]],["add",["card",5]],["add",["care",9]],["add",["cat",1]],["suggest",["car",2]],["add",["cat",20]],["suggest",["ca",2]],["suggest",["x",3]]]}},
{"name":"edge-empty-prefix","tags":["edge"],"args":{"calls":[["Autocomplete",[]],["add",["b",1]],["add",["a",1]],["suggest",["",5]]]}},
{"name":"edge-no-match","tags":["edge"],"args":{"calls":[["Autocomplete",[]],["suggest",["a",3]],["add",["b",1]],["suggest",["a",3]]]}},
{"name":"hidden-exact-match-included","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["ab",1]],["add",["abc",1]],["suggest",["ab",5]]]}},
{"name":"hidden-counts-accumulate","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["x",1]],["add",["y",2]],["add",["x",5]],["suggest",["",2]]]}},
{"name":"hidden-case-sensitive","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["Apple",1]],["add",["apple",1]],["suggest",["A",5]],["suggest",["a",5]]]}}
]}
```

## Oracle

```python oracle
class Autocomplete:
    def __init__(self):
        self.counts = {}
        self.keys = []

    def add(self, text, count):
        if text in self.counts:
            self.counts[text] += count
        else:
            self.counts[text] = count
            bisect.insort(self.keys, text)

    def suggest(self, prefix, k):
        lo = bisect.bisect_left(self.keys, prefix)
        hi = bisect.bisect_left(self.keys, prefix + "\U0010ffff")
        found = self.keys[lo:hi]
        found.sort(key=lambda t: (-self.counts[t], t))
        return found[:k]

def gen_random(seed):
    rnd = random.Random(seed)
    words = ["a", "ab", "abc", "abd", "b", "ba", "bab", "car", "card", "care", "cart"]
    return rand_ops(rnd, ("Autocomplete",), rnd.randint(5, 30), [
        (4, lambda r: ("add", r.choice(words), r.randint(1, 5))),
        (4, lambda r: ("suggest", r.choice(["", "a", "ab", "b", "ca", "car", "z"]), r.randint(1, 4)))])

def gen_perf(n):
    rnd = random.Random(110)
    letters = "abcdefghijklmnopqrstuvwxyz"
    calls = [["Autocomplete", []]]
    for i in range(n):
        w = "".join(rnd.choice(letters) for _ in range(rnd.randint(4, 9)))
        if i % 3 == 2:
            calls.append(["suggest", [w[:3], 5]])
        else:
            calls.append(["add", [w, rnd.randint(1, 9)]])
    return {"calls": calls}
```

## Interviewer notes

- **Target complexity:** Sorted array: O(n) insert, O(log n + m log m) suggest. Trie with per-node top-k: O(len) for both.
- **Scaling check:** sizes [20000, 60000, 120000], limit 6000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.6
- **Clarifying questions (answer verbatim):**
  - Q: Is the empty string a valid text?  
    A: Not in tests, but the empty prefix is.
- **Hint ladder:**
  - H0 (free): Start with a dictionary of counts and a linear scan to get it correct.
  - H1 (-5): Texts with a given prefix form one contiguous range in sorted order.
  - H2 (-10): Binary search for the range start and end. How do you build the upper bound?
  - H3 (-20): Or: a trie where each node caches its top-k, trading memory and update cost for fast reads.
- **Follow-ups:**
  - Ten million texts and 50k QPS: shard by prefix? Cache hot prefixes? Offline top-k per prefix?
  - Decay old counts (recency weighting).
  - Typo tolerance.
- **Mistakes the tests are built to catch:**
  - Sorting all texts on every suggest.
  - Wrong tie-break order.
  - Prefix upper bound that excludes some code points.
