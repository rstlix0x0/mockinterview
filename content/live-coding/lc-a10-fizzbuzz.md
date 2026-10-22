---
id: lc-a10-fizzbuzz
title: FizzBuzz
type: live-coding
level: [junior]
tags: [loops, strings]
time_minutes: 10
entry: fizz_buzz
kind: func
source: adapted
author: mockinterview
legacy_id: A10
---

# FizzBuzz

## Statement

Return a list of `n` strings for the numbers `1..n`: `"Fizz"` for multiples of 3, `"Buzz"` for multiples of 5, `"FizzBuzz"` for multiples of both, otherwise the number as a string.

**Signature:** `fizz_buzz(n: int) -> string[]`

**Constraints:**
- 0 <= n <= 1000000

**Examples:**

- **Example 1** - input: `{"n":5}`  
  output: `["1","2","Fizz","4","Buzz"]`
- **Example 2** - input: `{"n":15}`  
  output: `["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]`

## Signature

```signature
fizz_buzz(n: int) -> string[]
```

## Tests

```json tests
{"function":"fizz_buzz","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"n":5},"expected":["1","2","Fizz","4","Buzz"]},
{"name":"example-2","tags":["visible"],"args":{"n":15},"expected":["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]},
{"name":"edge-zero","tags":["edge"],"args":{"n":0},"expected":[]},
{"name":"edge-one","tags":["edge"],"args":{"n":1},"expected":["1"]},
{"name":"hidden-30","tags":["hidden"],"args":{"n":30},"expected":["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz","16","17","Fizz","19","Buzz","Fizz","22","23","Fizz","Buzz","26","Fizz","28","29","FizzBuzz"]},
{"name":"random-1","tags":["hidden"],"args":{"n":2},"expected":["1","2"]},
{"name":"random-2","tags":["hidden"],"args":{"n":3},"expected":["1","2","Fizz"]},
{"name":"random-3","tags":["hidden"],"args":{"n":4},"expected":["1","2","Fizz","4"]},
{"name":"random-4","tags":["hidden"],"args":{"n":6},"expected":["1","2","Fizz","4","Buzz","Fizz"]}
]}
```

## Reference solution

```python reference
def solve(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
```

## Interviewer notes

- **Target complexity:** O(n)
- **Clarifying questions (answer verbatim):**
  - Q: Is n = 0 valid?  
    A: Yes: return an empty list.
- **Hint ladder:**
  - H0 (free): Which multiple must be tested first?
  - H1 (-5): 15 (or both conditions) before 3 and 5.
  - H2 (-10): Build the list in one pass.
  - H3 (-20): Convert numbers with the language's integer-to-string function.
- **Follow-ups:**
  - Make the rules configurable: a list of (divisor, word) pairs.
  - Stream the output instead of building a list.
- **Mistakes the tests are built to catch:**
  - Testing 3 before 15.
  - Off-by-one on the range.
  - Returning numbers instead of strings.
