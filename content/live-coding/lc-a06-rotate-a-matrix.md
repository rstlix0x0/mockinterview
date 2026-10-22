---
id: lc-a06-rotate-a-matrix
title: Rotate a Matrix
type: live-coding
level: [junior]
tags: [matrix, indices]
time_minutes: 15
entry: rotate_matrix
kind: func
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

## Signature

```signature
rotate_matrix(matrix: int[][]) -> int[][]
```

## Tests

```json tests
{"function":"rotate_matrix","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"matrix":[[1,2],[3,4]]},"expected":[[3,1],[4,2]]},
{"name":"example-2","tags":["visible"],"args":{"matrix":[[1,2,3],[4,5,6]]},"expected":[[4,1],[5,2],[6,3]]},
{"name":"edge-empty","tags":["edge"],"args":{"matrix":[]},"expected":[]},
{"name":"edge-single","tags":["edge"],"args":{"matrix":[[7]]},"expected":[[7]]},
{"name":"edge-one-row","tags":["edge"],"args":{"matrix":[[1,2,3]]},"expected":[[1],[2],[3]]},
{"name":"edge-one-col","tags":["edge"],"args":{"matrix":[[1],[2],[3]]},"expected":[[3,2,1]]},
{"name":"hidden-square-4","tags":["hidden"],"args":{"matrix":[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]},"expected":[[13,9,5,1],[14,10,6,2],[15,11,7,3],[16,12,8,4]]},
{"name":"hidden-wide","tags":["hidden"],"args":{"matrix":[[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15]]},"expected":[[11,6,1],[12,7,2],[13,8,3],[14,9,4],[15,10,5]]},
{"name":"random-1","tags":["hidden"],"args":{"matrix":[[1],[0],[0]]},"expected":[[0,0,1]]},
{"name":"random-2","tags":["hidden"],"args":{"matrix":[[1],[6],[9]]},"expected":[[9,6,1]]},
{"name":"random-3","tags":["hidden"],"args":{"matrix":[[1,9],[0,5],[0,8],[4,3]]},"expected":[[4,0,0,1],[3,8,5,9]]},
{"name":"random-4","tags":["hidden"],"args":{"matrix":[[6],[2]]},"expected":[[2,6]]}
]}
```

## Reference solution

```python reference
def solve(matrix):
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix[::-1])]
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
