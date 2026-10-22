---
id: lc-c08-http-path-router
title: HTTP Path Router
type: live-coding
level: [senior]
tags: [design, strings, trie]
time_minutes: 45
languages: [python]
entry: Router
kind: ops
runs_code: true
source: adapted
author: mockinterview
legacy_id: C8
---

# HTTP Path Router

## Statement

Implement `Router`.

- `add_route(method, pattern, handler)` registers a handler (a string). Registering the same `(method, pattern)` again replaces the handler but keeps the original registration order.
- `route(method, path)` returns one of:
  - `{"handler": h, "params": {...}}`
  - `{"error": "not_found"}` - no registered pattern matches the path under any method
  - `{"error": "method_not_allowed", "allowed": [...]}` - patterns match the path, but none for this method; `allowed` is the sorted list of distinct methods of the patterns that match

Pattern segments (split on `/`; `/` alone is the root with zero segments):
- a **static** segment matches itself exactly
- `:name` matches any single segment and captures it in `params["name"]`
- `*` may only appear as the last segment; it matches **one or more** remaining segments and captures them joined by `/` in `params["*"]`

When several patterns of the requested method match, choose by comparing per-segment scores left to right (static = 2, param = 1, wildcard = 0), the highest wins; equal scores are resolved in favour of the earlier registration. Example: for `/a/b/c`, `/a/b/*` beats `/a/:x/c`.

**Signature:** `class Router { add_route(method: string, pattern: string, handler: string); route(method: string, path: string) -> object }`

**Constraints:**
- up to 2000 routes
- up to 200000 calls
- paths are canonical (no trailing or duplicate slashes)

**Examples:**

- **Example 1** - calls: `Router(); add_route("GET", "/users/:id", "show"); add_route("GET", "/users/me", "me"); add_route("POST", "/users", "create"); route("GET", "/users/me"); route("GET", "/users/42"); route("DELETE", "/users"); route("GET", "/x")`  
  returns: `[null,null,null,null,{"handler":"me","params":{}},{"handler":"show","params":{"id":"42"}},{"error":"method_not_allowed","allowed":["POST"]},{"error":"not_found"}]`

## Stub

```python
class Router:
    def __init__(self):
        """No constructor arguments."""
        pass

    def add_route(self, method, pattern, handler):
        """add_route(method: string, pattern: string, handler: string)"""
        raise NotImplementedError

    def route(self, method, path):
        """route(method: string, path: string) -> object"""
        raise NotImplementedError
```

## Signature

```signature
Router()
add_route(method: string, pattern: string, handler: string) -> void
route(method: string, path: string) -> record{handler?: string, params?: {string: string}, error?: string, allowed?: string[]}
```

## Tests

```json tests
{"function":"Router","kind":"ops","compare":"exact","fuzz":40,"perf":{"sizes":[2000,6000,12000],"limit_ms":5000,"max_exponent":1.5},"cases":[
{"name":"example-1","tags":["visible"],"args":{"calls":[["Router",[]],["add_route",["GET","/users/:id","show"]],["add_route",["GET","/users/me","me"]],["add_route",["POST","/users","create"]],["route",["GET","/users/me"]],["route",["GET","/users/42"]],["route",["DELETE","/users"]],["route",["GET","/x"]]]}},
{"name":"edge-root","tags":["edge"],"args":{"calls":[["Router",[]],["add_route",["GET","/","home"]],["route",["GET","/"]],["route",["GET","/x"]]]}},
{"name":"edge-wildcard-needs-one","tags":["edge"],"args":{"calls":[["Router",[]],["add_route",["GET","/files/*","f"]],["route",["GET","/files"]],["route",["GET","/files/a/b/c"]]]}},
{"name":"hidden-static-beats-param-beats-wildcard","tags":["hidden"],"args":{"calls":[["Router",[]],["add_route",["GET","/a/*","w"]],["add_route",["GET","/a/:x","p"]],["add_route",["GET","/a/b","s"]],["route",["GET","/a/b"]],["route",["GET","/a/c"]],["route",["GET","/a/c/d"]]]}},
{"name":"hidden-leftmost-score-wins","tags":["hidden"],"args":{"calls":[["Router",[]],["add_route",["GET","/a/:x/c","r1"]],["add_route",["GET","/a/b/*","r2"]],["route",["GET","/a/b/c"]]]}},
{"name":"hidden-replace-keeps-order","tags":["hidden"],"args":{"calls":[["Router",[]],["add_route",["GET","/p/:a","one"]],["add_route",["GET","/p/:b","two"]],["add_route",["GET","/p/:a","three"]],["route",["GET","/p/9"]]]}},
{"name":"hidden-tie-earlier-wins","tags":["hidden"],"args":{"calls":[["Router",[]],["add_route",["GET","/q/:a","first"]],["add_route",["GET","/q/:b","second"]],["route",["GET","/q/1"]]]}},
{"name":"hidden-method-not-allowed","tags":["hidden"],"args":{"calls":[["Router",[]],["add_route",["POST","/m","p"]],["add_route",["DELETE","/m","d"]],["add_route",["GET","/other","o"]],["route",["GET","/m"]]]}}
]}
```

