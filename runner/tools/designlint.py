#!/usr/bin/env python3
"""Structure check for a written design: did you cover what a senior answer must cover?

    python runner/tools/designlint.py work/design.md

It does NOT judge whether the design is good (the interviewer does that). It catches the omissions that cost
points in every round: a missing section, no numbers, no diagram, no stated trade-offs, Mermaid that will not render.
Exit code 1 if a required section is missing.
"""
import re
import sys

SECTIONS = [
    ("functional requirements", ("requirement", "scope", "functional", "use case")),
    ("non-functional requirements", ("non-functional", "nonfunctional", "nfr", "quality", "latency", "availability", "consistency")),
    ("estimation", ("estimat", "capacity", "back-of", "numbers", "scale")),
    ("API / interface", ("api", "interface", "endpoint", "contract")),
    ("data model", ("data model", "schema", "entities", "entity", "storage")),
    ("high-level design", ("high-level", "high level", "architecture", "components", "overview")),
    ("deep dives", ("deep dive", "deep-dive", "bottleneck", "hot spot")),
    ("trade-offs", ("trade-off", "tradeoff", "alternative", "decision", "why")),
    ("failure and scaling", ("failure", "reliab", "fault", "resilien", "scaling", "scalab", "operat")),
]
UNIT = re.compile(r"\d[\d.,]*\s*(?:%|(?:k|m|b|kb|mb|gb|tb|pb|qps|rps|tps|ms|µs|us|s|x)\b)", re.I)
TRADE_WORDS = re.compile(r"\b(because|trade-?off|instead of|alternative|versus|vs\.?|at the cost|downside|rather than|in exchange)\b", re.I)


def section_body(text, start, level):
    """Text after the heading at `start` up to the next heading of the same or a higher level (sub-headings are included)."""
    rest = text[start:].split("\n", 1)[1] if "\n" in text[start:] else ""
    m = re.search(r"^#{1,%d}\s" % level, rest, re.M)
    return rest[:m.start()] if m else rest


def real_words(body):
    """Words of actual content: template guidance in (parentheses), labels ending with a colon and code fences do not count."""
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    keep = [ln for ln in body.splitlines() if ln.strip() and not (ln.strip().startswith("(") and ln.strip().endswith(")"))
            and not ln.strip().endswith(":") and not ln.lstrip().startswith("#")]
    return len(re.findall(r"\w+", " ".join(keep)))


def lint(text):
    heads = [(m.start(), len(m.group(1)), m.group(2).strip().lower()) for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.M)]
    results, missing = [], 0
    for name, keys in SECTIONS:
        found = [(pos, lvl) for pos, lvl, h in heads if any(k in h for k in keys)]
        if not found:
            results.append(("MISSING", "section: " + name))
            missing += 1
        elif max(real_words(section_body(text, pos, lvl)) for pos, lvl in found) < 8:
            results.append(("EMPTY", "section: %s (heading present, fewer than 8 words of content)" % name))
            missing += 1
        else:
            results.append(("PASS", "section: " + name))
    blocks = re.findall(r"```mermaid\n(.*?)```", text, re.S)
    results.append(("PASS" if blocks else "WARN", "at least one Mermaid diagram (found %d)" % len(blocks)))
    if any("\\n" in b for b in blocks):
        results.append(("WARN", "a Mermaid block contains a literal backslash-n; use <br/> for line breaks"))
    nums = UNIT.findall(text)
    results.append(("PASS" if len(nums) >= 6 else "WARN", "numbers with units (found %d, want 6 or more): QPS, GB, ms, percent" % len(nums)))
    tw = TRADE_WORDS.findall(text)
    results.append(("PASS" if len(tw) >= 4 else "WARN", "stated trade-offs and alternatives (found %d reasoning phrases, want 4 or more)" % len(tw)))
    words = len(re.findall(r"\w+", re.sub(r"```.*?```", "", text, flags=re.S)))
    results.append(("PASS" if words >= 250 else "WARN", "enough prose to explain decisions (%d words outside code blocks)" % words))
    return results, missing


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    results, missing = lint(open(sys.argv[1], encoding="utf-8").read())
    for status, msg in results:
        print("%-8s %s" % (status, msg))
    print("%d required section(s) missing or empty" % missing)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
