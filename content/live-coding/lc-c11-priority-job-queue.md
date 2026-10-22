---
id: lc-c11-priority-job-queue
title: Priority Job Queue with Retries and Dead Letters
type: live-coding
level: [senior, staff]
tags: [design, heap, state-machine, retries]
time_minutes: 50
entry: JobQueue
kind: ops
source: adapted
author: mockinterview
legacy_id: C11
---

# Priority Job Queue with Retries and Dead Letters

## Statement

Implement `JobQueue(max_attempts)`. The clock is supplied by the caller through `now`, and `now` never decreases across calls.

- `submit(job_id, priority, available_at)`: add a pending job. Returns `false` (and changes nothing) if `job_id` was ever submitted before, in any state.
- `claim(now)`: pick the job to run: among pending jobs with `available_at <= now`, the one with the **highest** priority, then the smallest `available_at`, then the smallest `job_id`. It becomes in-flight and its attempt counter increases by one. Returns the id, or `null` when nothing is eligible.
- `complete(job_id)`: marks an in-flight job done and returns `true`; otherwise `false`.
- `fail(job_id, now, backoff)`: for an in-flight job, if it has already been claimed `max_attempts` times it becomes **dead** and the result is `"dead"`; otherwise it goes back to pending with `available_at = now + backoff` and the result is `"retry"`. For any other job the result is `null`.
- `dead_letters()`: sorted list of dead job ids.
- `stats()`: `{"pending": a, "in_flight": b, "done": c, "dead": d}`.

`claim` must not scan every pending job.

**Signature:** `class JobQueue { constructor(max_attempts); submit(id, priority, available_at) -> bool; claim(now) -> id | null; complete(id) -> bool; fail(id, now, backoff) -> 'retry' | 'dead' | null; dead_letters() -> string[]; stats() -> object }`

**Constraints:**
- up to 200000 operations
- priorities are integers 0..1000

**Examples:**

- **Example 1** - calls: `JobQueue(2); submit("a", 1, 0); submit("b", 5, 0); submit("c", 5, 10); claim(0); fail("b", 1, 3); claim(1); claim(4); fail("b", 5, 3); dead_letters(); stats()`  
  returns: `[null,true,true,true,"b","retry","a","b","dead",["b"],{"pending":1,"in_flight":1,"done":0,"dead":1}]`

## Signature

```signature
JobQueue(max_attempts: int)
submit(id: string, priority: int, available_at: int) -> bool
claim(now: int) -> string?
complete(id: string) -> bool
fail(id: string, now: int, backoff: int) -> string?
dead_letters() -> string[]
stats() -> record{pending: int, in_flight: int, done: int, dead: int}
```

## Tests

```json tests
{"function":"JobQueue","kind":"ops","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["JobQueue",[2]],["submit",["a",1,0]],["submit",["b",5,0]],["submit",["c",5,10]],["claim",[0]],["fail",["b",1,3]],["claim",[1]],["claim",[4]],["fail",["b",5,3]],["dead_letters",[]],["stats",[]]]},"expected":[null,true,true,true,"b","retry","a","b","dead",["b"],{"pending":1,"in_flight":1,"done":0,"dead":1}]},
{"name":"edge-nothing-eligible","tags":["edge"],"args":{"calls":[["JobQueue",[1]],["claim",[0]],["submit",["a",1,5]],["claim",[4]],["claim",[5]],["claim",[5]]]},"expected":[null,null,true,null,"a",null]},
{"name":"edge-duplicate-submit","tags":["edge"],"args":{"calls":[["JobQueue",[1]],["submit",["a",1,0]],["submit",["a",9,0]],["claim",[0]],["complete",["a"]],["submit",["a",1,0]]]},"expected":[null,true,false,"a",true,false]},
{"name":"hidden-priority-then-available-then-id","tags":["hidden"],"args":{"calls":[["JobQueue",[1]],["submit",["z",2,0]],["submit",["y",2,1]],["submit",["x",2,1]],["submit",["w",1,0]],["claim",[5]],["claim",[5]],["claim",[5]],["claim",[5]]]},"expected":[null,true,true,true,true,"z","x","y","w"]},
{"name":"hidden-retry-backoff","tags":["hidden"],"args":{"calls":[["JobQueue",[3]],["submit",["a",1,0]],["claim",[0]],["fail",["a",0,10]],["claim",[9]],["claim",[10]],["fail",["a",10,0]],["claim",[10]],["fail",["a",10,0]],["dead_letters",[]],["stats",[]]]},"expected":[null,true,"a","retry",null,"a","retry","a","dead",["a"],{"pending":0,"in_flight":0,"done":0,"dead":1}]},
{"name":"hidden-complete-and-fail-wrong-state","tags":["hidden"],"args":{"calls":[["JobQueue",[2]],["submit",["a",1,0]],["complete",["a"]],["fail",["a",0,1]],["claim",[0]],["complete",["a"]],["complete",["a"]],["fail",["a",0,1]],["fail",["nope",0,1]]]},"expected":[null,true,false,null,"a",true,false,null,null]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["JobQueue",[2]],["claim",[0]],["dead_letters",[]],["submit",["j0",2,5]],["claim",[8]],["claim",[9]],["claim",[11]],["fail",["j0",14,3]],["claim",[16]],["submit",["j1",3,21]],["complete",["j1"]],["submit",["j2",2,19]],["stats",[]]]},"expected":[null,null,[],true,"j0",null,null,"retry",null,true,false,true,{"pending":3,"in_flight":0,"done":0,"dead":0}]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["JobQueue",[1]],["submit",["j0",3,5]],["stats",[]],["submit",["j1",0,9]],["stats",[]],["claim",[11]],["claim",[14]],["dead_letters",[]],["submit",["j2",0,17]]]},"expected":[null,true,{"pending":1,"in_flight":0,"done":0,"dead":0},true,{"pending":2,"in_flight":0,"done":0,"dead":0},"j0","j1",[],true]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["JobQueue",[1]],["dead_letters",[]],["submit",["j0",2,2]],["claim",[4]],["submit",["j1",0,7]],["dead_letters",[]],["submit",["j2",2,11]],["fail",["j2",11,4]],["stats",[]],["submit",["j3",3,13]],["complete",["j3"]],["fail",["j1",19,3]]]},"expected":[null,[],true,"j0",true,[],true,null,{"pending":2,"in_flight":1,"done":0,"dead":0},true,false,null]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["JobQueue",[3]],["claim",[0]],["stats",[]],["dead_letters",[]],["submit",["j0",0,3]],["fail",["j0",5,1]],["fail",["j0",6,0]],["claim",[6]],["fail",["j0",6,2]],["submit",["j0",1,12]],["submit",["j2",0,15]],["fail",["j0",12,2]],["submit",["j3",2,18]],["submit",["j4",1,18]],["fail",["j3",20,1]]]},"expected":[null,null,{"pending":0,"in_flight":0,"done":0,"dead":0},[],true,null,null,"j0","retry",false,true,null,true,true,null]}
]}
```