## Oracle

```python oracle
class Router:
    def __init__(self):
        self.routes = []
        self.index = {}

    def add_route(self, method, pattern, handler):
        key = (method, pattern)
        if key in self.index:
            self.routes[self.index[key]][3] = handler
            return
        segs = [] if pattern == "/" else pattern.strip("/").split("/")
        self.index[key] = len(self.routes)
        self.routes.append([method, pattern, segs, handler])

    @staticmethod
    def _match(segs, path):
        params, score = {}, []
        for i, s in enumerate(segs):
            if s == "*":
                if len(path) <= i:
                    return None
                params["*"] = "/".join(path[i:])
                score.append(0)
                return tuple(score), params
            if i >= len(path):
                return None
            if s.startswith(":"):
                params[s[1:]] = path[i]
                score.append(1)
            elif s == path[i]:
                score.append(2)
            else:
                return None
        if len(segs) != len(path):
            return None
        return tuple(score), params

    def route(self, method, path):
        ps = [] if path == "/" else path.strip("/").split("/")
        best, allowed = None, set()
        for m, _, segs, handler in self.routes:
            r = self._match(segs, ps)
            if r is None:
                continue
            allowed.add(m)
            if m == method and (best is None or r[0] > best[0]):
                best = (r[0], r[1], handler)
        if best:
            return {"handler": best[2], "params": best[1]}
        if allowed:
            return {"error": "method_not_allowed", "allowed": sorted(allowed)}
        return {"error": "not_found"}

def gen_random(seed):
    rnd = random.Random(seed)
    PATTERNS = ["/", "/users", "/users/:id", "/users/me", "/users/:id/posts", "/files/*", "/files/public/*", "/a/:x/c", "/a/b/*", "/a/:y/:z"]
    PATHS = ["/", "/users", "/users/me", "/users/42", "/users/42/posts", "/users/me/posts", "/files/a", "/files/public/x/y", "/files", "/a/b/c", "/a/q/c", "/a/b/z", "/nope"]
    calls = [["Router", []]]
    for _ in range(rnd.randint(3, 9)):
        calls.append(["add_route", [rnd.choice(["GET", "POST", "DELETE"]), rnd.choice(PATTERNS), "h%d" % rnd.randint(1, 99)]])
    for _ in range(rnd.randint(5, 15)):
        calls.append(["route", [rnd.choice(["GET", "POST", "DELETE", "PUT"]), rnd.choice(PATHS)]])
    return {"calls": calls}

def gen_perf(n):
    rnd = random.Random(108)
    calls = [["Router", []]]
    for i in range(200):
        calls.append(["add_route", ["GET", "/s%d/:id/%s" % (i, rnd.choice(["x", "y", "*"])), "h%d" % i]])
    for _ in range(n):
        calls.append(["route", ["GET", "/s%d/%d/x" % (rnd.randint(0, 220), rnd.randint(0, 99))]])
    return {"calls": calls}
```

## Interviewer notes

- **Target complexity:** Linear scan: O(routes * segments) per lookup. A segment trie makes it O(segments).
- **Scaling check:** sizes [2000, 6000, 12000], limit 5000 ms (calibrated to a straightforward Python solution), growth exponent at most 1.5
- **Clarifying questions (answer verbatim):**
  - Q: Does method matter for choosing between patterns?  
    A: Only patterns registered for the requested method compete. Others only feed `allowed`.
  - Q: Can `:` params be empty?  
    A: No: segments are never empty.
- **Hint ladder:**
  - H0 (free): Start with the obviously correct linear scan over all routes.
  - H1 (-5): Write `match(pattern_segments, path_segments) -> (score_tuple, params) | None`.
  - H2 (-10): Python/JS tuple or array comparison gives you the lexicographic rule for free. Think about what to do for ties.
  - H3 (-20): Only then consider a trie with static/param/wildcard children and backtracking.
- **Follow-ups:**
  - Make lookup O(path length) with a trie. How does backtracking appear?
  - Add middleware groups and prefix mounting.
  - Regex constraints on params (`:id(\d+)`).
- **Mistakes the tests are built to catch:**
  - Picking the first match instead of the best.
  - Letting wildcard match zero segments.
  - Reporting method_not_allowed from patterns that do not match the path.
  - Replacing a duplicate route at the end of the order.
