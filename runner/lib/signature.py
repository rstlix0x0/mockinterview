"""The `## Signature` of a live-coding pack: grammar, parser and value check. Standard library only.

A signature states the JSON types of a problem's inputs and outputs, so that typed languages can be given glue
(docs/languages.md). Names are the Python names of the stub. One declaration per line:

    two_sum(nums: int[], target: int) -> int[]          kind: func, one line

    MinStack()                                          kind: ops, the constructor first (no return type),
    push(x: int) -> void                                then one line per method
    get_min() -> int

Types:

    int  float  bool  string                 int is a signed 64-bit integer; float also accepts integers
    T[]                                      list
    T?                                       T or null
    [A, B, ...]                              tuple: a list of fixed length (two or more)
    {string: T}                              map with string keys
    record{a: T, b?: U}                      object with these keys; `b?` may be absent
    A | B                                    either (left to the language whether it can express it)
    (T)                                      grouping, e.g. (int | string)[]
    void                                     method return only: the call returns nothing (null)
"""
import re

SCALARS = ("int", "float", "bool", "string")
INT_MIN, INT_MAX = -2 ** 63, 2 ** 63 - 1
_TOKEN = re.compile(r"\s*(->|[A-Za-z_][A-Za-z0-9_]*|[\[\]?|,:(){}])")


class SignatureError(Exception):
    pass


class Signature:
    """name, params [(name, type)], returns (None for an ops constructor) and methods [Signature]."""

    def __init__(self, name, params, returns, methods=()):
        self.name, self.params, self.returns, self.methods = name, params, returns, list(methods)

    def method(self, name):
        return next((m for m in self.methods if m.name == name), None)


# ------------------------------------------------------------------- parsing

def _tokens(text):
    out, pos = [], 0
    text = text.rstrip()
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            raise SignatureError("unexpected %r" % text[pos:].strip()[:20])
        out.append(m.group(1))
        pos = m.end()
    return out


class _Parser:
    def __init__(self, text):
        self.toks, self.i = _tokens(text), 0

    def peek(self, k=0):
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else None

    def take(self, want=None):
        tok = self.peek()
        if tok is None or (want is not None and tok != want):
            raise SignatureError("expected %s, found %s" % (repr(want) if want else "more",
                                                             "the end" if tok is None else repr(tok)))
        self.i += 1
        return tok

    def name(self):
        tok = self.take()
        if not re.match(r"^[A-Za-z_]", tok):
            raise SignatureError("expected a name, found %r" % tok)
        return tok

    def type(self):
        members = [self.member()]
        while self.peek() == "|":
            self.take("|")
            members.append(self.member())
        return members[0] if len(members) == 1 else ("union", members)

    def member(self):
        t = self.primary()
        while True:
            if self.peek() == "[" and self.peek(1) == "]":
                self.i += 2
                t = ("list", t)
            elif self.peek() == "?":
                self.take("?")
                if t[0] == "opt":
                    raise SignatureError("'??' is the same as '?'")
                t = ("opt", t)
            else:
                return t

    def primary(self):
        tok = self.take()
        if tok in SCALARS:
            return (tok,)
        if tok == "(":
            t = self.type()
            self.take(")")
            return t
        if tok == "[":
            items = [self.type()]
            while self.peek() == ",":
                self.take(",")
                items.append(self.type())
            self.take("]")
            if len(items) < 2:
                raise SignatureError("a tuple has two or more types; a list is T[]")
            return ("tuple", items)
        if tok == "{":
            if self.take() != "string":
                raise SignatureError("map keys are strings: {string: T}")
            self.take(":")
            t = self.type()
            self.take("}")
            return ("map", t)
        if tok == "record":
            self.take("{")
            fields, seen = [], set()
            while True:
                name = self.name()
                optional = self.peek() == "?"
                if optional:
                    self.take("?")
                self.take(":")
                if name in seen:
                    raise SignatureError("record field %r appears twice" % name)
                seen.add(name)
                fields.append((name, optional, self.type()))
                if self.peek() == "}":
                    break
                self.take(",")
            self.take("}")
            return ("record", fields)
        if tok == "void":
            raise SignatureError("void is only a method's return type")
        raise SignatureError("unknown type %r" % tok)

    def declaration(self):
        name = self.name()
        self.take("(")
        params, seen = [], set()
        while self.peek() not in (")", None):
            if params:
                self.take(",")
            pname = self.name()
            self.take(":")
            if pname in seen:
                raise SignatureError("parameter %r appears twice" % pname)
            seen.add(pname)
            params.append((pname, self.type()))
        self.take(")")
        returns = None
        if self.peek() == "->":
            self.take("->")
            if self.peek() == "void" and self.peek(1) is None:
                self.take()
                returns = ("void",)
            else:
                returns = self.type()
        if self.peek() is not None:
            raise SignatureError("unexpected %r after the declaration" % self.peek())
        return Signature(name, params, returns)


