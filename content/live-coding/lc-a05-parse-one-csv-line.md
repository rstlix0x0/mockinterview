---
id: lc-a05-parse-one-csv-line
title: Parse One CSV Line
type: live-coding
level: [junior]
tags: [parsing, state-machine]
time_minutes: 20
entry: parse_csv_line
kind: func
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

## Signature

```signature
parse_csv_line(line: string) -> string[]?
```

## Tests

```json tests
{"function":"parse_csv_line","kind":"func","compare":"exact","cases":[
{"name":"example-1","tags":["visible"],"args":{"line":"a,b,c"},"expected":["a","b","c"]},
{"name":"example-2","tags":["visible"],"args":{"line":"a,\"b,c\",d"},"expected":["a","b,c","d"]},
{"name":"example-3","tags":["visible"],"args":{"line":"\"say \"\"hi\"\"\",x"},"expected":["say \"hi\"","x"]},
{"name":"example-4","tags":["visible"],"args":{"line":"\"abc"},"expected":null},
{"name":"edge-empty-line","tags":["edge"],"args":{"line":""},"expected":[""]},
{"name":"edge-trailing-comma","tags":["edge"],"args":{"line":"a,"},"expected":["a",""]},
{"name":"edge-only-commas","tags":["edge"],"args":{"line":",,"},"expected":["","",""]},
{"name":"edge-empty-quoted","tags":["edge"],"args":{"line":"\"\""},"expected":[""]},
{"name":"hidden-spaces-kept","tags":["hidden"],"args":{"line":" a , b "},"expected":[" a "," b "]},
{"name":"hidden-junk-after-quote","tags":["hidden"],"args":{"line":"\"a\"b,c"},"expected":null},
{"name":"hidden-quote-in-plain","tags":["hidden"],"args":{"line":"a\"b"},"expected":null},
{"name":"hidden-escaped-at-end","tags":["hidden"],"args":{"line":"\"a\"\"\""},"expected":["a\""]},
{"name":"random-1","tags":["hidden"],"args":{"line":",,\"\""},"expected":["","",""]},
{"name":"random-2","tags":["hidden"],"args":{"line":"\"\"\",a\""},"expected":["\",a"]},
{"name":"random-3","tags":["hidden"],"args":{"line":"\"a a\"\"\""},"expected":["a a\""]},
{"name":"random-4","tags":["hidden"],"args":{"line":"\"b,,\""},"expected":["b,,"]}
]}
```

## Reference solution

```python reference
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
