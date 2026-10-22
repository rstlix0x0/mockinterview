---
id: lc-a08-count-primes
title: Count Primes Below N
type: live-coding
level: [junior]
tags: [math, sieve]
time_minutes: 10
languages: [python]
entry: count_primes
kind: func
runs_code: true
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

## Stub

```python
def count_primes(n):
    """count_primes(n: int) -> int"""
    raise NotImplementedError
```

## Signature

```signature
count_primes(n: int) -> int
```

## Tests

```json tests
{"function":"count_primes","kind":"func","compare":"exact","fuzz":10,"perf":{"sizes":[500000,2000000,5000000],"limit_ms":4000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"n":10}},
{"name":"example-2","tags":["visible"],"args":{"n":0}},
{"name":"example-3","tags":["visible"],"args":{"n":2}},
{"name":"edge-n-1","tags":["edge"],"args":{"n":1}},
{"name":"edge-n-3","tags":["edge"],"args":{"n":3}},
{"name":"hidden-100","tags":["hidden"],"args":{"n":100}},
{"name":"hidden-10000","tags":["hidden"],"args":{"n":10000}}
]}
```

## Oracle

```python oracle
def solve(n):
    if n < 3:
        return 0
    sieve = bytearray([1]) * n
    sieve[0:2] = b'\x00\x00'
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, n, i)))
    return sum(sieve)

def gen_random(seed):
    return {"n": random.Random(seed).randint(0, 300)}

def gen_perf(n):
    return {"n": n}
```

## Interviewer notes

- **Target complexity:** O(n log log n) time, O(n) space
- **Scaling check:** sizes [500000, 2000000, 5000000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
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
