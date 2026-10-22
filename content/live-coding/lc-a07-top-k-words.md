---
id: lc-a07-top-k-words
title: Top K Words
type: live-coding
level: [junior]
tags: [hash-map, sorting, strings]
time_minutes: 15
entry: top_words
kind: func
source: adapted
author: mockinterview
legacy_id: A7
---

# Top K Words

## Statement

Tokenize `text` into words after lowercasing: a word is a maximal run of characters from `a-z`, `0-9` and the apostrophe `'`. Everything else separates words. Return the `k` most frequent words as `[word, count]` pairs, ordered by count descending and then word ascending. Return fewer than `k` pairs if there are fewer distinct words.

**Signature:** `top_words(text: string, k: int) -> [string, int][]`

**Constraints:**
- 0 <= len(text) <= 1000000
- 0 <= k <= 1000

**Examples:**

- **Example 1** - input: `{"text":"The cat and the hat. The end!","k":2}`  
  output: `[["the",3],["and",1]]`
- **Example 2** - input: `{"text":"it's it's its","k":5}`  
  output: `[["it's",2],["its",1]]`

## Signature

```signature
top_words(text: string, k: int) -> [string, int][]
```

## Tests

```json tests
{"function":"top_words","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"text":"The cat and the hat. The end!","k":2},"expected":[["the",3],["and",1]]},
{"name":"example-2","tags":["visible"],"args":{"text":"it's it's its","k":5},"expected":[["it's",2],["its",1]]},
{"name":"edge-empty-text","tags":["edge"],"args":{"text":"","k":3},"expected":[]},
{"name":"edge-k-zero","tags":["edge"],"args":{"text":"a b c","k":0},"expected":[]},
{"name":"hidden-tie-break","tags":["hidden"],"args":{"text":"b a c b a c","k":3},"expected":[["a",2],["b",2],["c",2]]},
{"name":"hidden-digits-punct","tags":["hidden"],"args":{"text":"x1,x1;X2 ... x1","k":2},"expected":[["x1",3],["x2",1]]},
{"name":"hidden-non-ascii-separates","tags":["hidden"],"args":{"text":"café cafe","k":5},"expected":[["caf",1],["cafe",1]]},
{"name":"random-1","tags":["hidden"],"args":{"text":"it's the a the the it's x1 Cat a","k":4},"expected":[["the",3],["a",2],["it's",2],["cat",1]]},
{"name":"random-2","tags":["hidden"],"args":{"text":"a a THE THE a","k":4},"expected":[["a",3],["the",2]]},
{"name":"random-3","tags":["hidden"],"args":{"text":"dog a the x1 the it's","k":1},"expected":[["the",2]]},
{"name":"random-4","tags":["hidden"],"args":{"text":"the THE Cat","k":3},"expected":[["the",2],["cat",1]]}
]}
```

## Reference solution

```python reference
import re
from collections import Counter

def solve(text, k):
    words = re.findall(r"[a-z0-9']+", text.lower())
    c = Counter(words)
    ranked = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    return [[w, n] for w, n in ranked[:k]]
```

## Interviewer notes

- **Target complexity:** O(n + d log d) for d distinct words
- **Clarifying questions (answer verbatim):**
  - Q: What about non-ASCII letters?  
    A: They are separators.
  - Q: Is the apostrophe part of a word?  
    A: Yes.
- **Hint ladder:**
  - H0 (free): What are the two phases?
  - H1 (-5): Count, then rank.
  - H2 (-10): Rank with a composite key: (-count, word).
  - H3 (-20): For huge d use a heap of size k.
- **Follow-ups:**
  - Stream the text and keep memory O(d).
  - Use a size-k heap to get O(n + d log k).
- **Mistakes the tests are built to catch:**
  - Forgetting the alphabetical tie-break.
  - Splitting only on spaces.
  - Locale-dependent lowercasing.
