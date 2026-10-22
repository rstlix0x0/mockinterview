---
id: lc-c04-task-scheduler
title: Task Scheduler with Dependencies and Workers
type: live-coding
level: [senior, staff]
tags: [graph, simulation, heap]
time_minutes: 45
entry: schedule_tasks
kind: func
source: adapted
author: mockinterview
legacy_id: C4
---

# Task Scheduler with Dependencies and Workers

## Statement

`tasks` is a list of `{id, duration, deps}`. A task can start only after every task in `deps` has **finished**. There are `workers` identical workers; each runs one task at a time and tasks are not preempted. Simulate the schedule:

1. Time starts at 0. Whenever a worker is free and a task is ready, start the ready task with the **smallest id** (plain string comparison).
2. At a given instant, all tasks that finish at that instant free their workers and release their dependants **before** new tasks are assigned.

Return `{"makespan": T, "starts": {id: start_time}}` where `T` is the time the last task finishes (0 when there are no tasks). Error handling, checked in this order:

- any dependency names an unknown task: `{"error": "unknown_dependency"}`
- the dependency graph has a cycle (a self-dependency counts): `{"error": "cycle"}`

**Signature:** `schedule_tasks(tasks: {id: string, duration: int, deps: string[]}[], workers: int) -> object`

**Constraints:**
- 0 <= len(tasks) <= 50000
- 1 <= duration <= 10^6
- 1 <= workers <= 1000
- ids are unique; deps may repeat

**Examples:**

- **Example 1** - input: `{"tasks":[{"id":"a","duration":3,"deps":[]},{"id":"b","duration":2,"deps":["a"]},{"id":"c","duration":4,"deps":["a"]}],"workers":2}`  
  output: `{"makespan":7,"starts":{"a":0,"b":3,"c":3}}`
- **Example 2** - input: `{"tasks":[{"id":"x","duration":1,"deps":["y"]},{"id":"y","duration":1,"deps":["x"]}],"workers":1}`  
  output: `{"error":"cycle"}`

## Signature

```signature
schedule_tasks(tasks: record{id: string, duration: int, deps: string[]}[], workers: int) -> record{makespan?: int, starts?: {string: int}, error?: string}
```

## Tests

```json tests
{"function":"schedule_tasks","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"tasks":[{"id":"a","duration":3,"deps":[]},{"id":"b","duration":2,"deps":["a"]},{"id":"c","duration":4,"deps":["a"]}],"workers":2},"expected":{"makespan":7,"starts":{"a":0,"b":3,"c":3}}},
{"name":"example-2","tags":["visible"],"args":{"tasks":[{"id":"x","duration":1,"deps":["y"]},{"id":"y","duration":1,"deps":["x"]}],"workers":1},"expected":{"error":"cycle"}},
{"name":"edge-empty","tags":["edge"],"args":{"tasks":[],"workers":3},"expected":{"makespan":0,"starts":{}}},
{"name":"edge-unknown-dep","tags":["edge"],"args":{"tasks":[{"id":"a","duration":1,"deps":["zzz"]}],"workers":1},"expected":{"error":"unknown_dependency"}},
{"name":"edge-self-dependency","tags":["edge"],"args":{"tasks":[{"id":"a","duration":1,"deps":["a"]}],"workers":1},"expected":{"error":"cycle"}},
{"name":"hidden-unknown-beats-cycle","tags":["hidden"],"args":{"tasks":[{"id":"a","duration":1,"deps":["b"]},{"id":"b","duration":1,"deps":["a","q"]}],"workers":1},"expected":{"error":"unknown_dependency"}},
{"name":"hidden-tie-by-id","tags":["hidden"],"args":{"tasks":[{"id":"b","duration":2,"deps":[]},{"id":"a","duration":2,"deps":[]},{"id":"c","duration":2,"deps":[]}],"workers":2},"expected":{"makespan":4,"starts":{"a":0,"b":0,"c":2}}},
{"name":"hidden-finish-before-assign","tags":["hidden"],"args":{"tasks":[{"id":"a","duration":2,"deps":[]},{"id":"b","duration":2,"deps":[]},{"id":"c","duration":1,"deps":["a","b"]}],"workers":2},"expected":{"makespan":3,"starts":{"a":0,"b":0,"c":2}}},
{"name":"hidden-duplicate-deps","tags":["hidden"],"args":{"tasks":[{"id":"a","duration":1,"deps":[]},{"id":"b","duration":1,"deps":["a","a"]}],"workers":1},"expected":{"makespan":2,"starts":{"a":0,"b":1}}},
{"name":"random-1","tags":["hidden"],"args":{"tasks":[{"id":"t2","duration":1,"deps":[]},{"id":"t1","duration":1,"deps":[]},{"id":"t0","duration":1,"deps":[]},{"id":"t3","duration":1,"deps":["t0"]}],"workers":1},"expected":{"makespan":4,"starts":{"t0":0,"t1":1,"t2":2,"t3":3}}},
{"name":"random-2","tags":["hidden"],"args":{"tasks":[{"id":"t0","duration":1,"deps":[]},{"id":"t4","duration":3,"deps":["t1"]},{"id":"t1","duration":1,"deps":[]},{"id":"t2","duration":1,"deps":[]},{"id":"t3","duration":1,"deps":["t1"]}],"workers":2},"expected":{"makespan":5,"starts":{"t0":0,"t1":0,"t2":1,"t3":1,"t4":2}}},
{"name":"random-3","tags":["hidden"],"args":{"tasks":[{"id":"t3","duration":3,"deps":[]},{"id":"t5","duration":2,"deps":["t2"]},{"id":"t1","duration":1,"deps":["t0"]},{"id":"t2","duration":5,"deps":[]},{"id":"t4","duration":4,"deps":["t1"]},{"id":"t0","duration":2,"deps":[]}],"workers":2},"expected":{"makespan":9,"starts":{"t0":0,"t2":0,"t1":2,"t3":3,"t4":5,"t5":6}}},
{"name":"random-4","tags":["hidden"],"args":{"tasks":[{"id":"t2","duration":3,"deps":[]},{"id":"t0","duration":1,"deps":[]},{"id":"t1","duration":4,"deps":[]}],"workers":1},"expected":{"makespan":8,"starts":{"t0":0,"t1":1,"t2":5}}}
]}
```

