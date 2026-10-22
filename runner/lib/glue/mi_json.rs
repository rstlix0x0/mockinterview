// Written by mockinterview: a small JSON reader and writer for the glue, so the project needs no
// dependencies. DO NOT EDIT: the runner rewrites it on every run.
#![allow(dead_code)]

use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(String),
    Arr(Vec<Json>),
    Obj(Vec<(String, Json)>),
}

impl Json {
    pub fn get(&self, key: &str) -> &Json {
        match self {
            Json::Obj(items) => items.iter().find(|(k, _)| k == key).map(|(_, v)| v).unwrap_or(&Json::Null),
            _ => &Json::Null,
        }
    }

    pub fn has(&self, key: &str) -> bool {
        matches!(self, Json::Obj(items) if items.iter().any(|(k, _)| k == key))
    }

    pub fn arr(&self) -> &Vec<Json> {
        match self {
            Json::Arr(a) => a,
            other => panic!("mockinterview: expected a JSON array, got {:?}", other),
        }
    }

    pub fn dump(&self) -> String {
        let mut out = String::new();
        self.write(&mut out);
        out
    }

    fn write(&self, out: &mut String) {
        match self {
            Json::Null => out.push_str("null"),
            Json::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            Json::Int(n) => out.push_str(&n.to_string()),
            Json::Float(f) => {
                if f.is_finite() {
                    out.push_str(&format!("{:?}", f))
                } else {
                    out.push_str("null")
                }
            }
            Json::Str(s) => write_str(s, out),
            Json::Arr(a) => {
                out.push('[');
                for (i, x) in a.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    x.write(out);
                }
                out.push(']');
            }
            Json::Obj(items) => {
                out.push('{');
                for (i, (k, v)) in items.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    write_str(k, out);
                    out.push(':');
                    v.write(out);
                }
                out.push('}');
            }
        }
    }
}

fn write_str(s: &str, out: &mut String) {
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
}

pub fn parse(text: &str) -> Result<Json, String> {
    let mut p = Parser { s: text.as_bytes(), i: 0 };
    let v = p.value()?;
    p.ws();
    if p.i != p.s.len() {
        return Err(format!("trailing data at byte {}", p.i));
    }
    Ok(v)
}

struct Parser<'a> {
    s: &'a [u8],
    i: usize,
}

impl<'a> Parser<'a> {
    fn ws(&mut self) {
        while self.i < self.s.len() && matches!(self.s[self.i], b' ' | b'\n' | b'\r' | b'\t') {
            self.i += 1;
        }
    }

    fn lit(&mut self, word: &str, v: Json) -> Result<Json, String> {
        if self.s[self.i..].starts_with(word.as_bytes()) {
            self.i += word.len();
            Ok(v)
        } else {
            Err(format!("bad literal at byte {}", self.i))
        }
    }

    fn value(&mut self) -> Result<Json, String> {
        self.ws();
        match self.s.get(self.i) {
            None => Err("unexpected end".into()),
            Some(b'n') => self.lit("null", Json::Null),
            Some(b't') => self.lit("true", Json::Bool(true)),
            Some(b'f') => self.lit("false", Json::Bool(false)),
            Some(b'"') => Ok(Json::Str(self.string()?)),
            Some(b'[') => {
                self.i += 1;
                let mut items = Vec::new();
                self.ws();
                if self.s.get(self.i) == Some(&b']') {
                    self.i += 1;
                    return Ok(Json::Arr(items));
                }
                loop {
                    items.push(self.value()?);
                    self.ws();
                    match self.s.get(self.i) {
                        Some(b',') => self.i += 1,
                        Some(b']') => {
                            self.i += 1;
                            return Ok(Json::Arr(items));
                        }
                        _ => return Err(format!("expected , or ] at byte {}", self.i)),
                    }
                }
            }
            Some(b'{') => {
                self.i += 1;
                let mut items = Vec::new();
                self.ws();
                if self.s.get(self.i) == Some(&b'}') {
                    self.i += 1;
                    return Ok(Json::Obj(items));
                }
                loop {
                    self.ws();
                    let k = self.string()?;
                    self.ws();
                    if self.s.get(self.i) != Some(&b':') {
                        return Err(format!("expected : at byte {}", self.i));
                    }
                    self.i += 1;
                    items.push((k, self.value()?));
                    self.ws();
                    match self.s.get(self.i) {
                        Some(b',') => self.i += 1,
                        Some(b'}') => {
                            self.i += 1;
                            return Ok(Json::Obj(items));
                        }
                        _ => return Err(format!("expected , or }} at byte {}", self.i)),
                    }
                }
            }
            Some(_) => self.number(),
        }
    }

