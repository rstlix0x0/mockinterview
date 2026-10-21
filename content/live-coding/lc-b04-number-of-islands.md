---
id: lc-b04-number-of-islands
title: Number of Islands
type: live-coding
level: [junior, mid]
tags: [graph, dfs, bfs, grid]
time_minutes: 25
languages: [python]
entry: num_islands
kind: func
runs_code: true
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

## Stub

```python
def num_islands(grid):
    """num_islands(grid: string[]) -> int"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"num_islands","kind":"func","compare":"exact","fuzz":15,"perf":{"sizes":[200,500,1000],"limit_ms":6000,"max_exponent":2.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"grid":["11000","11000","00100","00011"]}},
{"name":"example-2","tags":["visible"],"args":{"grid":["101","010","101"]}},
{"name":"edge-empty","tags":["edge"],"args":{"grid":[]}},
{"name":"edge-all-water","tags":["edge"],"args":{"grid":["000","000"]}},
{"name":"edge-all-land","tags":["edge"],"args":{"grid":["111","111"]}},
{"name":"hidden-diagonal-not-connected","tags":["hidden"],"args":{"grid":["10","01"]}},
{"name":"hidden-spiral","tags":["hidden"],"args":{"grid":["11111","00001","11101","10001","11111"]}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    r, c = rnd.randint(1, 5), rnd.randint(1, 5)
    return {"grid": [''.join(rnd.choice("01") for _ in range(c)) for _ in range(r)]}

def gen_perf(n):
    return {"grid": ['1' * n for _ in range(n)]}
```

## Interviewer notes

- **Target complexity:** O(R * C) time and space
- **Scaling check:** sizes [200, 500, 1000], limit 6000 ms (calibrated to a straightforward Python solution), growth exponent at most 2.4
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
