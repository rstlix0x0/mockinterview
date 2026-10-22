---
id: lc-b19-linked-list-cycle-entry
title: Linked List Cycle Entry
type: live-coding
level: [junior, mid]
tags: [linked-list, two-pointers]
time_minutes: 25
languages: [python]
entry: cycle_start
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: B19
---

# Linked List Cycle Entry

## Statement

A singly linked list is described by `next_idx`: node `i` points to node `next_idx[i]` (`-1` means no next node). Node `0` is the head. Return the index of the node where a cycle begins (the first node you would visit twice when walking from the head), or `-1` if the list ends. An empty array is an empty list. In an interview you would be given node objects; here, build real nodes from the array yourself if you want practice, and solve it with O(1) extra space (Floyd's tortoise and hare).

**Signature:** `cycle_start(next_idx: int[]) -> int`

**Constraints:**
- 0 <= len(next_idx) <= 1000000

**Examples:**

- **Example 1** - input: `{"next_idx":[1,2,3,1]}`  
  output: `1`
- **Example 2** - input: `{"next_idx":[1,-1]}`  
  output: `-1`
- **Example 3** - input: `{"next_idx":[0]}`  
  output: `0`

## Stub

```python
def cycle_start(next_idx):
    """cycle_start(next_idx: int[]) -> int"""
    raise NotImplementedError
```

## Signature

```signature
cycle_start(next_idx: int[]) -> int
```

## Tests

```json tests
{"function":"cycle_start","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[100000,500000,1000000],"limit_ms":4000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"next_idx":[1,2,3,1]}},
{"name":"example-2","tags":["visible"],"args":{"next_idx":[1,-1]}},
{"name":"example-3","tags":["visible"],"args":{"next_idx":[0]}},
{"name":"edge-empty","tags":["edge"],"args":{"next_idx":[]}},
{"name":"edge-single-no-cycle","tags":["edge"],"args":{"next_idx":[-1]}},
{"name":"edge-cycle-at-head","tags":["edge"],"args":{"next_idx":[1,2,0]}},
{"name":"hidden-long-tail","tags":["hidden"],"args":{"next_idx":[1,2,3,4,5,3]}}
]}
```

## Oracle

```python oracle
def solve(next_idx):
    seen, cur = set(), 0
    if not next_idx:
        return -1
    while cur != -1:
        if cur in seen:
            return cur
        seen.add(cur)
        cur = next_idx[cur]
    return -1

def gen_random(seed):
    rnd = random.Random(seed)
    n = rnd.randint(0, 9)
    nxt = [i + 1 for i in range(n)]
    if n:
        nxt[-1] = rnd.choice([-1, rnd.randrange(n)])
    return {"next_idx": nxt}

def gen_perf(n):
    nxt = [i + 1 for i in range(n)]
    nxt[-1] = n // 2
    return {"next_idx": nxt}
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
- **Scaling check:** sizes [100000, 500000, 1000000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Can the structure branch?  
    A: No: every node has at most one next.
- **Hint ladder:**
  - H0 (free): A visited set works. What does it cost in memory?
  - H1 (-5): Two pointers at different speeds.
  - H2 (-10): If they meet there is a cycle; where do you restart one pointer?
  - H3 (-20): After they meet, restart one pointer at the head; advance both one step at a time: they meet at the entry.
- **Follow-ups:**
  - Return the cycle length.
  - Find the middle of a list in one pass.
- **Mistakes the tests are built to catch:**
  - Only detecting the cycle, not the entry.
  - Null-pointer errors when `fast.next` is missing.
