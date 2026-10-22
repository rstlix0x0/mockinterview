---
id: lc-b07-coin-change
title: Coin Change (Fewest Coins)
type: live-coding
level: [junior, mid]
tags: [dynamic-programming]
time_minutes: 25
entry: coin_change
kind: func
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

## Signature

```signature
coin_change(coins: int[], amount: int) -> int
```

## Tests

```json tests
{"function":"coin_change","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"coins":[1,2,5],"amount":11},"expected":3},
{"name":"example-2","tags":["visible"],"args":{"coins":[2],"amount":3},"expected":-1},
{"name":"example-3","tags":["visible"],"args":{"coins":[1],"amount":0},"expected":0},
{"name":"edge-impossible-big","tags":["edge"],"args":{"coins":[5,10],"amount":3},"expected":-1},
{"name":"hidden-greedy-fails","tags":["hidden"],"args":{"coins":[1,3,4],"amount":6},"expected":2},
{"name":"hidden-large-coin","tags":["hidden"],"args":{"coins":[7,3],"amount":14},"expected":2},
{"name":"hidden-unreachable","tags":["hidden"],"args":{"coins":[3,5],"amount":7},"expected":-1},
{"name":"random-1","tags":["hidden"],"args":{"coins":[1,2,6],"amount":0},"expected":0},
{"name":"random-2","tags":["hidden"],"args":{"coins":[2,9,4],"amount":18},"expected":2},
{"name":"random-3","tags":["hidden"],"args":{"coins":[4,2,5,1],"amount":22},"expected":5},
{"name":"random-4","tags":["hidden"],"args":{"coins":[1,7],"amount":5},"expected":5}
]}
```

## Reference solution

```python reference
def solve(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for c in coins:
        for a in range(c, amount + 1):
            if dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] < INF else -1
```

## Interviewer notes

- **Target complexity:** O(amount * len(coins)) time, O(amount) space
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
