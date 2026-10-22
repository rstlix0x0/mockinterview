---
id: lc-a04-group-anagrams
title: Group Anagrams
type: live-coding
level: [junior]
tags: [hash-map, sorting]
time_minutes: 15
entry: group_anagrams
kind: func
source: adapted
author: mockinterview
legacy_id: A4
---

# Group Anagrams

## Statement

Group the words that are anagrams of each other. Inside each group sort the words ascending. Sort the groups by their first word ascending. Duplicate words stay in the group once per occurrence. The empty string is a valid word.

**Signature:** `group_anagrams(words: string[]) -> string[][]`

**Constraints:**
- 0 <= len(words) <= 100000
- words are lowercase ASCII

**Examples:**

- **Example 1** - input: `{"words":["eat","tea","tan","ate","nat","bat"]}`  
  output: `[["ate","eat","tea"],["bat"],["nat","tan"]]`
- **Example 2** - input: `{"words":[""]}`  
  output: `[[""]]`

## Signature

```signature
group_anagrams(words: string[]) -> string[][]
```

## Tests

```json tests
{"function":"group_anagrams","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"words":["eat","tea","tan","ate","nat","bat"]},"expected":[["ate","eat","tea"],["bat"],["nat","tan"]]},
{"name":"example-2","tags":["visible"],"args":{"words":[""]},"expected":[[""]]},
{"name":"edge-empty-list","tags":["edge"],"args":{"words":[]},"expected":[]},
{"name":"edge-duplicates","tags":["edge"],"args":{"words":["a","a","b"]},"expected":[["a","a"],["b"]]},
{"name":"hidden-all-same","tags":["hidden"],"args":{"words":["abc","bca","cab","abc"]},"expected":[["abc","abc","bca","cab"]]},
{"name":"hidden-singletons","tags":["hidden"],"args":{"words":["x","y","z"]},"expected":[["x"],["y"],["z"]]},
{"name":"random-1","tags":["hidden"],"args":{"words":["","","",""]},"expected":[["","","",""]]},
{"name":"random-2","tags":["hidden"],"args":{"words":["","","cbc","","aa"]},"expected":[["","",""],["aa"],["cbc"]]},
{"name":"random-3","tags":["hidden"],"args":{"words":["a","","ac","cc","b","c"]},"expected":[[""],["a"],["ac"],["b"],["c"],["cc"]]},
{"name":"random-4","tags":["hidden"],"args":{"words":["","abb","bb"]},"expected":[[""],["abb"],["bb"]]}
]}
```

## Reference solution

```python reference
from collections import defaultdict

def solve(words):
    g = defaultdict(list)
    for w in words:
        g[''.join(sorted(w))].append(w)
    groups = [sorted(v) for v in g.values()]
    return sorted(groups, key=lambda grp: grp[0])
```

## Interviewer notes

- **Target complexity:** O(n * k log k) time for k = max word length
- **Clarifying questions (answer verbatim):**
  - Q: What is the output ordering?  
    A: As stated: each group sorted, groups ordered by first word.
  - Q: Case sensitivity?  
    A: Inputs are lowercase.
- **Hint ladder:**
  - H0 (free): What do all anagrams of a word have in common?
  - H1 (-5): A canonical key.
  - H2 (-10): Sorted letters, or a 26-count signature, as a map key.
  - H3 (-20): Sort groups at the end to satisfy the output contract.
- **Follow-ups:**
  - Use a count-signature key to reach O(n * k).
  - Words are Unicode: what changes?
- **Mistakes the tests are built to catch:**
  - Ignoring the required output ordering.
  - Using a mutable list as a hash key in languages that disallow it.