    fn number(&mut self) -> Result<Json, String> {
        let start = self.i;
        let mut float = false;
        while self.i < self.s.len() {
            match self.s[self.i] {
                b'0'..=b'9' | b'-' | b'+' => {}
                b'.' | b'e' | b'E' => float = true,
                _ => break,
            }
            self.i += 1;
        }
        let text = std::str::from_utf8(&self.s[start..self.i]).unwrap();
        if !float {
            if let Ok(n) = text.parse::<i64>() {
                return Ok(Json::Int(n));
            }
        }
        text.parse::<f64>().map(Json::Float).map_err(|_| format!("bad number {:?}", text))
    }

    fn hex4(&mut self) -> Result<u32, String> {
        let h = self.s.get(self.i..self.i + 4).ok_or("short \\u escape")?;
        self.i += 4;
        u32::from_str_radix(std::str::from_utf8(h).unwrap(), 16).map_err(|e| e.to_string())
    }

    fn string(&mut self) -> Result<String, String> {
        if self.s.get(self.i) != Some(&b'"') {
            return Err(format!("expected a string at byte {}", self.i));
        }
        self.i += 1;
        let mut buf: Vec<u8> = Vec::new();
        loop {
            let c = *self.s.get(self.i).ok_or("unterminated string")?;
            self.i += 1;
            match c {
                b'"' => return String::from_utf8(buf).map_err(|e| e.to_string()),
                b'\\' => {
                    let e = *self.s.get(self.i).ok_or("bad escape")?;
                    self.i += 1;
                    let ch = match e {
                        b'"' => '"',
                        b'\\' => '\\',
                        b'/' => '/',
                        b'b' => '\u{8}',
                        b'f' => '\u{c}',
                        b'n' => '\n',
                        b'r' => '\r',
                        b't' => '\t',
                        b'u' => {
                            let mut cp = self.hex4()?;
                            if (0xD800..0xDC00).contains(&cp) && self.s[self.i..].starts_with(b"\\u") {
                                self.i += 2;
                                let lo = self.hex4()?;
                                cp = 0x10000 + ((cp - 0xD800) << 10) + (lo.wrapping_sub(0xDC00) & 0x3FF);
                            }
                            char::from_u32(cp).unwrap_or('\u{FFFD}')
                        }
                        _ => return Err("bad escape".into()),
                    };
                    let mut tmp = [0u8; 4];
                    buf.extend_from_slice(ch.encode_utf8(&mut tmp).as_bytes());
                }
                c => buf.push(c),
            }
        }
    }
}

// ------------------------------------------------------------- conversions

pub trait FromJson: Sized {
    fn from_json(v: &Json) -> Self;
}

pub trait ToJson {
    fn to_json(&self) -> Json;
}

impl FromJson for i64 {
    fn from_json(v: &Json) -> Self {
        match v {
            Json::Int(n) => *n,
            other => panic!("mockinterview: expected an int, got {:?}", other),
        }
    }
}

impl FromJson for f64 {
    fn from_json(v: &Json) -> Self {
        match v {
            Json::Int(n) => *n as f64,
            Json::Float(f) => *f,
            other => panic!("mockinterview: expected a float, got {:?}", other),
        }
    }
}

