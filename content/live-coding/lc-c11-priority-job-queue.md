---
id: lc-c11-priority-job-queue
title: Priority Job Queue with Retries and Dead Letters
type: live-coding
level: [senior, staff]
tags: [design, heap, state-machine, retries]
time_minutes: 50
languages: [python]
entry: JobQueue
kind: ops
runs_code: true
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

## Stub

```python
class JobQueue:
    def __init__(self, max_attempts):
        """constructor(max_attempts)"""
        raise NotImplementedError

    def submit(self, id, priority, available_at):
        """submit(id, priority, available_at) -> bool"""
        raise NotImplementedError

    def claim(self, now):
        """claim(now) -> id | null"""
        raise NotImplementedError

    def complete(self, id):
        """complete(id) -> bool"""
        raise NotImplementedError

    def fail(self, id, now, backoff):
        """fail(id, now, backoff) -> 'retry' | 'dead' | null"""
        raise NotImplementedError

    def dead_letters(self):
        """dead_letters() -> string[]"""
        raise NotImplementedError

    def stats(self):
        """stats() -> object"""
        raise NotImplementedError
```

## Tests

```json tests
{"function":"JobQueue","kind":"ops","compare":"exact","fuzz":50,"perf":{"sizes":[20000,100000,200000],"limit_ms":5000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["JobQueue",[2]],["submit",["a",1,0]],["submit",["b",5,0]],["submit",["c",5,10]],["claim",[0]],["fail",["b",1,3]],["claim",[1]],["claim",[4]],["fail",["b",5,3]],["dead_letters",[]],["stats",[]]]}},
{"name":"edge-nothing-eligible","tags":["edge"],"args":{"calls":[["JobQueue",[1]],["claim",[0]],["submit",["a",1,5]],["claim",[4]],["claim",[5]],["claim",[5]]]}},
{"name":"edge-duplicate-submit","tags":["edge"],"args":{"calls":[["JobQueue",[1]],["submit",["a",1,0]],["submit",["a",9,0]],["claim",[0]],["complete",["a"]],["submit",["a",1,0]]]}},
{"name":"hidden-priority-then-available-then-id","tags":["hidden"],"args":{"calls":[["JobQueue",[1]],["submit",["z",2,0]],["submit",["y",2,1]],["submit",["x",2,1]],["submit",["w",1,0]],["claim",[5]],["claim",[5]],["claim",[5]],["claim",[5]]]}},
{"name":"hidden-retry-backoff","tags":["hidden"],"args":{"calls":[["JobQueue",[3]],["submit",["a",1,0]],["claim",[0]],["fail",["a",0,10]],["claim",[9]],["claim",[10]],["fail",["a",10,0]],["claim",[10]],["fail",["a",10,0]],["dead_letters",[]],["stats",[]]]}},
{"name":"hidden-complete-and-fail-wrong-state","tags":["hidden"],"args":{"calls":[["JobQueue",[2]],["submit",["a",1,0]],["complete",["a"]],["fail",["a",0,1]],["claim",[0]],["complete",["a"]],["complete",["a"]],["fail",["a",0,1]],["fail",["nope",0,1]]]}}
]}
```

## Oracle

```python oracle
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

def gen_random(seed):
    rnd = random.Random(seed)
    calls = [["JobQueue", [rnd.randint(1, 3)]]]
    now, jobs, nxt = 0, [], 0
    for _ in range(rnd.randint(8, 40)):
        now += rnd.randint(0, 3)
        c = rnd.random()
        if c < 0.3:
            jid = "j%d" % (rnd.randint(0, nxt) if nxt and rnd.random() < 0.15 else nxt)
            nxt += 1
            jobs.append(jid)
            calls.append(["submit", [jid, rnd.randint(0, 3), now + rnd.randint(0, 4)]])
        elif c < 0.55:
            calls.append(["claim", [now]])
        elif c < 0.7 and jobs:
            calls.append(["complete", [rnd.choice(jobs)]])
        elif c < 0.85 and jobs:
            calls.append(["fail", [rnd.choice(jobs), now, rnd.randint(0, 4)]])
        elif c < 0.93:
            calls.append(["dead_letters", []])
        else:
            calls.append(["stats", []])
    return {"calls": calls}

def gen_perf(n):
    rnd = random.Random(111)
    calls = [["JobQueue", [3]]]
    now, claimed = 0, []
    for i in range(n):
        now += 1
        c = rnd.random()
        if c < 0.4:
            calls.append(["submit", ["j%d" % i, rnd.randint(0, 9), now + rnd.randint(0, 50)]])
        elif c < 0.7:
            calls.append(["claim", [now]])
        elif c < 0.85:
            calls.append(["complete", ["j%d" % rnd.randint(0, i)]])
        else:
            calls.append(["fail", ["j%d" % rnd.randint(0, i), now, rnd.randint(1, 20)]])
    calls.append(["stats", []])
    return {"calls": calls}
```

## Interviewer notes

- **Target complexity:** O(log n) per submit, claim and fail
- **Scaling check:** sizes [20000, 100000, 200000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
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
