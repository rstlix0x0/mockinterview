---
id: lc-a14-spiral-matrix
title: Spiral Matrix
type: live-coding
level: [junior]
tags: [matrix, simulation]
time_minutes: 20
languages: [python]
entry: spiral_order
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: A14
---

# Spiral Matrix

## Statement

Return all elements of a rectangular matrix in clockwise spiral order, starting at the top-left cell and moving right first.

**Signature:** `spiral_order(matrix: int[][]) -> int[]`

**Constraints:**
- 0 <= rows, cols <= 1000
- all rows have the same length

**Examples:**

- **Example 1** - input: `{"matrix":[[1,2,3],[4,5,6],[7,8,9]]}`  
  output: `[1,2,3,6,9,8,7,4,5]`
- **Example 2** - input: `{"matrix":[[1,2,3,4],[5,6,7,8],[9,10,11,12]]}`  
  output: `[1,2,3,4,8,12,11,10,9,5,6,7]`

## Stub

```python
def spiral_order(matrix):
    """spiral_order(matrix: int[][]) -> int[]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"spiral_order","kind":"func","compare":"exact","fuzz":25,"perf":{"sizes":[200,500,1000],"limit_ms":4000,"max_exponent":2.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"matrix":[[1,2,3],[4,5,6],[7,8,9]]}},
{"name":"example-2","tags":["visible"],"args":{"matrix":[[1,2,3,4],[5,6,7,8],[9,10,11,12]]}},
{"name":"edge-empty","tags":["edge"],"args":{"matrix":[]}},
{"name":"edge-single-row","tags":["edge"],"args":{"matrix":[[1,2,3]]}},
{"name":"edge-single-col","tags":["edge"],"args":{"matrix":[[1],[2],[3]]}},
{"name":"hidden-two-by-one","tags":["hidden"],"args":{"matrix":[[1],[2]]}}
]}
```

## Oracle

```python oracle
def solve(matrix):
    if not matrix:
        return []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            out.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            out.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                out.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])
            left += 1
    return out

def gen_random(seed):
    rnd = random.Random(seed)
    r, c = rnd.randint(1, 5), rnd.randint(1, 5)
    return {"matrix": [[rnd.randint(0, 99) for _ in range(c)] for _ in range(r)]}

def gen_perf(n):
    return {"matrix": [list(range(i * n, i * n + n)) for i in range(n)]}
```

## Interviewer notes

- **Target complexity:** O(rows * cols)
- **Scaling check:** sizes [200, 500, 1000], limit 4000 ms (calibrated to a straightforward Python solution), growth exponent at most 2.4
- **Clarifying questions (answer verbatim):**
  - Q: Is a matrix with zero columns possible?  
    A: Treat `[]` as the only empty case.
- **Hint ladder:**
  - H0 (free): What defines the current boundary?
  - H1 (-5): Four boundaries: top, bottom, left, right.
  - H2 (-10): After each side, shrink the matching boundary.
  - H3 (-20): Re-check the boundaries before the 3rd and 4th side, otherwise single rows/columns repeat.
- **Follow-ups:**
  - Generate an n x n spiral matrix.
  - Counter-clockwise from the centre.
- **Mistakes the tests are built to catch:**
  - Duplicate output on single-row or single-column matrices.
  - Not guarding the empty matrix.
