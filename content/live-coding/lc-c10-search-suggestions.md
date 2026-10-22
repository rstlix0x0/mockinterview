---
id: lc-c10-search-suggestions
title: Search Suggestions
type: live-coding
level: [senior]
tags: [design, trie, binary-search, sorting]
time_minutes: 35
entry: Autocomplete
kind: ops
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

## Signature

```signature
Autocomplete()
add(text: string, count: int) -> void
suggest(prefix: string, k: int) -> string[]
```

## Tests

```json tests
{"function":"Autocomplete","kind":"ops","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["Autocomplete",[]],["add",["car",5]],["add",["card",5]],["add",["care",9]],["add",["cat",1]],["suggest",["car",2]],["add",["cat",20]],["suggest",["ca",2]],["suggest",["x",3]]]},"expected":[null,null,null,null,null,["care","car"],null,["cat","care"],[]]},
{"name":"edge-empty-prefix","tags":["edge"],"args":{"calls":[["Autocomplete",[]],["add",["b",1]],["add",["a",1]],["suggest",["",5]]]},"expected":[null,null,null,["a","b"]]},
{"name":"edge-no-match","tags":["edge"],"args":{"calls":[["Autocomplete",[]],["suggest",["a",3]],["add",["b",1]],["suggest",["a",3]]]},"expected":[null,[],null,[]]},
{"name":"hidden-exact-match-included","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["ab",1]],["add",["abc",1]],["suggest",["ab",5]]]},"expected":[null,null,null,["ab","abc"]]},
{"name":"hidden-counts-accumulate","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["x",1]],["add",["y",2]],["add",["x",5]],["suggest",["",2]]]},"expected":[null,null,null,null,["x","y"]]},
{"name":"hidden-case-sensitive","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["Apple",1]],["add",["apple",1]],["suggest",["A",5]],["suggest",["a",5]]]},"expected":[null,null,null,["Apple"],["apple"]]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["abc",4]],["add",["car",3]],["add",["bab",5]],["add",["cart",1]],["suggest",["ab",1]],["add",["care",4]],["add",["ba",1]],["add",["ab",1]],["add",["car",1]],["suggest",["ab",2]],["suggest",["car",4]]]},"expected":[null,null,null,null,null,["abc"],null,null,null,null,["abc","ab"],["car","care","cart"]]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["add",["cart",5]],["suggest",["a",2]],["add",["a",3]],["add",["car",2]],["add",["ba",5]],["add",["a",2]],["suggest",["a",1]],["add",["care",3]],["add",["care",5]],["suggest",["b",2]],["add",["ba",4]],["suggest",["b",1]]]},"expected":[null,null,[],null,null,null,null,["a"],null,null,["ba"],null,["ba"]]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["suggest",["a",2]],["add",["b",4]],["suggest",["a",2]],["suggest",["car",1]],["suggest",["",1]],["add",["ba",5]],["suggest",["ab",1]],["suggest",["ab",3]],["suggest",["ca",4]],["suggest",["b",2]],["suggest",["a",3]],["add",["cart",1]],["suggest",["a",2]]]},"expected":[null,[],null,[],[],["b"],null,[],[],[],["ba","b"],[],null,[]]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["Autocomplete",[]],["suggest",["b",3]],["add",["card",1]],["suggest",["z",2]],["add",["cart",4]],["add",["ab",4]],["add",["ba",1]],["suggest",["ca",3]],["suggest",["a",1]],["suggest",["a",4]]]},"expected":[null,[],null,[],null,null,null,["cart","card"],["ab"],["ab"]]}
]}
```

## Reference solution

```python reference
import bisect

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
```

## Interviewer notes

- **Target complexity:** Sorted array: O(n) insert, O(log n + m log m) suggest. Trie with per-node top-k: O(len) for both.
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
