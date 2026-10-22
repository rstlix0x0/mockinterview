---
id: lc-c07-in-memory-file-system
title: In-Memory File System
type: live-coding
level: [senior, staff]
tags: [design, tree, trie-like]
time_minutes: 45
entry: InMemoryFS
kind: ops
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

## Signature

```signature
InMemoryFS()
mkdir(path: string) -> bool
write(path: string, content: string) -> bool
read(path: string) -> string?
ls(path: string) -> string[]?
delete(path: string) -> bool
```

## Tests

```json tests
{"function":"InMemoryFS","kind":"ops","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/a/b"]],["write",["/a/b/f","hello"]],["ls",["/a"]],["read",["/a/b/f"]],["ls",["/a/b/f"]],["delete",["/a"]],["ls",["/"]]]},"expected":[null,true,true,["b"],"hello",["f"],true,[]]},
{"name":"edge-root-ops","tags":["edge"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/"]],["write",["/","x"]],["read",["/"]],["ls",["/"]],["delete",["/"]]]},"expected":[null,false,false,null,[],false]},
{"name":"edge-empty-file","tags":["edge"],"args":{"calls":[["InMemoryFS",[]],["write",["/e",""]],["read",["/e"]],["ls",["/"]]]},"expected":[null,true,"",["e"]]},
{"name":"hidden-file-blocks-mkdir","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["write",["/f","1"]],["mkdir",["/f"]],["mkdir",["/f/g"]],["ls",["/"]]]},"expected":[null,true,false,false,["f"]]},
{"name":"hidden-write-to-dir","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/d"]],["write",["/d","x"]],["read",["/d"]]]},"expected":[null,true,false,null]},
{"name":"hidden-write-missing-parent","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["write",["/no/such/f","x"]],["ls",["/"]]]},"expected":[null,false,[]]},
{"name":"hidden-mkdir-idempotent","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/a/b"]],["mkdir",["/a/b"]],["mkdir",["/a/b/c"]],["ls",["/a"]]]},"expected":[null,true,false,true,["b"]]},
{"name":"random-1","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["mkdir",["/b"]],["mkdir",["/a/x/z"]],["mkdir",["/b/x"]],["mkdir",["/c/d/e"]],["mkdir",["/b"]],["write",["/",""]],["ls",["/a/x/z"]],["mkdir",["/a"]],["ls",["/a/y"]],["write",["/b","hi"]],["read",["/b"]],["mkdir",["/a/x/z"]],["write",["/c/d/e",""]],["write",["/c/d/e","hi"]],["ls",["/b"]]]},"expected":[null,true,true,true,true,false,false,[],false,null,false,null,false,false,false,["x"]]},
{"name":"random-2","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["ls",["/b"]],["read",["/a/x/z"]],["write",["/a/y","hi"]],["delete",["/a/x"]],["read",["/a"]],["read",["/a"]],["mkdir",["/a/x/z"]],["read",["/a/y"]],["read",["/a/x/z"]],["write",["/c/d/e","hi"]],["mkdir",["/a/x"]],["read",["/a/x/z"]],["mkdir",["/a"]],["read",["/b"]],["ls",["/"]],["mkdir",["/a/y"]]]},"expected":[null,null,null,false,false,null,null,true,null,null,false,false,null,false,null,["a"],true]},
{"name":"random-3","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["delete",["/c/d/e"]],["write",["/a/y","yo"]],["mkdir",["/b"]],["write",["/b/x",""]],["read",["/a"]],["read",["/b"]],["write",["/a/x/z","yo"]],["mkdir",["/"]],["ls",["/b"]],["read",["/a"]],["ls",["/a/x/z"]],["delete",["/b"]]]},"expected":[null,false,false,true,true,null,null,false,false,["x"],null,null,true]},
{"name":"random-4","tags":["hidden"],"args":{"calls":[["InMemoryFS",[]],["read",["/a/y"]],["ls",["/a/x/z"]],["write",["/b","yo"]],["ls",["/b/x"]],["write",["/a/y","hi"]],["write",["/b/x","hi"]],["read",["/a/y"]],["ls",["/b"]],["mkdir",["/"]],["read",["/b"]],["write",["/a/x/z",""]],["mkdir",["/a/y"]]]},"expected":[null,null,null,true,null,false,false,null,["b"],false,"yo",false,true]}
]}
```

## Reference solution

```python reference
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
```

## Interviewer notes

- **Target complexity:** O(depth) per operation (plus O(k log k) to sort k children for ls)
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
