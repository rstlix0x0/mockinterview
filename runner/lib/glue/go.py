"""Go glue: `mi_main.go` (package main) beside the engineer's `solution.go`.

Types: int -> int, float -> float64, T[] -> []T, T? -> *T (a slice, map or union is nil instead), tuples and
records -> named structs, {string: T} -> map[string]T, unions of scalars -> any. A nil slice or map is written
as [] or {} unless the signature allows null there. Functions are camelCase (twoSum), a class gets a
constructor NewName and exported methods (GetMin).
"""
from . import Unsupported, all_types, camel, named_types, pascal
from ..signature import SCALARS, fmt

KEYWORDS = {"break", "case", "chan", "const", "continue", "default", "defer", "else", "fallthrough", "for", "func",
            "go", "goto", "if", "import", "interface", "map", "package", "range", "return", "select", "struct",
            "switch", "type", "var"}
SCALAR_GO = {"int": "int", "float": "float64", "bool": "bool", "string": "string"}
SCALAR_DEC = {"int": "miInt", "float": "miFloat", "bool": "miBool", "string": "miString"}
NILABLE = ("list", "map", "union")

HELPERS = '''
func miInt(v any) int {
	n, err := v.(json.Number).Int64()
	if err != nil {
		panic("mockinterview: not an int: " + v.(json.Number).String())
	}
	return int(n)
}

func miFloat(v any) float64 {
	f, _ := v.(json.Number).Float64()
	return f
}

func miBool(v any) bool     { return v.(bool) }
func miString(v any) string { return v.(string) }

func main() {
	defer func() {
		if r := recover(); r != nil {
			where := ""
			for _, line := range strings.Split(string(debug.Stack()), "\\n") {
				if strings.Contains(line, "/solution.go:") {
					file := strings.Fields(line)[0]
					where = " at " + file[strings.LastIndex(file, "/")+1:]
					break
				}
			}
			fmt.Fprintf(os.Stderr, "panic: %v%s\\n", r, where)
			os.Exit(1)
		}
	}()
	dec := json.NewDecoder(os.Stdin)
	dec.UseNumber()
	var req map[string]any
	if err := dec.Decode(&req); err != nil {
		fmt.Fprintln(os.Stderr, "mockinterview: bad request:", err)
		os.Exit(2)
	}
	data, err := json.Marshal(miCall(req))
	if err != nil {
		fmt.Fprintln(os.Stderr, "the result cannot be written as JSON:", err)
		os.Exit(1)
	}
	if err := os.WriteFile(os.Args[1], data, 0o644); err != nil {
		fmt.Fprintln(os.Stderr, "mockinterview:", err)
		os.Exit(2)
	}
}
'''


def _tname(t):
    """A type spelled for a structural name: [string, int] -> TupleStringInt."""
    tag = t[0]
    if tag in SCALARS:
        return pascal(tag)
    return {"list": lambda: _tname(t[1]) + "List", "opt": lambda: "Opt" + _tname(t[1]),
            "map": lambda: _tname(t[1]) + "Map", "tuple": lambda: "Tuple", "record": lambda: "Record",
            "union": lambda: "Any"}[tag]()


def ident(name):
    """A parameter name: begin_word -> beginWord; a Go keyword gets a trailing underscore."""
    n = camel(name)
    return n + "_" if n in KEYWORDS else n