def parse(text, kind):
    """Parse the body of a ```signature block for a pack of `kind` ('func' or 'ops')."""
    decls = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            decls.append(_Parser(line).declaration())
        except SignatureError as exc:
            raise SignatureError("line %d: %s" % (n, exc))
    if not decls:
        raise SignatureError("the block is empty")
    if kind == "func":
        if len(decls) != 1:
            raise SignatureError("a func pack has one declaration, found %d" % len(decls))
        if decls[0].returns in (None, ("void",)):
            raise SignatureError("%s needs a return type" % decls[0].name)
        return decls[0]
    ctor, methods = decls[0], decls[1:]
    if ctor.returns is not None:
        raise SignatureError("the first line is the constructor and has no return type")
    seen = set()
    for m in methods:
        if m.returns is None:
            raise SignatureError("method %s needs a return type (void when it returns nothing)" % m.name)
        if m.name in seen:
            raise SignatureError("method %s appears twice" % m.name)
        seen.add(m.name)
    return Signature(ctor.name, ctor.params, None, methods)


def fmt(t):
    """Canonical text of a parsed type."""
    tag = t[0]
    if tag in SCALARS or tag == "void":
        return tag
    if tag == "list":
        inner = fmt(t[1])
        return ("(%s)[]" if t[1][0] == "union" else "%s[]") % inner
    if tag == "opt":
        inner = fmt(t[1])
        return ("(%s)?" if t[1][0] == "union" else "%s?") % inner
    if tag == "tuple":
        return "[%s]" % ", ".join(fmt(x) for x in t[1])
    if tag == "map":
        return "{string: %s}" % fmt(t[1])
    if tag == "record":
        return "record{%s}" % ", ".join("%s%s: %s" % (n, "?" if o else "", fmt(x)) for n, o, x in t[1])
    return " | ".join(fmt(x) for x in t[1])


# -------------------------------------------------------------- value check

def _kind(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool %s" % ("true" if v else "false")
    if isinstance(v, (int, float, str)):
        return "%s %s" % (type(v).__name__.replace("str", "string"), repr(v)[:30])
    return "list" if isinstance(v, list) else "object" if isinstance(v, dict) else type(v).__name__


def check(value, t, where="value"):
    """None when `value` (decoded JSON) has type `t`, else a message naming the first place that differs."""
    tag = t[0]
    bad = "%s: expected %s, got %s" % (where, fmt(t), _kind(value))
    if tag == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            return bad
        return None if INT_MIN <= value <= INT_MAX else "%s: %d does not fit a 64-bit int" % (where, value)
    if tag == "float":
        return None if isinstance(value, (int, float)) and not isinstance(value, bool) else bad
    if tag == "bool":
        return None if isinstance(value, bool) else bad
    if tag == "string":
        return None if isinstance(value, str) else bad
    if tag == "void":
        return None if value is None else bad
    if tag == "opt":
        return None if value is None else check(value, t[1], where)
    if tag == "union":
        return None if any(check(value, m, where) is None for m in t[1]) else bad
    if tag == "list":
        if not isinstance(value, list):
            return bad
        for i, x in enumerate(value):
            msg = check(x, t[1], "%s[%d]" % (where, i))
            if msg:
                return msg
        return None
    if tag == "tuple":
        if not isinstance(value, list) or len(value) != len(t[1]):
            return bad if not isinstance(value, list) else "%s: expected %d items, got %d" % (
                where, len(t[1]), len(value))
        for i, (x, it) in enumerate(zip(value, t[1])):
            msg = check(x, it, "%s[%d]" % (where, i))
            if msg:
                return msg
        return None
    if tag == "map":
        if not isinstance(value, dict):
            return bad
        for k, x in value.items():
            msg = check(x, t[1], "%s[%r]" % (where, k))
            if msg:
                return msg
        return None
    if tag == "record":
        if not isinstance(value, dict):
            return bad
        names = {n for n, _o, _t in t[1]}
        extra = sorted(set(value) - names)
        if extra:
            return "%s: key %r is not in %s" % (where, extra[0], fmt(t))
        for n, optional, ft in t[1]:
            if n not in value:
                if not optional:
                    return "%s: key %r is missing" % (where, n)
                continue
            msg = check(value[n], ft, "%s.%s" % (where, n))
            if msg:
                return msg
        return None
    raise ValueError("unknown type tag %r" % tag)


def check_call(sig, kind, args, result, where):
    """Check one test input and the oracle's result against the signature. Returns the first message or None.

    func: `args` is the case's args object. ops: `args` is {"calls": [...]} and `result` the list of returns."""
    if kind == "func":
        if not isinstance(args, dict):
            return "%s: args is not an object" % where
        for name, t in sig.params:
            if name not in args:
                return "%s: argument %r is missing" % (where, name)
            msg = check(args[name], t, "%s %s" % (where, name))
            if msg:
                return msg
        extra = sorted(set(args) - {n for n, _t in sig.params})
        if extra:
            return "%s: argument %r is not in the signature" % (where, extra[0])
        return check(result, sig.returns, "%s result" % where)
    calls = args.get("calls") if isinstance(args, dict) else None
    if not isinstance(calls, list) or not calls:
        return "%s: no calls" % where
    for i, call in enumerate(calls):
        name, cargs = call[0], call[1]
        decl = sig if i == 0 else sig.method(name)
        if decl is None:
            return "%s call %d: %s is not a method in the signature" % (where, i, name)
        if len(cargs) != len(decl.params):
            return "%s call %d: %s takes %d arguments, got %d" % (where, i, name, len(decl.params), len(cargs))
        for (pname, t), v in zip(decl.params, cargs):
            msg = check(v, t, "%s call %d %s(%s)" % (where, i, name, pname))
            if msg:
                return msg
        if i and result is not None:
            msg = check(result[i], decl.returns, "%s call %d %s() result" % (where, i, name))
            if msg:
                return msg
    return None
