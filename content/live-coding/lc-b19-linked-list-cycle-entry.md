---
id: lc-b19-linked-list-cycle-entry
title: Linked List Cycle Entry
type: live-coding
level: [junior, mid]
tags: [linked-list, two-pointers]
time_minutes: 25
entry: cycle_start
kind: func
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

## Signature

```signature
cycle_start(next_idx: int[]) -> int
```

## Tests

```json tests
{"function":"cycle_start","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"next_idx":[1,2,3,1]},"expected":1},
{"name":"example-2","tags":["visible"],"args":{"next_idx":[1,-1]},"expected":-1},
{"name":"example-3","tags":["visible"],"args":{"next_idx":[0]},"expected":0},
{"name":"edge-empty","tags":["edge"],"args":{"next_idx":[]},"expected":-1},
{"name":"edge-single-no-cycle","tags":["edge"],"args":{"next_idx":[-1]},"expected":-1},
{"name":"edge-cycle-at-head","tags":["edge"],"args":{"next_idx":[1,2,0]},"expected":0},
{"name":"hidden-long-tail","tags":["hidden"],"args":{"next_idx":[1,2,3,4,5,3]},"expected":3},
{"name":"random-1","tags":["hidden"],"args":{"next_idx":[1,2,3,4,5,6,7,8,-1]},"expected":-1},
{"name":"random-2","tags":["hidden"],"args":{"next_idx":[1,2,3,4,-1]},"expected":-1},
{"name":"random-3","tags":["hidden"],"args":{"next_idx":[1,2,3,4,5,-1]},"expected":-1},
{"name":"random-4","tags":["hidden"],"args":{"next_idx":[1,2,3,4,5,6,7,-1]},"expected":-1}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(n) time, O(1) space
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
