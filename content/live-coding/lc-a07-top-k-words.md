---
id: lc-a07-top-k-words
title: Top K Words
type: live-coding
level: [junior]
tags: [hash-map, sorting, strings]
time_minutes: 15
languages: [python]
entry: top_words
kind: func
runs_code: true
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

## Stub

```python
def top_words(text, k):
    """top_words(text: string, k: int) -> [string, int][]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"top_words","kind":"func","compare":"exact","fuzz":6,"cases":[
{"name":"example-1","tags":["visible"],"args":{"text":"The cat and the hat. The end!","k":2}},
{"name":"example-2","tags":["visible"],"args":{"text":"it's it's its","k":5}},
{"name":"edge-empty-text","tags":["edge"],"args":{"text":"","k":3}},
{"name":"edge-k-zero","tags":["edge"],"args":{"text":"a b c","k":0}},
{"name":"hidden-tie-break","tags":["hidden"],"args":{"text":"b a c b a c","k":3}},
{"name":"hidden-digits-punct","tags":["hidden"],"args":{"text":"x1,x1;X2 ... x1","k":2}},
{"name":"hidden-non-ascii-separates","tags":["hidden"],"args":{"text":"café cafe","k":5}}
]}
```

## Oracle

```python oracle
def solve(text, k):
    words = re.findall(r"[a-z0-9']+", text.lower())
    c = Counter(words)
    ranked = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    return [[w, n] for w, n in ranked[:k]]

def gen_random(seed):
    rnd = random.Random(seed)
    vocab = ["the", "a", "Cat", "dog", "it's", "x1", "THE", "dog."]
    return {"text": ' '.join(rnd.choice(vocab) for _ in range(rnd.randint(0, 12))), "k": rnd.randint(0, 4)}
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
