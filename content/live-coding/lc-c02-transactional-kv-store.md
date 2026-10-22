---
id: lc-c02-transactional-kv-store
title: In-Memory Key-Value Store with Nested Transactions
type: live-coding
level: [senior, staff]
tags: [design, state, stack]
time_minutes: 40
entry: TransactionalKV
kind: ops
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
{"function":"TransactionalKV","kind":"ops","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["TransactionalKV",[]],["set",["a",1]],["begin",[]],["set",["a",2]],["get",["a"]],["rollback",[]],["get",["a"]],["commit",[]]]},"expected":[null,null,null,null,2,true,1,false]},
{"name":"edge-commit-nested-then-rollback-outer","tags":["edge"],"args":{"calls":[["TransactionalKV",[]],["set",["x",1]],["begin",[]],["set",["x",2]],["begin",[]],["set",["x",3]],["commit",[]],["get",["x"]],["rollback",[]],["get",["x"]]]},"expected":[null,null,null,null,null,null,true,3,true,1]},
{"name":"hidden-delete-in-txn","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["set",["k",5]],["begin",[]],["delete",["k"]],["get",["k"]],["rollback",[]],["get",["k"]],["delete",["k"]],["delete",["k"]]]},"expected":[null,null,null,true,null,true,5,true,false]},
{"name":"hidden-no-open-txn","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["commit",[]],["rollback",[]],["begin",[]],["commit",[]],["commit",[]]]},"expected":[null,false,false,null,true,false]},
{"name":"hidden-new-key-rolled-back","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["begin",[]],["set",["n",1]],["rollback",[]],["get",["n"]]]},"expected":[null,null,null,true,null]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["rollback",[]],["rollback",[]],["get",["b"]],["rollback",[]],["set",["c",9]],["set",["c",6]],["set",["a",7]],["set",["b",0]],["rollback",[]],["begin",[]],["get",["a"]],["set",["c",4]],["set",["b",8]],["begin",[]],["set",["a",5]],["rollback",[]],["rollback",[]]]},"expected":[null,false,false,null,false,null,null,null,null,false,null,7,null,null,null,null,true,true]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["delete",["b"]],["commit",[]],["commit",[]],["get",["a"]],["delete",["b"]],["get",["b"]],["get",["b"]],["delete",["b"]],["delete",["b"]],["begin",[]],["commit",[]],["set",["c",0]],["delete",["c"]],["set",["b",0]],["set",["b",3]],["set",["b",4]],["commit",[]]]},"expected":[null,false,false,false,null,false,null,null,false,false,null,true,null,true,null,null,null,false]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["commit",[]],["delete",["c"]],["commit",[]],["get",["a"]],["delete",["b"]],["rollback",[]],["commit",[]],["rollback",[]],["set",["b",9]],["set",["a",2]],["set",["a",0]],["commit",[]],["rollback",[]],["get",["a"]],["rollback",[]],["get",["c"]]]},"expected":[null,false,false,false,null,false,false,false,false,null,null,null,false,false,0,false,null]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["TransactionalKV",[]],["set",["c",2]],["rollback",[]],["commit",[]],["delete",["a"]],["begin",[]],["set",["b",0]],["begin",[]],["set",["c",4]],["set",["a",1]],["set",["a",7]],["commit",[]],["commit",[]],["set",["b",3]],["commit",[]]]},"expected":[null,null,false,false,false,null,null,null,null,null,null,true,true,null,false]}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** Snapshot stack: O(keys) per begin. Undo log: O(1) per write, O(changes) per rollback.
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
