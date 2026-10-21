---
id: lc-c07-in-memory-file-system
title: In-Memory File System
type: live-coding
level: [senior, staff]
tags: [design, tree, trie-like]
time_minutes: 45
languages: [python]
entry: InMemoryFS
kind: ops
runs_code: true
source: adapted
author: mockinterview
legacy_id: C7
---

# In-Memory File System

## Statement

Implement `InMemoryFS`. Paths are absolute, use `/` as separator, have no trailing slash (except the root `/`) and contain no `.` or `..`.

- `mkdir(path)`: create the directory and any missing parents. Returns `true` if at least one directory was created, `false` if it already existed or a **file** is in the way.
- `write(path, content)`: create or overwrite a file. The parent directory must already exist. Returns `false` if the parent is missing or is a file, if `path` is an existing directory, or if `path` is `/`.
- `read(path)`: file content, or `null` if the path does not exist or is a directory.
- `ls(path)`: for a directory, the sorted names of its direct children (names only); for a file, a one-element list with its own name; `null` if the path does not exist.
- `delete(path)`: remove a file or a whole directory subtree. Returns `false` if the path does not exist or is `/`.

File content may be an empty string, which is still a file.

**Signature:** `class InMemoryFS { mkdir(path) -> bool; write(path, content) -> bool; read(path) -> string | null; ls(path) -> string[] | null; delete(path) -> bool }`

**Constraints:**
- up to 200000 operations
- path depth <= 50

**Examples:**

- **Example 1** - calls: `InMemoryFS(); mkdir("/a/b"); write("/a/b/f", "hello"); ls("/a"); read("/a/b/f"); ls("/a/b/f"); delete("/a"); ls("/")`  
  returns: `[null,true,true,["b"],"hello",["f"],true,[]]`

## Stub

```python
class InMemoryFS:
    def __init__(self):
        """No constructor arguments."""
        pass

    def mkdir(self, path):
        """mkdir(path) -> bool"""
        raise NotImplementedError

    def write(self, path, content):
        """write(path, content) -> bool"""
        raise NotImplementedError

    def read(self, path):
        """read(path) -> string | null"""
        raise NotImplementedError

    def ls(self, path):
        """ls(path) -> string[] | null"""
        raise NotImplementedError

    def delete(self, path):
        """delete(path) -> bool"""
        raise NotImplementedError
```

## Tests

```json tests
{"function":"InMemoryFS","kind":"ops","compare":"exact","fuzz":40,"perf":{"sizes":[20000,100000,200000],"limit_ms":5000,"max_exponent":1.4},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/a/b"]],["write",["/a/b/f","hello"]],["ls",["/a"]],["read",["/a/b/f"]],["ls",["/a/b/f"]],["delete",["/a"]],["ls",["/"]]]}},
{"name":"edge-root-ops","tags":["edge"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/"]],["write",["/","x"]],["read",["/"]],["ls",["/"]],["delete",["/"]]]}},
{"name":"edge-empty-file","tags":["edge"],"args":{"calls":[["InMemoryFS",[]],["write",["/e",""]],["read",["/e"]],["ls",["/"]]]}},
{"name":"hidden-file-blocks-mkdir","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["write",["/f","1"]],["mkdir",["/f"]],["mkdir",["/f/g"]],["ls",["/"]]]}},
{"name":"hidden-write-to-dir","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/d"]],["write",["/d","x"]],["read",["/d"]]]}},
{"name":"hidden-write-missing-parent","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["write",["/no/such/f","x"]],["ls",["/"]]]}},
{"name":"hidden-mkdir-idempotent","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/a/b"]],["mkdir",["/a/b"]],["mkdir",["/a/b/c"]],["ls",["/a"]]]}}
]}
```

## Oracle

