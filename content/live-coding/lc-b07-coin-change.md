---
id: lc-b07-coin-change
title: Coin Change (Fewest Coins)
type: live-coding
level: [junior, mid]
tags: [dynamic-programming]
time_minutes: 25
languages: [python]
entry: coin_change
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B7
---

# Coin Change (Fewest Coins)

## Statement

Given distinct positive coin denominations and a target `amount`, return the fewest coins that sum exactly to `amount`, or `-1` if impossible. Each coin may be used any number of times. `amount = 0` needs 0 coins.

**Signature:** `coin_change(coins: int[], amount: int) -> int`

**Constraints:**
- 1 <= len(coins) <= 12
- 1 <= coin <= 10^4
- 0 <= amount <= 100000

**Examples:**

- **Example 1** - input: `{"coins":[1,2,5],"amount":11}`  
  output: `3`
- **Example 2** - input: `{"coins":[2],"amount":3}`  
  output: `-1`
- **Example 3** - input: `{"coins":[1],"amount":0}`  
  output: `0`

## Stub

```python
def coin_change(coins, amount):
    """coin_change(coins: int[], amount: int) -> int"""
    raise NotImplementedError
```

## Signature

```signature
coin_change(coins: int[], amount: int) -> int
```

## Tests

```json tests
{"function":"coin_change","kind":"func","compare":"exact","fuzz":15,"perf":{"sizes":[10000,50000,100000],"limit_ms":4000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"coins":[1,2,5],"amount":11}},
{"name":"example-2","tags":["visible"],"args":{"coins":[2],"amount":3}},
{"name":"example-3","tags":["visible"],"args":{"coins":[1],"amount":0}},
{"name":"edge-impossible-big","tags":["edge"],"args":{"coins":[5,10],"amount":3}},
{"name":"hidden-greedy-fails","tags":["hidden"],"args":{"coins":[1,3,4],"amount":6}},
{"name":"hidden-large-coin","tags":["hidden"],"args":{"coins":[7,3],"amount":14}},
{"name":"hidden-unreachable","tags":["hidden"],"args":{"coins":[3,5],"amount":7}}
]}
```

## Oracle

```python oracle
def solve(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for c in coins:
        for a in range(c, amount + 1):
            if dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] < INF else -1

def gen_random(seed):
    rnd = random.Random(seed)
    return {"coins": rnd.sample(range(1, 10), rnd.randint(1, 4)), "amount": rnd.randint(0, 25)}

def gen_perf(n):
    return {"coins": [1, 5, 10, 25, 100, 331, 997], "amount": n}
```

## Interviewer notes

- **Target complexity:** O(amount * len(coins)) time, O(amount) space
- **Scaling check:** sizes [10000, 50000, 100000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: Is greedy acceptable?  
    A: Only if you can prove it. Try coins [1,3,4] and amount 6.
- **Hint ladder:**
  - H0 (free): Does the greedy choice always work?
  - H1 (-5): Define best(a) = fewest coins for amount a.
  - H2 (-10): best(a) = 1 + min(best(a - c)) over coins c <= a.
  - H3 (-20): Bottom-up array of size amount + 1 initialised to 'infinity'; best(0) = 0.
- **Follow-ups:**
  - Count the number of distinct combinations.
  - Each coin is available only once.
- **Mistakes the tests are built to catch:**
  - Greedy.
  - Using INT_MAX and overflowing on +1.
  - Plain recursion without memoization.
