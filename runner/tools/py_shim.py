#!/usr/bin/env python3
"""Process-protocol shim for Python solutions.   usage: py_shim.py path/to/solution.py
stdin : {"function": "name", "args": {...}}  or  {"function": "ClassName", "calls": [[name, [args]], ...]}
stdout: the JSON result. For class problems the result is the list of return values (null for the constructor)."""
import importlib.util
import json
import sys


def main():
    path = sys.argv[1]
    spec = importlib.util.spec_from_file_location("solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    req = json.load(sys.stdin)
    target = getattr(mod, req["function"])
    if "calls" in req:
        out, obj = [], None
        for i, (name, args) in enumerate(req["calls"]):
            if i == 0:
                obj = target(*args)
                out.append(None)
            else:
                out.append(getattr(obj, name)(*args))
    else:
        out = target(**req["args"])
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
