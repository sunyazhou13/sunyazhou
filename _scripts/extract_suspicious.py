#!/usr/bin/env python3
"""
Extract "suspicious" prose sentences from English blog posts for manual review.

Rules:
- Skip YAML front matter
- Skip code blocks (``` fenced)
- Skip the Preface/Introduction disclaimer paragraph
- Skip image lines and bare link lists
- Flag sentences matching AI-translation awkwardness heuristics

Usage: python3 extract_suspicious.py > suspicious_report.txt
"""

import re
from pathlib import Path

EN_POSTS_DIR = Path("/Users/sunyazhou/Documents/sunyazhou/_posts/en")

# Heuristics for awkward AI-translated English prose
SUSPICIOUS_PATTERNS = [
    # Literal translation starters (直译句首)
    (r'^(In addition|First of all|On the whole|To sum up|In summary),?\s', '直译句首'),
    (r'^(Next|Then|Finally),\s+(I|we|let|the|this|it)', 'Next/Then/Finally 句首'),
    (r'^We (can|will) (see|know|find) that', 'we can see that'),
    (r'^It is worth (noting|mentioning) that', 'It is worth noting'),
    (r'^As we all know', 'As we all know'),
    (r'^At this point', 'At this point'),
    (r'^The above', 'The above'),
    (r'\bObviously\b', 'Obviously'),
    (r'\bin actual development\b', 'in actual development'),
    (r'\bin daily (use|development|work|life)\b', 'in daily'),
    (r'\bfrom the perspective of\b', 'from the perspective of'),
    (r'\bsummarized as follows\b|\blisted as follows\b', 'as follows'),
    (r'\bfor your reference\b', 'for your reference'),
    (r'\bwelcome to reprint\b', 'welcome to reprint'),
    (r'\bget it done\b', 'get it done'),
    (r'\bpaying it off\b|\bpay off the technical debt\b', 'pay off debt'),
    (r'\btechnical guys\b', 'technical guys'),
    (r'\bzero technical content\b', 'zero technical content'),
    (r'\bimprove your awareness\b|\brise in awareness\b', 'awareness 直译'),
    (r'\bmore impressive\b', 'more impressive'),
    (r'\bencapsulat', 'encapsulate 封装'),
    (r'\bhandwriting\b|\bhand-written\b', 'handwriting 手写'),
    (r'\bbrush (up|questions|leetcode|problems)\b', 'brush 刷'),
    (r'\bsolve the problem of\b', 'solve the problem of'),
    (r'\bthe problem of\b.*\bcomes\b', 'the problem of comes'),
    (r'\bmake a (record|summary|note)\b', 'make a record 记录'),
    (r'\brecorded here\b|\brecording it here\b', 'recorded here 记录'),
    (r'\borganized here\b|\borganized it\b', 'organized here 整理'),
    (r'\bfor reference only\b', 'for reference only'),
    (r'\bsharing with everyone\b', 'sharing with everyone'),
    (r'\blearn(ed)? .{0,20} from .{0,30} (article|post|tutorial)', 'learned from'),
    (r'\bdig (a|into) (hole|pit)\b', 'dig a pit 挖坑'),
    (r'\bfill (in )?the (hole|pit)\b', 'fill the pit 填坑'),
    (r'\bsteps? are as follows\b', 'steps as follows'),
    (r'\bthe effect is as follows\b', 'effect as follows'),
    (r'\bthe principle (is|of) (as follows|simple)\b', 'principle as follows'),
    (r'\bneeds? to be (noted|mentioned)\b', 'needs to be noted'),
    (r'\bnot difficult to (find|see|understand)\b', 'not difficult to find'),
    (r'\beasy to (know|understand) that\b', 'easy to know'),
    (r'\bsimply (put|speaking)\b', 'simply put'),
    (r'\bthat is to say\b', 'that is to say'),
    (r'\bin other words\b', 'in other words'),
    (r'\bon the other hand\b', 'on the other hand'),
    (r'\band so on\b', 'and so on 等等'),
    (r'\betc\.\s', 'etc.'),
    (r'\bthe so-called\b', 'the so-called 所谓'),
    (r'\bwhat I want to say\b', 'what I want to say'),
    (r'\bI won\'t (say|talk) much\b', "won't say much 废话不多说"),
    (r'\bwithout further ado\b', 'without further ado'),
    (r'\benter(s)?? the (text|topic)\b', 'enter the topic 进入正题'),
    (r'\blet\'s (take a look|look at)\b', "let's take a look"),
    (r'\btake a (look|look at)\b', 'take a look'),
    (r'\bthe following is\b|\bas follows\b', 'the following is'),
    (r'\bwill be explained (below|later)\b', 'explained below'),
    (r'\bdemo( is)? as follows\b', 'demo as follows'),
    (r'\bcode( is)? as follows\b', 'code as follows'),
]


def extract_prose(content):
    """Extract prose lines: skip front matter, code blocks, disclaimer, images, links."""
    lines = content.split('\n')
    prose_lines = []
    in_code = False
    in_frontmatter = False
    in_disclaimer = False
    disclaimer_done = False

    for i, line in enumerate(lines):
        # Front matter
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == '---':
                in_frontmatter = False
            continue

        # Code blocks
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue

        # Skip images, empty lines, pure links
        stripped = line.strip()
        if not stripped or stripped.startswith('!['):
            continue
        # Bare markdown links (link lists)
        if re.match(r'^\*?\s*\[.*\]\(.*\)\s*\*?$', stripped):
            continue

        # Disclaimer: the first paragraph after a Preface/Introduction heading
        if re.match(r'^#{1,3}\s+(Preface|Introduction)\s*$', stripped):
            in_disclaimer = True
            disclaimer_done = True
            continue
        if in_disclaimer:
            # Disclaimer paragraph contains the characteristic patterns
            if ('personal' in stripped and ('close' in stripped or 'uncomfortable' in stripped or 'license' in stripped or 'repost' in stripped or 'reprint' in stripped or 'RSS' in stripped or 'copyright' in stripped)):
                continue  # skip disclaimer line
            elif stripped.startswith('#'):
                in_disclaimer = False  # next section, stop skipping
            elif re.match(r'^[>#*]', stripped):
                continue  # still in disclaimer area (blockquote etc.)
            else:
                in_disclaimer = False

        prose_lines.append((i + 1, line))

    return prose_lines


def main():
    md_files = sorted(EN_POSTS_DIR.glob('*.md'))
    print(f"# Suspicious prose sentences across {len(md_files)} English posts\n")

    total_files_with_hits = 0
    total_hits = 0

    for fp in md_files:
        content = fp.read_text()
        prose = extract_prose(content)
        hits = []
        for lineno, line in prose:
            text = line.strip()
            for pat, label in SUSPICIOUS_PATTERNS:
                if re.search(pat, text, re.IGNORECASE if pat.startswith(r'^') is False else 0):
                    hits.append((lineno, label, text))
                    break  # one hit per line is enough

        if hits:
            total_files_with_hits += 1
            total_hits += len(hits)
            print(f"## {fp.name} ({len(hits)} hits)")
            for lineno, label, text in hits:
                text_short = text[:150] + ('...' if len(text) > 150 else '')
                print(f"  L{lineno} [{label}] {text_short}")
            print()

    print(f"\n# Summary: {total_hits} suspicious lines in {total_files_with_hits}/{len(md_files)} files")


if __name__ == '__main__':
    main()
