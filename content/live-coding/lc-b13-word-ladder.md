---
id: lc-b13-word-ladder
title: Word Ladder
type: live-coding
level: [mid, senior]
tags: [graph, bfs]
time_minutes: 40
entry: ladder_length
kind: func
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

## Signature

```signature
ladder_length(begin_word: string, end_word: string, word_list: string[]) -> int
```

## Tests

```json tests
{"function":"ladder_length","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"begin_word":"hit","end_word":"cog","word_list":["hot","dot","dog","lot","log","cog"]},"expected":5},
{"name":"example-2","tags":["visible"],"args":{"begin_word":"hit","end_word":"cog","word_list":["hot","dot","dog","lot","log"]},"expected":0},
{"name":"edge-one-step","tags":["edge"],"args":{"begin_word":"a","end_word":"b","word_list":["b"]},"expected":2},
{"name":"hidden-shortcut","tags":["hidden"],"args":{"begin_word":"aaa","end_word":"ccc","word_list":["aab","abb","bbb","bbc","bcc","ccc","aac","acc"]},"expected":4},
{"name":"hidden-unreachable","tags":["hidden"],"args":{"begin_word":"abc","end_word":"xyz","word_list":["xyz","abd"]},"expected":0},
{"name":"random-1","tags":["hidden"],"args":{"begin_word":"abc","end_word":"ccc","word_list":["cca","baa","aab","cbb","aba","aaa","cac","cba","acc","bcb","bab"]},"expected":0},
{"name":"random-2","tags":["hidden"],"args":{"begin_word":"bcc","end_word":"acc","word_list":["aac","aba","bbb","caa","cca","cac","ccc"]},"expected":0},
{"name":"random-3","tags":["hidden"],"args":{"begin_word":"acc","end_word":"cbc","word_list":["acb","aba","cab","aab","cbb","bab","aaa","bcb"]},"expected":0},
{"name":"random-4","tags":["hidden"],"args":{"begin_word":"bbc","end_word":"acc","word_list":["aaa","bbb","abc","bba","baa"]},"expected":0}
]}
```

## Reference solution

```python reference
from collections import defaultdict, deque

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
```

## Interviewer notes

- **Target complexity:** O(N * L^2) with wildcard buckets, versus O(N^2 * L) pairwise
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
