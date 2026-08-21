#!/usr/bin/env python3
"""Dump full source lines for targeted translationese patterns (needs manual rewrite)."""
import os, re, sys

POSTS = "/Users/sunyazhou/Documents/sunyazhou/_posts/en"
REPORT = "/tmp/suspicious_report.txt"

# Patterns that need sentence-level manual review (NOT the bulk "as follows" class)
TARGET_TAGS = [
    "The above", "Obviously", "the so-called", "and so on", "etc.",
    "直译句首", "solve the problem of", "At this point", "recorded here",
    "what I want to say", "for reference only", "handwriting", "more impressive",
    "in daily", "on the other hand", "from the perspective of", "get it done",
    "in actual development", "simply put", "encapsulate",
]

def extract_prose(content):
    """Yield (lineno, line) for prose lines only: skip front matter, code fences, tables, images, bare links."""
    lines = content.split("\n")
    in_fm = False
    fm_done = False
    in_code = False
    out = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not fm_done:
            if s == "---":
                if in_fm:
                    in_fm = False
                    fm_done = True
                else:
                    in_fm = True
                continue
            if in_fm:
                continue
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s.startswith("|"):  # table rows
            continue
        if s.startswith("![") or re.match(r'^<img ', s):
            continue
        if re.match(r'^\s*https?://\s*$', s):
            continue
        out.append((i, line))
    return out

entries = []  # (fname, lineno)
cur_file = None
with open(REPORT) as f:
    for line in f:
        m = re.match(r'^## (.+\.md) \(', line)
        if m:
            cur_file = m.group(1)
            continue
        m = re.match(r'^\s+L(\d+) \[(.+?)\] ', line)
        if m and cur_file:
            tag = m.group(2)
            if any(tag == t or tag.startswith(t + " ") for t in TARGET_TAGS):
                entries.append((cur_file, int(m.group(1)), tag))

print(f"targeted entries: {len(entries)}")
with open("/tmp/targeted_lines.txt", "w") as out:
    byfile = {}
    for fname, ln, tag in entries:
        byfile.setdefault(fname, []).append((ln, tag))
    for fname in sorted(byfile):
        path = os.path.join(POSTS, fname)
        if not os.path.exists(path):
            continue
        prose = dict(extract_prose(open(path).read()))
        out.write(f"===== {fname} =====\n")
        for ln, tag in sorted(byfile[fname]):
            text = prose.get(ln, "(not a prose line — skipped)")
            out.write(f"  L{ln} [{tag}] {text}\n")
        out.write("\n")
print("written /tmp/targeted_lines.txt")
