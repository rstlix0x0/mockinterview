---
id: lc-b13-word-ladder
title: Word Ladder
type: live-coding
level: [mid, senior]
tags: [graph, bfs]
time_minutes: 40
languages: [python]
entry: ladder_length
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B13
---

# Word Ladder

## Statement

Transform `begin_word` into `end_word` by changing exactly one letter at a time; every intermediate word must be in `word_list` (the begin word does not need to be in it). Return the number of words in the shortest sequence, counting both ends, or `0` if no sequence exists. `end_word` must be in `word_list`. All words have the same length and `begin_word != end_word`.

**Signature:** `ladder_length(begin_word: string, end_word: string, word_list: string[]) -> int`

**Constraints:**
- 1 <= word length <= 10
- up to 20000 words (lowercase)

**Examples:**

- **Example 1** - input: `{"begin_word":"hit","end_word":"cog","word_list":["hot","dot","dog","lot","log","cog"]}`  
  output: `5`
- **Example 2** - input: `{"begin_word":"hit","end_word":"cog","word_list":["hot","dot","dog","lot","log"]}`  
  output: `0`

## Stub

```python
def ladder_length(begin_word, end_word, word_list):
    """ladder_length(begin_word: string, end_word: string, word_list: string[]) -> int"""
    raise NotImplementedError
```

## Signature

```signature
ladder_length(begin_word: string, end_word: string, word_list: string[]) -> int
```

## Tests

```json tests
{"function":"ladder_length","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[5,6,7],"limit_ms":6000,"max_exponent":null},"cases":[
{"name":"example-1","tags":["visible"],"args":{"begin_word":"hit","end_word":"cog","word_list":["hot","dot","dog","lot","log","cog"]}},
{"name":"example-2","tags":["visible"],"args":{"begin_word":"hit","end_word":"cog","word_list":["hot","dot","dog","lot","log"]}},
{"name":"edge-one-step","tags":["edge"],"args":{"begin_word":"a","end_word":"b","word_list":["b"]}},
{"name":"hidden-shortcut","tags":["hidden"],"args":{"begin_word":"aaa","end_word":"ccc","word_list":["aab","abb","bbb","bbc","bcc","ccc","aac","acc"]}},
{"name":"hidden-unreachable","tags":["hidden"],"args":{"begin_word":"abc","end_word":"xyz","word_list":["xyz","abd"]}}
]}
```

## Oracle

```python oracle
def solve(begin_word, end_word, word_list):
    words = set(word_list)
    if end_word not in words:
        return 0
    if begin_word == end_word:
        return 1
    L = len(begin_word)
    buckets = defaultdict(list)
    for w in words | {begin_word}:
        for i in range(L):
            buckets[w[:i] + '*' + w[i + 1:]].append(w)
    dist = {begin_word: 1}
    q = deque([begin_word])
    while q:
        w = q.popleft()
        for i in range(L):
            for nb in buckets[w[:i] + '*' + w[i + 1:]]:
                if nb not in dist:
                    dist[nb] = dist[w] + 1
                    if nb == end_word:
                        return dist[nb]
                    q.append(nb)
    return 0

def gen_random(seed):
    rnd = random.Random(seed)
    L = 3
    allw = [''.join(p) for p in itertools.product("abc", repeat=L)]
    words = rnd.sample(allw, rnd.randint(2, 12))
    b, e = rnd.sample(allw, 2)
    return {"begin_word": b, "end_word": e, "word_list": words}

def gen_perf(n):
    k = n
    words = [''.join(p) for p in itertools.product("abcd", repeat=k)]
    return {"begin_word": "a" * k, "end_word": "d" * k, "word_list": words}
```

## Interviewer notes

- **Target complexity:** O(N * L^2) with wildcard buckets, versus O(N^2 * L) pairwise
- **Scaling check:** sizes [5, 6, 7], limit 6000 ms (calibrated to a straightforward Python solution)
- **Clarifying questions (answer verbatim):**
  - Q: Is the begin word counted?  
    A: Yes: the answer for hit -> hot -> dot -> dog -> cog is 5.
- **Hint ladder:**
  - H0 (free): What is the graph here?
  - H1 (-5): Words are nodes; edges connect words that differ in one position. Shortest path in an unweighted graph.
  - H2 (-10): BFS. Building edges pairwise is O(N^2 * L). Can you group neighbours faster?
  - H3 (-20): Wildcard buckets: 'h*t' groups hot, hit, hat.
- **Follow-ups:**
  - Return one shortest sequence.
  - Return all shortest sequences.
  - Bidirectional BFS.
- **Mistakes the tests are built to catch:**
  - DFS (not shortest).
  - Pairwise neighbour search timing out.
  - Not counting the begin word.
