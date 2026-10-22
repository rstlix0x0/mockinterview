"""Interview-mode dependency checks: a solution may use only its language's standard library.

A cheap static look before `run`, friction in the same spirit as the mod's guard, not a sandbox: a dynamic
import gets past it. Each check returns the names it found that are not allowed.
"""
import ast
import sys


def check_python(solution):
    with open(solution, encoding="utf-8") as fh:
        source = fh.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []  # the run itself reports the syntax error
    allowed = set(sys.stdlib_module_names) | {"__future__"}
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        else:
            continue
        for name in names:
            top = name.split(".")[0]
            if top not in allowed and top not in found:
                found.append(top)
    return found


CHECKS = {"python": check_python}


def check(kind, solution):
    return CHECKS[kind](solution)