class Go:
    file = "mi_main.go"

    # ------------------------------------------------------------- checks
    def check(self, sig):
        for t, ctx in all_types(sig):
            if t[0] == "union":
                bad = [fmt(m) for m in t[1] if m[0] not in SCALARS]
                if bad:
                    raise Unsupported("Go glue supports unions of int, float, bool and string only (%s)" % fmt(t))
            if t[0] == "record":
                for name, optional, ft in t[1]:
                    if optional and ft[0] == "opt":
                        raise Unsupported("Go cannot tell an absent field from a null one (%s?: %s)"
                                          % (name, fmt(ft)))

    # -------------------------------------------------------------- types
    def _setup(self, sig):
        self.check(sig)
        self.names = named_types(sig, ("record", "tuple"),
                                 structural=lambda t: "Tuple" + "".join(_tname(m) for m in t[1])
                                 if t[0] == "tuple" else None, reserved=(sig.name,))
        self.funcs, self.order, self.decls = {}, [], []

    def gt(self, t):
        tag = t[0]
        if tag in SCALAR_GO:
            return SCALAR_GO[tag]
        if tag == "list":
            return "[]" + self.gt(t[1])
        if tag == "opt":
            return self.gt(t[1]) if t[1][0] in NILABLE else "*" + self.gt(t[1])
        if tag == "map":
            return "map[string]" + self.gt(t[1])
        if tag == "union":
            return "any"
        return self.names[fmt(t)]

    def field_type(self, optional, t):
        return "*" + self.gt(t) if optional and t[0] not in NILABLE else self.gt(t)

    def _fn(self, kind, t, body):
        key = (kind, fmt(t))
        if key not in self.funcs:
            name = "mi%s%d" % (kind, len(self.funcs) + 1)
            self.funcs[key] = name
            self.order.append((name, kind, t, body))
        return self.funcs[key]

    def dec(self, t):
        """Name of a function any -> the Go type of t."""
        if t[0] in SCALAR_DEC:
            return SCALAR_DEC[t[0]]
        return self._fn("Dec", t, None)

    def enc(self, t, x):
        """Go expression turning x (of the Go type of t) into a value for json.Marshal."""
        if t[0] in SCALAR_GO:
            return x
        return "%s(%s)" % (self._fn("Enc", t, None), x)

    def _body(self, name, kind, t):
        gt, tag = self.gt(t), t[0]
        if kind == "Dec":
            head = "func %s(v any) %s {\n" % (name, gt)
            if tag == "list":
                body = ("\ta := v.([]any)\n\tout := make(%s, len(a))\n\tfor i, x := range a {\n"
                        "\t\tout[i] = %s(x)\n\t}\n\treturn out\n" % (gt, self.dec(t[1])))
            elif tag == "opt" and t[1][0] in NILABLE:
                body = "\tif v == nil {\n\t\treturn nil\n\t}\n\treturn %s(v)\n" % self.dec(t[1])
            elif tag == "opt":
                body = "\tif v == nil {\n\t\treturn nil\n\t}\n\tx := %s(v)\n\treturn &x\n" % self.dec(t[1])
            elif tag == "map":
                body = ("\tm := v.(map[string]any)\n\tout := make(%s, len(m))\n\tfor k, x := range m {\n"
                        "\t\tout[k] = %s(x)\n\t}\n\treturn out\n" % (gt, self.dec(t[1])))
            elif tag == "tuple":
                body = "\ta := v.([]any)\n\treturn %s{%s}\n" % (
                    gt, ", ".join("%s(a[%d])" % (self.dec(m), i) for i, m in enumerate(t[1])))
            elif tag == "record":
                lines = ["\tm := v.(map[string]any)\n\tvar out %s\n" % gt]
                for fname, optional, ft in t[1]:
                    field = pascal(fname)
                    if not optional:
                        lines.append('\tout.%s = %s(m["%s"])\n' % (field, self.dec(ft), fname))
                    elif ft[0] in NILABLE:
                        lines.append('\tif x, ok := m["%s"]; ok {\n\t\tout.%s = %s(x)\n\t}\n'
                                     % (fname, field, self.dec(ft)))
                    else:
                        lines.append('\tif x, ok := m["%s"]; ok {\n\t\ty := %s(x)\n\t\tout.%s = &y\n\t}\n'
                                     % (fname, self.dec(ft), field))
                body = "".join(lines) + "\treturn out\n"
            else:  # union of scalars
                members = [m[0] for m in t[1]]
                cases = []
                if "int" in members or "float" in members:
                    num = "\tcase json.Number:\n"
                    if "int" in members:
                        num += "\t\tif n, err := x.Int64(); err == nil {\n\t\t\treturn int(n)\n\t\t}\n"
                    if "float" in members:
                        num += "\t\tf, _ := x.Float64()\n\t\treturn f\n"
                    cases.append(num)
                if "string" in members:
                    cases.append("\tcase string:\n\t\treturn x\n")
                if "bool" in members:
                    cases.append("\tcase bool:\n\t\treturn x\n")
                body = "\tswitch x := v.(type) {\n%s\t}\n\tpanic(\"mockinterview: bad value for %s\")\n" % (
                    "".join(cases), fmt(t))
            return head + body + "}\n"
        head = "func %s(x %s) any {\n" % (name, gt)
        if tag == "list":
            body = ("\tout := make([]any, len(x))\n\tfor i, e := range x {\n\t\tout[i] = %s\n\t}\n\treturn out\n"
                    % self.enc(t[1], "e"))
        elif tag == "opt":
            inner = "x" if t[1][0] in NILABLE else "*x"
            body = "\tif x == nil {\n\t\treturn nil\n\t}\n\treturn %s\n" % self.enc(t[1], inner)
        elif tag == "map":
            body = ("\tout := make(map[string]any, len(x))\n\tfor k, e := range x {\n\t\tout[k] = %s\n\t}\n"
                    "\treturn out\n" % self.enc(t[1], "e"))
        elif tag == "tuple":
            body = "\treturn []any{%s}\n" % ", ".join(self.enc(m, "x.V%d" % i) for i, m in enumerate(t[1]))
        elif tag == "record":
            lines = ["\tout := map[string]any{}\n"]
            for fname, optional, ft in t[1]:
                field = "x." + pascal(fname)
                if not optional:
                    lines.append('\tout["%s"] = %s\n' % (fname, self.enc(ft, field)))
                else:
                    inner = field if ft[0] in NILABLE else "*" + field
                    lines.append('\tif %s != nil {\n\t\tout["%s"] = %s\n\t}\n' % (field, fname, self.enc(ft, inner)))
            body = "".join(lines) + "\treturn out\n"
        else:  # union of scalars
            members = [m[0] for m in t[1]]
            gotypes = [SCALAR_GO[m] for m in members]
            if "float" in members and "int" not in members:
                gotypes.append("int")
            body = ("\tswitch x.(type) {\n\tcase %s:\n\t\treturn x\n\t}\n"
                    "\tpanic(fmt.Sprintf(\"returned %%T (%%v); the signature allows %s\", x, x))\n"
                    % (", ".join(gotypes), fmt(t)))
        return head + body + "}\n"

    def _type_decls(self, sig):
        out, seen = [], set()
        for t, _ctx in all_types(sig):
            key = fmt(t)
            if t[0] not in ("record", "tuple") or key in seen:
                continue
            seen.add(key)
            name = self.names[key]
            if t[0] == "tuple":
                fields = [("V%d" % i, self.gt(m)) for i, m in enumerate(t[1])]
                doc = "// %s is the tuple %s, a JSON array.\n" % (name, key)
            else:
                fields = [(pascal(n), self.field_type(o, ft)) for n, o, ft in t[1]]
                doc = "// %s is %s; a nil field is absent.\n" % (name, key) if any(o for _n, o, _t in t[1]) \
                    else "// %s is %s.\n" % (name, key)
            width = max(len(f) for f, _t in fields)
            out.append(doc + "type %s struct {\n%s}\n" % (
                name, "".join("\t%s %s\n" % (f.ljust(width), ft) for f, ft in fields)))
        return out

    # ---------------------------------------------------------- outputs
    def _params(self, decl):
        return ", ".join("%s %s" % (ident(n), self.gt(t)) for n, t in decl.params)

    def _ret(self, decl):
        return "" if decl.returns == ("void",) else " " + self.gt(decl.returns)

    def stub(self, sig, kind):
        self._setup(sig)
        head = "package main\n\n"
        if self.names:
            head += "// %s: defined in mi_main.go, which the runner rewrites on every run.\n\n" % ", ".join(
                sorted(self.names.values()))
        if kind == "func":
            return head + "func %s(%s)%s {\n\tpanic(\"not implemented\")\n}\n" % (
                camel(sig.name), self._params(sig), self._ret(sig))
        recv = sig.name[:1].lower()
        out = [head + "type %s struct {\n}\n\nfunc New%s(%s) *%s {\n\treturn &%s{}\n}\n"
               % (sig.name, sig.name, self._params(sig), sig.name, sig.name)]
        for m in sig.methods:
            r = "obj" if recv in {ident(n) for n, _t in m.params} else recv
            out.append("func (%s *%s) %s(%s)%s {\n\tpanic(\"not implemented\")\n}\n"
                       % (r, sig.name, pascal(m.name), self._params(m), self._ret(m)))
        return "\n".join(out)

    def files(self, sig, kind, pack_id, request_name):
        """{path in work/: content}. request_name(snake name) is how the request spells a method."""
        self._setup(sig)
        if kind == "func":
            args = ", ".join("%s(a[%d])" % (self.dec(t), i) for i, (_n, t) in enumerate(sig.params))
            call = "%s(%s)" % (camel(sig.name), args)
            body = "\ta := req[\"args\"].([]any)\n\t_ = a\n\treturn %s\n" % self.enc(sig.returns, call)
        else:
            ctor = ", ".join("%s(first[%d])" % (self.dec(t), i) for i, (_n, t) in enumerate(sig.params))
            cases = []
            for m in sig.methods:
                args = ", ".join("%s(a[%d])" % (self.dec(t), i) for i, (_n, t) in enumerate(m.params))
                call = "obj.%s(%s)" % (pascal(m.name), args)
                stmt = call if m.returns == ("void",) else "out[i] = %s" % self.enc(m.returns, call)
                cases.append("\t\tcase %s:\n\t\t\t%s\n" % (_q(request_name(m.name)), stmt))
            body = ("\tcalls := req[\"calls\"].([]any)\n\tout := make([]any, len(calls))\n"
                    "\tfirst := calls[0].([]any)[1].([]any)\n\t_ = first\n\tobj := New%s(%s)\n"
                    "\tfor i := 1; i < len(calls); i++ {\n\t\tc := calls[i].([]any)\n\t\ta := c[1].([]any)\n"
                    "\t\t_ = a\n\t\tswitch c[0].(string) {\n%s\t\tdefault:\n"
                    "\t\t\tpanic(\"unknown method \" + c[0].(string))\n\t\t}\n\t}\n\treturn out\n"
                    % (sig.name, ctor, "".join(cases)))
        call_fn = "func miCall(req map[string]any) any {\n%s}\n" % body
        funcs = []
        i = 0
        while i < len(self.order):  # bodies register further helpers as they are written
            name, kind_, t, _ = self.order[i]
            funcs.append(self._body(name, kind_, t))
            i += 1
        parts = ["// Code generated by mockinterview for %s. DO NOT EDIT: the runner rewrites it on every run.\n"
                 "\npackage main\n\nimport (\n\t\"encoding/json\"\n\t\"fmt\"\n\t\"os\"\n\t\"runtime/debug\"\n"
                 "\t\"strings\"\n)\n" % pack_id]
        parts += self._type_decls(sig)
        parts.append(call_fn)
        parts += funcs
        parts.append(HELPERS.lstrip("\n"))
        return {self.file: "\n".join(parts)}


def _q(s):
    return '"%s"' % s
