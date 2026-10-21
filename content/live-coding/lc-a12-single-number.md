---
id: lc-a12-single-number
title: Single Number
type: live-coding
level: [junior]
tags: [bit-manipulation]
time_minutes: 10
languages: [python]
entry: single_number
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: A12
---

# Single Number

## Statement

Every value in `nums` appears exactly twice except one value that appears once. Return that value. Aim for O(n) time and O(1) extra space.

**Signature:** `single_number(nums: int[]) -> int`

**Constraints:**
- 1 <= len(nums) <= 1000001 (odd)

**Examples:**

- **Example 1** - input: `{"nums":[2,2,1]}`  
  output: `1`
- **Example 2** - input: `{"nums":[4,1,2,1,2]}`  
  output: `4`

## Stub

```python
def single_number(nums):
    """single_number(nums: int[]) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"single_number","kind":"func","compare":"exact","fuzz":15,"perf":{"sizes":[100000,500000,1000000],"limit_ms":3000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[2,2,1]}},
{"name":"example-2","tags":["visible"],"args":{"nums":[4,1,2,1,2]}},
{"name":"edge-single","tags":["edge"],"args":{"nums":[7]}},
{"name":"edge-negative","tags":["edge"],"args":{"nums":[-3,5,5]}},
{"name":"hidden-zero","tags":["hidden"],"args":{"nums":[0,1,1]}}
]}
```

## Oracle

```python oracle
def solve(nums):
    r = 0
    for x in nums:
        r ^= x
    return r

def gen_random(seed):
    rnd = random.Random(seed)
    vals = rnd.sample(range(-50, 50), rnd.randint(1, 8))
    single = vals[0]
    arr = vals[1:] * 2 + [single]
    rnd.shuffle(arr)
    return {"nums": arr}

def gen_perf(n):
    rnd = random.Random(212)
    vals = rnd.sample(range(-10**9, 10**9), n // 2 + 1)
    arr = vals[1:] * 2 + [vals[0]]
    rnd.shuffle(arr)
    return {"nums": arr}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
- **Scaling check:** sizes [100000, 500000, 1000000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Can the unique value be negative or zero?  
    A: Yes.
- **Hint ladder:**
  - H0 (free): A hash map works. Can you avoid the memory?
  - H1 (-5): What is x XOR x? And x XOR 0?
  - H2 (-10): XOR is commutative and associative.
  - H3 (-20): XOR everything together.
- **Follow-ups:**
  - Every value appears three times except one.
  - Two values appear once.
- **Mistakes the tests are built to catch:**
  - Sorting (O(n log n)) when O(n) was asked.
  - Using addition tricks that overflow.
