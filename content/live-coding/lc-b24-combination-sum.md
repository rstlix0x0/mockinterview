---
id: lc-b24-combination-sum
title: Combination Sum
type: live-coding
level: [junior, mid]
tags: [backtracking]
time_minutes: 25
entry: combination_sum
kind: func
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

## Signature

```signature
combination_sum(candidates: int[], target: int) -> int[][]
```

## Tests

```json tests
{"function":"combination_sum","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"candidates":[2,3,6,7],"target":7},"expected":[[2,2,3],[7]]},
{"name":"example-2","tags":["visible"],"args":{"candidates":[2,3,5],"target":8},"expected":[[2,2,2,2],[2,3,3],[3,5]]},
{"name":"edge-impossible","tags":["edge"],"args":{"candidates":[5,7],"target":3},"expected":[]},
{"name":"edge-single-candidate","tags":["edge"],"args":{"candidates":[3],"target":9},"expected":[[3,3,3]]},
{"name":"hidden-unsorted-input","tags":["hidden"],"args":{"candidates":[7,2,3],"target":7},"expected":[[2,2,3],[7]]},
{"name":"random-1","tags":["hidden"],"args":{"candidates":[1,2,6],"target":1},"expected":[[1]]},
{"name":"random-2","tags":["hidden"],"args":{"candidates":[2,9,4],"target":10},"expected":[[2,2,2,2,2],[2,2,2,4],[2,4,4]]},
{"name":"random-3","tags":["hidden"],"args":{"candidates":[1,7],"target":3},"expected":[[1,1,1]]},
{"name":"random-4","tags":["hidden"],"args":{"candidates":[2,5,6,7],"target":13},"expected":[[2,2,2,2,5],[2,2,2,7],[2,5,6],[6,7]]}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** Output-sensitive; pruning with sorted candidates
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
