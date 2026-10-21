---
id: lc-b03-top-k-frequent-elements
title: Top K Frequent Elements
type: live-coding
level: [junior, mid]
tags: [hash-map, heap, sorting]
time_minutes: 20
languages: [python]
entry: top_k_frequent
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B3
---

# Top K Frequent Elements

## Statement

Return the `k` most frequent values in `nums`, ordered by frequency descending and then by value ascending. `k` is at most the number of distinct values.

**Signature:** `top_k_frequent(nums: int[], k: int) -> int[]`

**Constraints:**
- 1 <= len(nums) <= 200000
- 1 <= k <= distinct values

**Examples:**

- **Example 1** - input: `{"nums":[1,1,1,2,2,3],"k":2}`  
  output: `[1,2]`
- **Example 2** - input: `{"nums":[4,4,5,5,6],"k":2}`  
  output: `[4,5]`

## Stub

```python
def top_k_frequent(nums, k):
    """top_k_frequent(nums: int[], k: int) -> int[]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"top_k_frequent","kind":"func","compare":"exact","fuzz":15,"perf":{"sizes":[20000,100000,200000],"limit_ms":3000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[1,1,1,2,2,3],"k":2}},
{"name":"example-2","tags":["visible"],"args":{"nums":[4,4,5,5,6],"k":2}},
{"name":"edge-single","tags":["edge"],"args":{"nums":[9],"k":1}},
{"name":"edge-all-equal-freq","tags":["edge"],"args":{"nums":[3,1,2],"k":3}},
{"name":"hidden-negatives","tags":["hidden"],"args":{"nums":[-1,-1,2,2,2,0],"k":1}}
]}
```

## Oracle

```python oracle
def solve(nums, k):
    c = Counter(nums)
    return [v for v, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]

def gen_random(seed):
    rnd = random.Random(seed)
    nums = [rnd.randint(-4, 4) for _ in range(rnd.randint(1, 12))]
    return {"nums": nums, "k": rnd.randint(1, len(set(nums)))}

def gen_perf(n):
    rnd = random.Random(4)
    return {"nums": [rnd.randint(-n, n) for _ in range(n)], "k": 10}
```

## Interviewer notes

- **Target complexity:** O(n log k) with a heap, or O(n) with bucket sort
- **Scaling check:** sizes [20000, 100000, 200000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: Tie-breaking?  
    A: Lower value first.
- **Hint ladder:**
  - H0 (free): Count first.
  - H1 (-5): Then select the top k by a composite key.
  - H2 (-10): A heap of size k, or bucket by frequency for O(n).
  - H3 (-20): Respect the tie-break exactly.
- **Follow-ups:**
  - O(n) bucket-sort version.
  - Top k on a stream with bounded memory (Misra-Gries / count-min sketch discussion).
- **Mistakes the tests are built to catch:**
  - Sorting only by frequency and leaving ties unspecified.
  - Using a max-heap of all items: O(d log d) is fine but explain the trade-off.
