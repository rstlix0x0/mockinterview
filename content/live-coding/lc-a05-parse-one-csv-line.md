---
id: lc-a05-parse-one-csv-line
title: Parse One CSV Line
type: live-coding
level: [junior]
tags: [parsing, state-machine]
time_minutes: 20
languages: [python]
entry: parse_csv_line
kind: func
runs_code: true
source: adapted
author: mockinterview
legacy_id: A5
---

# Parse One CSV Line

## Statement

Split one CSV record into fields, following these rules:

- Fields are separated by commas. An empty line is one empty field; a trailing comma adds a final empty field.
- A field may be wrapped in double quotes. Inside a quoted field a comma is literal and `""` stands for one `"` character.
- A quote is only allowed as the first character of a field (opening a quoted field) or inside a quoted field.
- Return `null` for malformed input: an unterminated quote, a quote inside an unquoted field, or any character between a closing quote and the next comma.
- Do not trim whitespace.

**Signature:** `parse_csv_line(line: string) -> string[] | null`

**Constraints:**
- 0 <= len(line) <= 100000
- no newline characters

**Examples:**

- **Example 1** - input: `{"line":"a,b,c"}`  
  output: `["a","b","c"]`
- **Example 2** - input: `{"line":"a,\"b,c\",d"}`  
  output: `["a","b,c","d"]`
- **Example 3** - input: `{"line":"\"say \"\"hi\"\"\",x"}`  
  output: `["say \"hi\"","x"]`
- **Example 4** - input: `{"line":"\"abc"}`  
  output: `null`

## Stub

```python
def parse_csv_line(line):
    """parse_csv_line(line: string) -> string[] | null"""
    raise NotImplementedError
```

## Signature

```signature
parse_csv_line(line: string) -> string[]?
```

## Tests

```json tests
{"function":"parse_csv_line","kind":"func","compare":"exact","fuzz":20,"cases":[
{"name":"example-1","tags":["visible"],"args":{"line":"a,b,c"}},
{"name":"example-2","tags":["visible"],"args":{"line":"a,\"b,c\",d"}},
{"name":"example-3","tags":["visible"],"args":{"line":"\"say \"\"hi\"\"\",x"}},
{"name":"example-4","tags":["visible"],"args":{"line":"\"abc"}},
{"name":"edge-empty-line","tags":["edge"],"args":{"line":""}},
{"name":"edge-trailing-comma","tags":["edge"],"args":{"line":"a,"}},
{"name":"edge-only-commas","tags":["edge"],"args":{"line":",,"}},
{"name":"edge-empty-quoted","tags":["edge"],"args":{"line":"\"\""}},
{"name":"hidden-spaces-kept","tags":["hidden"],"args":{"line":" a , b "}},
{"name":"hidden-junk-after-quote","tags":["hidden"],"args":{"line":"\"a\"b,c"}},
{"name":"hidden-quote-in-plain","tags":["hidden"],"args":{"line":"a\"b"}},
{"name":"hidden-escaped-at-end","tags":["hidden"],"args":{"line":"\"a\"\"\""}}
]}
```

## Oracle

```python oracle
def solve(line):
    fields, cur = [], []
    i, n = 0, len(line)
    while True:
        if i < n and line[i] == '"':
            i += 1
            while True:
                if i >= n:
                    return None
                if line[i] == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        cur.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    cur.append(line[i])
                    i += 1
            if i < n and line[i] != ',':
                return None
        else:
            while i < n and line[i] != ',':
                if line[i] == '"':
                    return None
                cur.append(line[i])
                i += 1
        fields.append(''.join(cur))
        cur = []
        if i >= n:
            return fields
        i += 1

def gen_random(seed):
    rnd = random.Random(seed)
    if rnd.random() < 0.25:
        return {"line": rnd.choice(['"abc', 'a"b', '"a"b', 'x,"y', '"a""', ',"', 'a,"b"c,d'])}
    fields = [''.join(rnd.choice('ab ,"') for _ in range(rnd.randint(0, 4))) for _ in range(rnd.randint(1, 4))]
    enc = []
    for f in fields:
        if any(c in f for c in ',"') or rnd.random() < 0.3:
            enc.append('"' + f.replace('"', '""') + '"')
        else:
            enc.append(f)
    return {"line": ','.join(enc)}
```

## Interviewer notes

- **Target complexity:** O(n) time and space
- **Clarifying questions (answer verbatim):**
  - Q: Multi-line fields?  
    A: Out of scope. Lines never contain newlines.
  - Q: Should I trim spaces?  
    A: No.
- **Hint ladder:**
  - H0 (free): Which states can the parser be in?
  - H1 (-5): Not-in-quotes, in-quotes, and just-closed-a-quote.
  - H2 (-10): In quotes, a quote followed by a quote is a literal; otherwise it closes the field.
  - H3 (-20): After closing, only a comma or the end of input is legal.
- **Follow-ups:**
  - Support quoted fields that contain newlines across a stream of lines.
  - Write the encoder and prove parse(encode(x)) == x.
- **Mistakes the tests are built to catch:**
  - Using split(',') and breaking on quoted commas.
  - Dropping the trailing empty field.
  - Accepting a quote in the middle of an unquoted field.
