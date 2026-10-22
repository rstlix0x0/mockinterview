---
id: lc-b04-number-of-islands
title: Number of Islands
type: live-coding
level: [junior, mid]
tags: [graph, dfs, bfs, grid]
time_minutes: 25
entry: num_islands
kind: func
source: adapted
author: mockinterview
legacy_id: B4
---

# Number of Islands

## Statement

`grid` is a list of equal-length strings of `'0'` (water) and `'1'` (land). Count the islands: maximal groups of land cells connected horizontally or vertically.

**Signature:** `num_islands(grid: string[]) -> int`

**Constraints:**
- 0 <= rows, cols <= 1000
- the grid can be a single 1000 x 1000 island

**Examples:**

- **Example 1** - input: `{"grid":["11000","11000","00100","00011"]}`  
  output: `3`
- **Example 2** - input: `{"grid":["101","010","101"]}`  
  output: `5`

## Signature

```signature
num_islands(grid: string[]) -> int
```

## Tests

```json tests
{"function":"num_islands","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"grid":["11000","11000","00100","00011"]},"expected":3},
{"name":"example-2","tags":["visible"],"args":{"grid":["101","010","101"]},"expected":5},
{"name":"edge-empty","tags":["edge"],"args":{"grid":[]},"expected":0},
{"name":"edge-all-water","tags":["edge"],"args":{"grid":["000","000"]},"expected":0},
{"name":"edge-all-land","tags":["edge"],"args":{"grid":["111","111"]},"expected":1},
{"name":"hidden-diagonal-not-connected","tags":["hidden"],"args":{"grid":["10","01"]},"expected":2},
{"name":"hidden-spiral","tags":["hidden"],"args":{"grid":["11111","00001","11101","10001","11111"]},"expected":1},
{"name":"random-1","tags":["hidden"],"args":{"grid":["000","011","001","010","001"]},"expected":3},
{"name":"random-2","tags":["hidden"],"args":{"grid":["0","1","1"]},"expected":1},
{"name":"random-3","tags":["hidden"],"args":{"grid":["00","10","10","10"]},"expected":1},
{"name":"random-4","tags":["hidden"],"args":{"grid":["1","0"]},"expected":1}
]}
```

## Reference solution

```python reference
def solve(grid):
    if not grid:
        return 0
    R, C = len(grid), len(grid[0])
    seen = [[False] * C for _ in range(R)]
    count = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == '1' and not seen[r][c]:
                count += 1
                seen[r][c] = True
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < R and 0 <= ny < C and grid[nx][ny] == '1' and not seen[nx][ny]:
                            seen[nx][ny] = True
                            stack.append((nx, ny))
    return count
```

## Interviewer notes

- **Target complexity:** O(R * C) time and space
- **Clarifying questions (answer verbatim):**
  - Q: Are diagonals connected?  
    A: No.
  - Q: May I modify the grid?  
    A: Treat the input as read-only unless you copy it.
- **Hint ladder:**
  - H0 (free): How do you avoid counting a land cell twice?
  - H1 (-5): Flood fill from each unvisited land cell.
  - H2 (-10): BFS or DFS with a visited set; count one per fresh start.
  - H3 (-20): A 1000 x 1000 single island makes naive recursion 10^6 deep. Use an explicit stack or queue.
- **Follow-ups:**
  - Largest island area.
  - Count islands under a stream of 'add land' operations (union-find).
- **Mistakes the tests are built to catch:**
  - Recursive DFS overflowing the stack on a huge island.
  - Counting diagonals.
  - Forgetting visited marks and looping forever.