```python oracle
class InMemoryFS:
    def __init__(self):
        self.root = {}

    @staticmethod
    def _parts(path):
        return [] if path == "/" else path.strip("/").split("/")

    def _walk_dir(self, parts):
        node = self.root
        for p in parts:
            node = node.get(p)
            if not isinstance(node, dict):
                return None
        return node

    def mkdir(self, path):
        node, created = self.root, False
        for p in self._parts(path):
            if p in node:
                if not isinstance(node[p], dict):
                    return False
            else:
                node[p] = {}
                created = True
            node = node[p]
        return created

    def write(self, path, content):
        parts = self._parts(path)
        if not parts:
            return False
        parent = self._walk_dir(parts[:-1])
        if parent is None or isinstance(parent.get(parts[-1]), dict):
            return False
        parent[parts[-1]] = content
        return True

    def read(self, path):
        parts = self._parts(path)
        if not parts:
            return None
        parent = self._walk_dir(parts[:-1])
        if parent is None:
            return None
        v = parent.get(parts[-1])
        return v if isinstance(v, str) else None

    def ls(self, path):
        parts = self._parts(path)
        if not parts:
            return sorted(self.root)
        parent = self._walk_dir(parts[:-1])
        if parent is None or parts[-1] not in parent:
            return None
        v = parent[parts[-1]]
        return sorted(v) if isinstance(v, dict) else [parts[-1]]

    def delete(self, path):
        parts = self._parts(path)
        if not parts:
            return False
        parent = self._walk_dir(parts[:-1])
        if parent is None or parts[-1] not in parent:
            return False
        del parent[parts[-1]]
        return True

def gen_random(seed):
    rnd = random.Random(seed)
    paths = ["/", "/a", "/b", "/a/x", "/a/y", "/a/x/z", "/b/x", "/c/d/e"]
    return rand_ops(rnd, ("InMemoryFS",), rnd.randint(8, 35), [
        (3, lambda r: ("mkdir", r.choice(paths))), (4, lambda r: ("write", r.choice(paths), r.choice(["", "hi", "yo"]))),
        (3, lambda r: ("read", r.choice(paths))), (3, lambda r: ("ls", r.choice(paths))), (2, lambda r: ("delete", r.choice(paths)))])

def gen_perf(n):
    rnd = random.Random(107)
    dirs = ["/d%d/s%d" % (i, j) for i in range(30) for j in range(30)]
    return rand_ops(rnd, ("InMemoryFS",), n, [
        (3, lambda r: ("mkdir", r.choice(dirs))), (6, lambda r: ("write", r.choice(dirs) + "/f%d" % r.randint(0, 20), "v")),
        (6, lambda r: ("read", r.choice(dirs) + "/f%d" % r.randint(0, 20))), (1, lambda r: ("ls", r.choice(dirs))), (1, lambda r: ("delete", r.choice(dirs) + "/f%d" % r.randint(0, 20)))])
```

## Interviewer notes

- **Target complexity:** O(depth) per operation (plus O(k log k) to sort k children for ls)
- **Scaling check:** sizes [20000, 100000, 200000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.4
- **Clarifying questions (answer verbatim):**
  - Q: Is `//` or a trailing slash possible?  
    A: No, paths are canonical.
  - Q: Does `ls` mark directories?  
    A: No, plain names.
- **Hint ladder:**
  - H0 (free): What recursive structure do paths describe?
  - H1 (-5): A tree: directories map names to children, files hold content.
  - H2 (-10): Write one helper that walks to a parent directory and returns nothing if any step is missing or is a file.
  - H3 (-20): Distinguish directory from file by node type, not by content (empty file != directory).
- **Follow-ups:**
  - Add `move(src, dst)` and `copy`. What invariant protects against moving a directory into itself?
  - Add `find(name)` returning all matches.
  - Persist to disk and reload.
- **Mistakes the tests are built to catch:**
  - Using falsy content ("") as 'not a file'.
  - Partially creating directories before failing.
  - Allowing delete('/') or write('/').
