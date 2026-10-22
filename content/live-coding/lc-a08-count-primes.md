---
id: lc-a08-count-primes
title: Count Primes Below N
type: live-coding
level: [junior]
tags: [math, sieve]
time_minutes: 10
entry: count_primes
kind: func
source: adapted
author: mockinterview
legacy_id: A8
---

# Count Primes Below N

## Statement

Return the number of prime numbers strictly less than `n`.

**Signature:** `count_primes(n: int) -> int`

**Constraints:**
- 0 <= n <= 5000000

**Examples:**

- **Example 1** - input: `{"n":10}`  
  output: `4`
- **Example 2** - input: `{"n":0}`  
  output: `0`
- **Example 3** - input: `{"n":2}`  
  output: `0`

## Signature

```signature
count_primes(n: int) -> int
```

## Tests

```json tests
{"function":"count_primes","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"n":10},"expected":4},
{"name":"example-2","tags":["visible"],"args":{"n":0},"expected":0},
{"name":"example-3","tags":["visible"],"args":{"n":2},"expected":0},
{"name":"edge-n-1","tags":["edge"],"args":{"n":1},"expected":0},
{"name":"edge-n-3","tags":["edge"],"args":{"n":3},"expected":1},
{"name":"hidden-100","tags":["hidden"],"args":{"n":100},"expected":25},
{"name":"hidden-10000","tags":["hidden"],"args":{"n":10000},"expected":1229},
{"name":"random-1","tags":["hidden"],"args":{"n":295},"expected":62},
{"name":"random-2","tags":["hidden"],"args":{"n":182},"expected":42},
{"name":"random-3","tags":["hidden"],"args":{"n":199},"expected":45},
{"name":"random-4","tags":["hidden"],"args":{"n":103},"expected":26}
]}
```

## Reference solution

```python reference
def solve(n):
    if n < 3:
        return 0
    sieve = bytearray([1]) * n
    sieve[0:2] = b'\x00\x00'
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, n, i)))
    return sum(sieve)
```

## Interviewer notes

- **Target complexity:** O(n log log n) time, O(n) space
- **Clarifying questions (answer verbatim):**
  - Q: Upper bound?  
    A: 5 million.
- **Hint ladder:**
  - H0 (free): What is the cost of testing every number by trial division?
  - H1 (-5): Mark multiples instead of testing divisibility.
  - H2 (-10): Sieve of Eratosthenes. Start crossing off at i*i.
  - H3 (-20): A byte or bit array keeps memory small.
- **Follow-ups:**
  - Segmented sieve for n up to 10^10.
  - Count primes in a range [lo, hi].
- **Mistakes the tests are built to catch:**
  - Off-by-one: 'strictly less than'.
  - Starting the inner loop at 2*i and doing too much work.
  - A boolean list that exhausts memory in some languages.
