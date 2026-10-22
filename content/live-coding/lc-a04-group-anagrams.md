---
id: lc-a04-group-anagrams
title: Group Anagrams
type: live-coding
level: [junior]
tags: [hash-map, sorting]
time_minutes: 15
languages: [python]
entry: group_anagrams
kind: func
runs_code: true
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

## Stub

```python
def group_anagrams(words):
    """group_anagrams(words: string[]) -> string[][]"""
    raise NotImplementedError
```

## Signature

```signature
group_anagrams(words: string[]) -> string[][]
```

## Tests

```json tests
{"function":"group_anagrams","kind":"func","compare":"exact","fuzz":6,"cases":[
{"name":"example-1","tags":["visible"],"args":{"words":["eat","tea","tan","ate","nat","bat"]}},
{"name":"example-2","tags":["visible"],"args":{"words":[""]}},
{"name":"edge-empty-list","tags":["edge"],"args":{"words":[]}},
{"name":"edge-duplicates","tags":["edge"],"args":{"words":["a","a","b"]}},
{"name":"hidden-all-same","tags":["hidden"],"args":{"words":["abc","bca","cab","abc"]}},
{"name":"hidden-singletons","tags":["hidden"],"args":{"words":["x","y","z"]}}
]}
```

## Oracle

```python oracle
def solve(words):
    g = defaultdict(list)
    for w in words:
        g[''.join(sorted(w))].append(w)
    groups = [sorted(v) for v in g.values()]
    return sorted(groups, key=lambda grp: grp[0])

def gen_random(seed):
    rnd = random.Random(seed)
    return {"words": [''.join(rnd.choice("abc") for _ in range(rnd.randint(0, 3))) for _ in range(rnd.randint(0, 8))]}
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
