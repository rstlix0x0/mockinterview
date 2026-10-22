---
id: lc-b24-combination-sum
title: Combination Sum
type: live-coding
level: [junior, mid]
tags: [backtracking]
time_minutes: 25
languages: [python]
entry: combination_sum
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B24
---

# Combination Sum

## Statement

Given distinct positive integers `candidates` and a `target`, return every unique combination of candidates that sums to `target`. A candidate may be used any number of times. Each combination is listed in non-decreasing order, and the combinations are returned in lexicographic order. Different orderings of the same multiset count as one combination.

**Signature:** `combination_sum(candidates: int[], target: int) -> int[][]`

**Constraints:**
- 1 <= len(candidates) <= 10
- 1 <= target <= 40
- the number of results is at most 10000

**Examples:**

- **Example 1** - input: `{"candidates":[2,3,6,7],"target":7}`  
  output: `[[2,2,3],[7]]`
- **Example 2** - input: `{"candidates":[2,3,5],"target":8}`  
  output: `[[2,2,2,2],[2,3,3],[3,5]]`

## Stub

```python
def combination_sum(candidates, target):
    """combination_sum(candidates: int[], target: int) -> int[][]"""
    raise NotImplementedError
```

## Signature

```signature
combination_sum(candidates: int[], target: int) -> int[][]
```

## Tests

```json tests
{"function":"combination_sum","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[20,30,40],"limit_ms":4000,"max_exponent":null},"cases":[
{"name":"example-1","tags":["visible"],"args":{"candidates":[2,3,6,7],"target":7}},
{"name":"example-2","tags":["visible"],"args":{"candidates":[2,3,5],"target":8}},
{"name":"edge-impossible","tags":["edge"],"args":{"candidates":[5,7],"target":3}},
{"name":"edge-single-candidate","tags":["edge"],"args":{"candidates":[3],"target":9}},
{"name":"hidden-unsorted-input","tags":["hidden"],"args":{"candidates":[7,2,3],"target":7}}
]}
```

## Oracle

```python oracle
def solve(candidates, target):
    cands = sorted(set(candidates))
    res = []

    def go(start, remaining, path):
        if remaining == 0:
            res.append(list(path))
            return
        for i in range(start, len(cands)):
            c = cands[i]
            if c > remaining:
                break
            path.append(c)
            go(i, remaining - c, path)
            path.pop()
    go(0, target, [])
    return res

def gen_random(seed):
    rnd = random.Random(seed)
    return {"candidates": rnd.sample(range(1, 10), rnd.randint(1, 4)), "target": rnd.randint(1, 15)}

def gen_perf(n):
    return {"candidates": [2, 3, 5, 7, 11], "target": n}
```

## Interviewer notes

- **Target complexity:** Output-sensitive; pruning with sorted candidates
- **Scaling check:** sizes [20, 30, 40], limit 4000 ms (calibrated to a straightforward Python solution)
- **Clarifying questions (answer verbatim):**
  - Q: Is the input sorted?  
    A: Not necessarily.
- **Hint ladder:**
  - H0 (free): What decision do you make at each step?
  - H1 (-5): Choose a candidate, or move on to the next candidate.
  - H2 (-10): To avoid permutations, only allow candidates at index >= the last used index.
  - H3 (-20): Sort first so you can stop early when a candidate exceeds the remainder.
- **Follow-ups:**
  - Each candidate may be used once, with duplicates in the input (Combination Sum II).
  - Count the combinations only (DP).
- **Mistakes the tests are built to catch:**
  - Producing [2,3,2] and [3,2,2] separately.
  - Not stopping once the remainder is exceeded.
  - Returning unsorted combinations.
