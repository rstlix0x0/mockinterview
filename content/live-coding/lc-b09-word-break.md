---
id: lc-b09-word-break
title: Word Break
type: live-coding
level: [junior, mid]
tags: [dynamic-programming, strings]
time_minutes: 25
languages: [python]
entry: word_break
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B9
---

# Word Break

## Statement

Return `true` if the non-empty string `s` can be split into a sequence of one or more words from `word_dict` (words may be reused).

**Signature:** `word_break(s: string, word_dict: string[]) -> bool`

**Constraints:**
- 1 <= len(s) <= 5000
- 1 <= len(word_dict) <= 1000
- words are non-empty

**Examples:**

- **Example 1** - input: `{"s":"leetcode","word_dict":["leet","code"]}`  
  output: `true`
- **Example 2** - input: `{"s":"catsandog","word_dict":["cats","dog","sand","and","cat"]}`  
  output: `false`

## Stub

```python
def word_break(s, word_dict):
    """word_break(s: string, word_dict: string[]) -> bool"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"word_break","kind":"func","compare":"exact","fuzz":20,"perf":{"sizes":[30,1000,5000],"limit_ms":3000,"max_exponent":2.2},"cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"leetcode","word_dict":["leet","code"]}},
{"name":"example-2","tags":["visible"],"args":{"s":"catsandog","word_dict":["cats","dog","sand","and","cat"]}},
{"name":"edge-single-char","tags":["edge"],"args":{"s":"a","word_dict":["a"]}},
{"name":"edge-no-words-match","tags":["edge"],"args":{"s":"abc","word_dict":["d"]}},
{"name":"hidden-reuse","tags":["hidden"],"args":{"s":"aaaa","word_dict":["a","aa"]}},
{"name":"hidden-overlap-trap","tags":["hidden"],"args":{"s":"aaaaab","word_dict":["a","aa","aaa","aaaa","b"]}}
]}
```

## Oracle

```python oracle
def solve(s, word_dict):
    words = set(word_dict)
    lens = sorted({len(w) for w in words})
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for L in lens:
            if L > i:
                break
            if dp[i - L] and s[i - L:i] in words:
                dp[i] = True
                break
    return dp[len(s)]

def gen_random(seed):
    rnd = random.Random(seed)
    words = list({''.join(rnd.choice("ab") for _ in range(rnd.randint(1, 3))) for _ in range(rnd.randint(1, 4))})
    return {"s": ''.join(rnd.choice("ab") for _ in range(rnd.randint(1, 10))), "word_dict": words}

def gen_perf(n):
    return {"s": 'a' * n + 'b', "word_dict": ['a', 'aa', 'aaa', 'aaaa', 'aaaaa', 'aaaaaa']}
```

## Interviewer notes

- **Target complexity:** O(n * L) with L the number of distinct word lengths
- **Scaling check:** sizes [30, 1000, 5000], limit 3000 ms (calibrated to a straightforward Python solution), growth exponent at most 2.2
- **Clarifying questions (answer verbatim):**
  - Q: Can words overlap?  
    A: No. It is a partition of s.
- **Hint ladder:**
  - H0 (free): What makes naive recursion exponential?
  - H1 (-5): The same suffix is solved repeatedly.
  - H2 (-10): dp[i] = can the prefix of length i be segmented?
  - H3 (-20): Only try word lengths that exist in the dictionary.
- **Follow-ups:**
  - Return all segmentations.
  - Return the segmentation with the fewest words.
- **Mistakes the tests are built to catch:**
  - No memoization: the 'aaaa...b' test never finishes.
  - Slicing strings in an O(n^3) way.
  - Off-by-one on dp[0].