## Reference solution

```python reference
import heapq
from collections import defaultdict

def solve(tasks, workers):
    byid = {t["id"]: t for t in tasks}
    for t in tasks:
        for d in t["deps"]:
            if d not in byid:
                return {"error": "unknown_dependency"}
    indeg = {t["id"]: len(set(t["deps"])) for t in tasks}
    children = defaultdict(list)
    for t in tasks:
        for d in set(t["deps"]):
            children[d].append(t["id"])
    ready = [i for i, k in indeg.items() if k == 0]
    heapq.heapify(ready)
    running, starts = [], {}
    free, now, done = workers, 0, 0
    while done < len(tasks):
        while free and ready:
            i = heapq.heappop(ready)
            starts[i] = now
            heapq.heappush(running, (now + byid[i]["duration"], i))
            free -= 1
        if not running:
            return {"error": "cycle"}
        now = running[0][0]
        while running and running[0][0] == now:
            _, i = heapq.heappop(running)
            free += 1
            done += 1
            for c in children[i]:
                indeg[c] -= 1
                if indeg[c] == 0:
                    heapq.heappush(ready, c)
    return {"makespan": now, "starts": starts}
```

## Interviewer notes

- **Target complexity:** O((V + E) log V)
- **Clarifying questions (answer verbatim):**
  - Q: Is the id comparison numeric?  
    A: No, plain string comparison.
  - Q: Can a worker sit idle while a task is ready?  
    A: No.
- **Hint ladder:**
  - H0 (free): Which two data structures drive a discrete-event simulation here?
  - H1 (-5): A min-heap of ready ids and a min-heap of (finish_time, id) for running tasks.
  - H2 (-10): Jump the clock straight to the next finish time instead of ticking.
  - H3 (-20): If nothing is running and unfinished tasks remain, the graph has a cycle. Check unknown dependencies first.
- **Follow-ups:**
  - Compute the critical path (the chain that determines the makespan).
  - Different worker speeds.
  - A task failing and being retried: how does the simulation change?
- **Mistakes the tests are built to catch:**
  - Assigning before releasing the finished tasks at the same instant.
  - Ticking the clock one unit at a time (duration up to 10^6).
  - Numeric id ordering.
  - Reporting cycle before unknown_dependency.