## Reference solution

```python reference
import heapq
from collections import Counter

class JobQueue:
    def __init__(self, max_attempts):
        self.max_attempts = max_attempts
        self.state, self.attempts, self.prio = {}, {}, {}
        self.waiting, self.ready = [], []

    def submit(self, job_id, priority, available_at):
        if job_id in self.state:
            return False
        self.state[job_id], self.attempts[job_id], self.prio[job_id] = "pending", 0, priority
        heapq.heappush(self.waiting, (available_at, job_id))
        return True

    def claim(self, now):
        while self.waiting and self.waiting[0][0] <= now:
            at, jid = heapq.heappop(self.waiting)
            heapq.heappush(self.ready, (-self.prio[jid], at, jid))
        if not self.ready:
            return None
        _, _, jid = heapq.heappop(self.ready)
        self.state[jid] = "in_flight"
        self.attempts[jid] += 1
        return jid

    def complete(self, job_id):
        if self.state.get(job_id) != "in_flight":
            return False
        self.state[job_id] = "done"
        return True

    def fail(self, job_id, now, backoff):
        if self.state.get(job_id) != "in_flight":
            return None
        if self.attempts[job_id] >= self.max_attempts:
            self.state[job_id] = "dead"
            return "dead"
        self.state[job_id] = "pending"
        heapq.heappush(self.waiting, (now + backoff, job_id))
        return "retry"

    def dead_letters(self):
        return sorted(j for j, s in self.state.items() if s == "dead")

    def stats(self):
        c = Counter(self.state.values())
        return {k: c.get(k, 0) for k in ("pending", "in_flight", "done", "dead")}
```

## Interviewer notes

- **Target complexity:** O(log n) per submit, claim and fail
- **Clarifying questions (answer verbatim):**
  - Q: Does the attempt counter increase on claim or on fail?  
    A: On claim.
  - Q: Can `now` go backwards?  
    A: No.
- **Hint ladder:**
  - H0 (free): Draw the state machine first: pending -> in_flight -> done | pending (retry) | dead.
  - H1 (-5): Eligibility depends on time, ordering on priority. One heap cannot do both.
  - H2 (-10): Two heaps: a 'waiting' min-heap by available_at, and a 'ready' heap ordered by (-priority, available_at, id).
  - H3 (-20): On claim, move everything with available_at <= now from waiting to ready, then pop ready.
- **Follow-ups:**
  - Visibility timeout: a claimed job returns to pending if it is not completed within T.
  - Multiple consumers: what makes `claim` atomic? (compare-and-set, SELECT ... FOR UPDATE SKIP LOCKED)
  - Exactly-once vs at-least-once: what does your design guarantee?
  - Persist to a database and recover after a crash.
- **Mistakes the tests are built to catch:**
  - Scanning all pending jobs on claim.
  - Counting attempts on fail instead of on claim.
  - Resubmitting an id that already exists.
  - Sorting only by priority and ignoring available_at / id tie-breaks.

---
