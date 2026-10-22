#!/usr/bin/env python3
"""Process-protocol shim for Python solutions.   usage: py_shim.py path/to/solution.py path/to/result.json
stdin : {"function": "name", "args": {...}}  or  {"function": "ClassName", "calls": [[name, [args]], ...]}
result: the JSON value, written to the result file. For class problems it is the list of return values (null
        for the constructor). stdout and stderr stay the solution's, so print() debugging is harmless."""
import importlib.util
import json
import sys


def main():
    path, result = sys.argv[1], sys.argv[2]
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
    text = json.dumps(out)  # fails before the file is touched if the value is not JSON
    with open(result, "w", encoding="utf-8") as fh:
        fh.write(text)


if __name__ == "__main__":
    main()
