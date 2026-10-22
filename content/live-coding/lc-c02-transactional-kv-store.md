---
id: lc-c02-transactional-kv-store
title: In-Memory Key-Value Store with Nested Transactions
type: live-coding
level: [senior, staff]
tags: [design, state, stack]
time_minutes: 40
languages: [python]
entry: TransactionalKV
kind: ops
runs_code: true
source: adapted
author: mockinterview
legacy_id: C2
---

# In-Memory Key-Value Store with Nested Transactions

## Statement

Implement `TransactionalKV`:

- `set(key, value)` stores a value.
- `get(key)` returns the value, or `null` if the key is absent.
- `delete(key)` removes the key and returns `true` if it existed, else `false`.
- `begin()` opens a (possibly nested) transaction.
- `commit()` closes the innermost transaction and keeps its changes (they become part of the enclosing transaction, if any, and are still undone if the enclosing one rolls back). Returns `false` if no transaction is open.
- `rollback()` closes the innermost transaction and discards every change made since its matching `begin()`. Returns `false` if no transaction is open.

Reads inside a transaction see that transaction's uncommitted writes.

**Signature:** `class TransactionalKV { set(k, v); get(k) -> v | null; delete(k) -> bool; begin(); commit() -> bool; rollback() -> bool }`

**Constraints:**
- keys are strings, values are integers
- up to 100000 operations
- up to 1000 distinct keys

**Examples:**

- **Example 1** - calls: `TransactionalKV(); set("a", 1); begin(); set("a", 2); get("a"); rollback(); get("a"); commit()`  
  returns: `[null,null,null,null,2,true,1,false]`

## Stub

```python
class TransactionalKV:
    def __init__(self):
        """No constructor arguments."""
        pass

    def set(self, k, v):
        """set(k, v)"""
        raise NotImplementedError

    def get(self, k):
        """get(k) -> v | null"""
        raise NotImplementedError

    def delete(self, k):
        """delete(k) -> bool"""
        raise NotImplementedError

    def begin(self):
        """begin()"""
        raise NotImplementedError

    def commit(self):
        """commit() -> bool"""
        raise NotImplementedError

    def rollback(self):
        """rollback() -> bool"""
        raise NotImplementedError
```

## Signature

```signature
TransactionalKV()
set(k: string, v: int) -> void
get(k: string) -> int?
delete(k: string) -> bool
begin() -> void
commit() -> bool
rollback() -> bool
```

## Tests

```json tests
{"function":"TransactionalKV","kind":"ops","compare":"exact","fuzz":30,"perf":{"sizes":[20000,60000,100000],"limit_ms":5000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["TransactionalKV",[]],["set",["a",1]],["begin",[]],["set",["a",2]],["get",["a"]],["rollback",[]],["get",["a"]],["commit",[]]]}},
{"name":"edge-commit-nested-then-rollback-outer","tags":["edge"],"args":{"calls":[["TransactionalKV",[]],["set",["x",1]],["begin",[]],["set",["x",2]],["begin",[]],["set",["x",3]],["commit",[]],["get",["x"]],["rollback",[]],["get",["x"]]]}},
{"name":"hidden-delete-in-txn","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["set",["k",5]],["begin",[]],["delete",["k"]],["get",["k"]],["rollback",[]],["get",["k"]],["delete",["k"]],["delete",["k"]]]}},
{"name":"hidden-no-open-txn","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["commit",[]],["rollback",[]],["begin",[]],["commit",[]],["commit",[]]]}},
{"name":"hidden-new-key-rolled-back","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["begin",[]],["set",["n",1]],["rollback",[]],["get",["n"]]]}}
]}
```

## Oracle

```python oracle
class TransactionalKV:
    def __init__(self):
        self.data = {}
        self.snaps = []

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        return self.data.pop(key, None) is not None or False

    def begin(self):
        self.snaps.append(dict(self.data))

    def commit(self):
        if not self.snaps:
            return False
        self.snaps.pop()
        return True

    def rollback(self):
        if not self.snaps:
            return False
        self.data = self.snaps.pop()
        return True

def gen_random(seed):
    rnd = random.Random(seed)
    return rand_ops(rnd, ("TransactionalKV",), rnd.randint(8, 40), [
        (4, lambda r: ("set", r.choice("abc"), r.randint(0, 9))),
        (3, lambda r: ("get", r.choice("abc"))),
        (2, lambda r: ("delete", r.choice("abc"))),
        (2, lambda r: ("begin",)), (2, lambda r: ("commit",)), (2, lambda r: ("rollback",))])

def gen_perf(n):
    rnd = random.Random(102)
    return rand_ops(rnd, ("TransactionalKV",), n, [
        (8, lambda r: ("set", "k%d" % r.randint(0, 300), r.randint(0, 99))),
        (6, lambda r: ("get", "k%d" % r.randint(0, 300))),
        (2, lambda r: ("delete", "k%d" % r.randint(0, 300))),
        (1, lambda r: ("begin",)), (1, lambda r: ("commit",)), (1, lambda r: ("rollback",))])
```

## Interviewer notes

- **Target complexity:** Snapshot stack: O(keys) per begin. Undo log: O(1) per write, O(changes) per rollback.
- **Scaling check:** sizes [20000, 60000, 100000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: What does commit of a nested transaction mean?  
    A: The changes merge into the parent. An outer rollback still discards them.
  - Q: Can delete of a missing key create an undo entry?  
    A: It must not change visible state.
- **Hint ladder:**
  - H0 (free): What do you need to remember in order to undo?
  - H1 (-5): A full copy of the state at begin() is the simplest correct answer. Do that first.
  - H2 (-10): Then think about an undo log: for each write inside a transaction, record the previous value (or 'absent').
  - H3 (-20): On commit of an inner transaction, its undo records must be handed to the parent, not dropped.
- **Follow-ups:**
  - Replace the snapshot with an undo log so begin() is O(1). What is the memory trade-off?
  - Add `count(value)` in O(1) average.
  - Add concurrent readers: what isolation level do you provide?
- **Mistakes the tests are built to catch:**
  - Snapshot copy that is shallow for mutable values.
  - Treating an inner commit as a permanent write (outer rollback must still undo it).
  - Returning `true` from delete for a missing key.
  - Undo log that forgets keys that were absent before the write.
