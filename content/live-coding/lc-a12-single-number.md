---
id: lc-a12-single-number
title: Single Number
type: live-coding
level: [junior]
tags: [bit-manipulation]
time_minutes: 10
entry: single_number
kind: func
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

## Signature

```signature
single_number(nums: int[]) -> int
```

## Tests

```json tests
{"function":"single_number","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"nums":[2,2,1]},"expected":1},
{"name":"example-2","tags":["visible"],"args":{"nums":[4,1,2,1,2]},"expected":4},
{"name":"edge-single","tags":["edge"],"args":{"nums":[7]},"expected":7},
{"name":"edge-negative","tags":["edge"],"args":{"nums":[-3,5,5]},"expected":-3},
{"name":"hidden-zero","tags":["hidden"],"args":{"nums":[0,1,1]},"expected":0},
{"name":"random-1","tags":["hidden"],"args":{"nums":[-35,-47,-46,-35,40,-47,40,38,38]},"expected":-46},
{"name":"random-2","tags":["hidden"],"args":{"nums":[-35,32,-42,2,3,24,-35,24,32,2,3]},"expected":-42},
{"name":"random-3","tags":["hidden"],"args":{"nums":[-49,26,-37,-37,39,26,-21,-46,-49,39,-10,-10,-46]},"expected":-21},
{"name":"random-4","tags":["hidden"],"args":{"nums":[-29,-29,3,0,-50,3,0]},"expected":-50}
]}
```

## Reference solution

```python reference
def solve(nums):
    r = 0
    for x in nums:
        r ^= x
    return r
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
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