impl FromJson for bool {
    fn from_json(v: &Json) -> Self {
        match v {
            Json::Bool(b) => *b,
            other => panic!("mockinterview: expected a bool, got {:?}", other),
        }
    }
}

impl FromJson for String {
    fn from_json(v: &Json) -> Self {
        match v {
            Json::Str(s) => s.clone(),
            other => panic!("mockinterview: expected a string, got {:?}", other),
        }
    }
}

impl<T: FromJson> FromJson for Vec<T> {
    fn from_json(v: &Json) -> Self {
        v.arr().iter().map(T::from_json).collect()
    }
}

impl<T: FromJson> FromJson for Option<T> {
    fn from_json(v: &Json) -> Self {
        match v {
            Json::Null => None,
            other => Some(T::from_json(other)),
        }
    }
}

impl<T: FromJson> FromJson for HashMap<String, T> {
    fn from_json(v: &Json) -> Self {
        match v {
            Json::Obj(items) => items.iter().map(|(k, x)| (k.clone(), T::from_json(x))).collect(),
            other => panic!("mockinterview: expected an object, got {:?}", other),
        }
    }
}

impl<A: FromJson, B: FromJson> FromJson for (A, B) {
    fn from_json(v: &Json) -> Self {
        let a = v.arr();
        (A::from_json(&a[0]), B::from_json(&a[1]))
    }
}

impl<A: FromJson, B: FromJson, C: FromJson> FromJson for (A, B, C) {
    fn from_json(v: &Json) -> Self {
        let a = v.arr();
        (A::from_json(&a[0]), B::from_json(&a[1]), C::from_json(&a[2]))
    }
}

impl<A: FromJson, B: FromJson, C: FromJson, D: FromJson> FromJson for (A, B, C, D) {
    fn from_json(v: &Json) -> Self {
        let a = v.arr();
        (A::from_json(&a[0]), B::from_json(&a[1]), C::from_json(&a[2]), D::from_json(&a[3]))
    }
}

impl ToJson for () {
    fn to_json(&self) -> Json {
        Json::Null
    }
}

impl ToJson for i64 {
    fn to_json(&self) -> Json {
        Json::Int(*self)
    }
}

impl ToJson for f64 {
    fn to_json(&self) -> Json {
        Json::Float(*self)
    }
}

impl ToJson for bool {
    fn to_json(&self) -> Json {
        Json::Bool(*self)
    }
}

impl ToJson for String {
    fn to_json(&self) -> Json {
        Json::Str(self.clone())
    }
}

impl<T: ToJson> ToJson for Vec<T> {
    fn to_json(&self) -> Json {
        Json::Arr(self.iter().map(|x| x.to_json()).collect())
    }
}

impl<T: ToJson> ToJson for Option<T> {
    fn to_json(&self) -> Json {
        match self {
            None => Json::Null,
            Some(x) => x.to_json(),
        }
    }
}

impl<T: ToJson> ToJson for HashMap<String, T> {
    fn to_json(&self) -> Json {
        Json::Obj(self.iter().map(|(k, x)| (k.clone(), x.to_json())).collect())
    }
}

impl<A: ToJson, B: ToJson> ToJson for (A, B) {
    fn to_json(&self) -> Json {
        Json::Arr(vec![self.0.to_json(), self.1.to_json()])
    }
}

impl<A: ToJson, B: ToJson, C: ToJson> ToJson for (A, B, C) {
    fn to_json(&self) -> Json {
        Json::Arr(vec![self.0.to_json(), self.1.to_json(), self.2.to_json()])
    }
}

impl<A: ToJson, B: ToJson, C: ToJson, D: ToJson> ToJson for (A, B, C, D) {
    fn to_json(&self) -> Json {
        Json::Arr(vec![self.0.to_json(), self.1.to_json(), self.2.to_json(), self.3.to_json()])
    }
}
