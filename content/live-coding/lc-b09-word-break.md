---
id: lc-b09-word-break
title: Word Break
type: live-coding
level: [junior, mid]
tags: [dynamic-programming, strings]
time_minutes: 25
entry: word_break
kind: func
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

## Signature

```signature
word_break(s: string, word_dict: string[]) -> bool
```

## Tests

```json tests
{"function":"word_break","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"s":"leetcode","word_dict":["leet","code"]},"expected":true},
{"name":"example-2","tags":["visible"],"args":{"s":"catsandog","word_dict":["cats","dog","sand","and","cat"]},"expected":false},
{"name":"edge-single-char","tags":["edge"],"args":{"s":"a","word_dict":["a"]},"expected":true},
{"name":"edge-no-words-match","tags":["edge"],"args":{"s":"abc","word_dict":["d"]},"expected":false},
{"name":"hidden-reuse","tags":["hidden"],"args":{"s":"aaaa","word_dict":["a","aa"]},"expected":true},
{"name":"hidden-overlap-trap","tags":["hidden"],"args":{"s":"aaaaab","word_dict":["a","aa","aaa","aaaa","b"]},"expected":true},
{"name":"random-1","tags":["hidden"],"args":{"s":"babaaabbaa","word_dict":["baa","a","aab"]},"expected":false},
{"name":"random-2","tags":["hidden"],"args":{"s":"abbaa","word_dict":["baa","ba","a"]},"expected":false},
{"name":"random-3","tags":["hidden"],"args":{"s":"abaaa","word_dict":["bab","abb","a","aba"]},"expected":true},
{"name":"random-4","tags":["hidden"],"args":{"s":"bbbbaba","word_dict":["b"]},"expected":false}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(n * L) with L the number of distinct word lengths
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
