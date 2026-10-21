---
id: lc-a06-rotate-a-matrix
title: Rotate a Matrix
type: live-coding
level: [junior]
tags: [matrix, indices]
time_minutes: 15
languages: [python]
entry: rotate_matrix
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: A6
---

# Rotate a Matrix

## Statement

Return a new matrix that is the input rotated 90 degrees clockwise. The matrix may be non-square: an `r x c` input becomes `c x r`. An empty matrix returns an empty matrix.

**Signature:** `rotate_matrix(matrix: int[][]) -> int[][]`

**Constraints:**
- 0 <= rows, cols <= 1000

**Examples:**

- **Example 1** - input: `{"matrix":[[1,2],[3,4]]}`  
  output: `[[3,1],[4,2]]`
- **Example 2** - input: `{"matrix":[[1,2,3],[4,5,6]]}`  
  output: `[[4,1],[5,2],[6,3]]`

## Stub

```python
def rotate_matrix(matrix):
    """rotate_matrix(matrix: int[][]) -> int[][]"""
    raise NotImplementedError
```

## Tests

```json tests
{"function":"rotate_matrix","kind":"func","compare":"exact","fuzz":6,"cases":[
{"name":"example-1","tags":["visible"],"args":{"matrix":[[1,2],[3,4]]}},
{"name":"example-2","tags":["visible"],"args":{"matrix":[[1,2,3],[4,5,6]]}},
{"name":"edge-empty","tags":["edge"],"args":{"matrix":[]}},
{"name":"edge-single","tags":["edge"],"args":{"matrix":[[7]]}},
{"name":"edge-one-row","tags":["edge"],"args":{"matrix":[[1,2,3]]}},
{"name":"edge-one-col","tags":["edge"],"args":{"matrix":[[1],[2],[3]]}},
{"name":"hidden-square-4","tags":["hidden"],"args":{"matrix":[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]}},
{"name":"hidden-wide","tags":["hidden"],"args":{"matrix":[[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15]]}}
]}
```

## Oracle

```python oracle
def solve(matrix):
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix[::-1])]

def gen_random(seed):
    rnd = random.Random(seed)
    r, c = rnd.randint(1, 4), rnd.randint(1, 4)
    return {"matrix": [[rnd.randint(0, 9) for _ in range(c)] for _ in range(r)]}
```

## Interviewer notes

- **Target complexity:** O(r * c) time and space
- **Clarifying questions (answer verbatim):**
  - Q: In place?  
    A: Return a new matrix here. As a follow-up, do the square case in place.
- **Hint ladder:**
  - H0 (free): Where does element (i, j) of the input end up?
  - H1 (-5): In an r x c input it moves to row j, column r-1-i.
  - H2 (-10): Allocate the c x r output and fill it with that formula.
  - H3 (-20): Check the 1xN and Nx1 shapes.
- **Follow-ups:**
  - Rotate a square matrix in place using O(1) extra space.
  - Rotate counter-clockwise.
- **Mistakes the tests are built to catch:**
  - Assuming a square matrix.
  - Swapping the dimensions of the output.
