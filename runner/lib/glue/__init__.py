"""Generated glue for typed languages (Go, Rust). Standard library only.

A typed language cannot call a function by name at run time, so for each problem the runner writes, from the
pack's `## Signature`: a typed stub (on `begin`) and a small program around the solution (the glue, on `begin`
and before every build) that reads the request from stdin, converts the JSON arguments to the signature's types,
calls the solution and writes the JSON result to the file named by its first argument. The request is the
positional one (`{"function", "args": [...]}` or `{"function", "calls": [...]}`).

A language file picks a generator with `glue = "go"` or `glue = "rust"`. Records (and Go tuples, Rust unions)
become named types; `named_types` chooses their names from where they appear.
"""
from ..signature import fmt


class Unsupported(Exception):
    """The signature uses something this language's glue cannot express."""


def pascal(name):
    """two_sum -> TwoSum, in_flight -> InFlight."""
    return "".join(w[:1].upper() + w[1:] for w in name.split("_") if w)


def camel(name):
    p = pascal(name)
    return p[:1].lower() + p[1:]


def _item(context):
    """Name of a list element from the list's name: tasks -> Task, data -> DataItem."""
    if context.endswith("s") and not context.endswith("ss") and len(context) > 1:
        return context[:-1]
    return context + "Item"


def walk(t, context, visit):
    """Call visit(type, context name) for t and every type inside it, outermost first."""
    visit(t, context)
    tag = t[0]
    if tag == "list":
        walk(t[1], _item(context), visit)
    elif tag == "opt":
        walk(t[1], context, visit)
    elif tag == "map":
        walk(t[1], context + "Value", visit)
    elif tag == "tuple":
        for i, x in enumerate(t[1]):
            walk(x, "%sItem%d" % (context, i), visit)
    elif tag == "record":
        for name, _opt, x in t[1]:
            walk(x, context + pascal(name), visit)
    elif tag == "union":
        for x in t[1]:
            walk(x, context, visit)


def all_types(sig):
    """[(type, context name)] for every parameter and return type of the signature."""
    out = []

    def visit(t, ctx):
        out.append((t, ctx))

    decls = [sig] + list(sig.methods)
    for d in decls:
        for pname, t in d.params:
            walk(t, pascal(pname), visit)
        if d.returns is not None and d.returns != ("void",):
            walk(d.returns, pascal(d.name) + "Result", visit)
    return out


def named_types(sig, tags, structural=None, reserved=()):
    """{fmt(type): name} for each distinct type whose tag is in `tags`, named after its first context.

    `structural(t)` may give a name from the type itself (Go tuples: TupleStringInt) instead of the context.
    Names never repeat and never equal one in `reserved` (the class name); a clash gets 2, 3, ... appended."""
    names, used = {}, set(reserved)
    for t, ctx in all_types(sig):
        key = fmt(t)
        if t[0] not in tags or key in names:
            continue
        base = (structural and structural(t)) or ctx
        name, n = base, 2
        while name in used:
            name, n = "%s%d" % (base, n), n + 1
        used.add(name)
        names[key] = name
    return names


def uses(sig, tag):
    return any(t[0] == tag for t, _c in all_types(sig))


def get(name):
    """A fresh generator by name."""
    from importlib import import_module
    return getattr(import_module("." + name, __name__), name.capitalize())()


GENERATORS = ("go", "rust")
