#!/usr/bin/env python3
"""Remove dead external resources from blog posts.

Rules:
- Apple .avif art URLs -> fix to .png (verified 200)
- [text](dead-url)  -> keep text, drop link (if text is the url itself, drop all)
- ![alt](dead-url)   -> drop image markup entirely
- bare dead-url      -> drop url, drop line if only dangling remnants remain
- SKIP: code fences, example.com, devicecheck API endpoints
"""
import json
import os
import re

DATA = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_report_data.json"
POSTS = "/Users/sunyazhou/Documents/sunyazhou/_posts"
LOG = "/Users/sunyazhou/Documents/sunyazhou/_scripts/dead_link_removal_log.txt"

EXCLUDE_SUBSTR = ("example.com", "devicecheck.apple.com")

# fixes: .avif -> .png on apple library art
FIX_AVIF = re.compile(
    r'(https://developer\.apple\.com/library/content/[^\s)]+?)\.avif\)')


def is_excluded(url):
    return any(s in url for s in EXCLUDE_SUBSTR)


def load_dead_urls():
    with open(DATA, encoding='utf-8') as f:
        data = json.load(f)
    urls = []
    for cat in ('dead', 'unreachable'):
        urls += [i['url'] for i in data['buckets'][cat]]
    # dead-img bucket refs already gone (article deleted), but include anyway
    urls += [i['url'] for i in data['buckets'].get('dead-img', [])]
    urls = [u for u in urls if not is_excluded(u)]
    # dedupe, longest first so specific urls replace before domain-ish ones
    return sorted(set(urls), key=len, reverse=True)


def unlink_mdlinks(content, url, log, fname):
    """Handle [text](url) and ![alt](url) forms for this url."""
    esc = re.escape(url)
    # image form
    img_re = re.compile(r'!\[[^\]]*\]\(' + esc + r'\)\s*')
    n_img = len(img_re.findall(content))
    if n_img:
        content = img_re.sub('', content)
        log.append(f"{fname}: removed {n_img} image markup -> {url[:70]}")
    # mdlink form: [text](url)
    link_re = re.compile(r'\[([^\]]*)\]\(' + esc + r'\)')
    n_link = 0
    def link_sub(m):
        nonlocal n_link
        n_link += 1
        text = m.group(1).strip()
        # if text is empty or is the url itself, drop entirely
        if not text or text == url or (text.startswith('http') and text in url):
            return ''
        return text
    content = link_re.sub(link_sub, content)
    if n_link:
        log.append(f"{fname}: unlinked {n_link} md link -> {url[:70]}")
    return content, n_img + n_link


def remove_bare(content, url, log, fname):
    """Remove leftover bare occurrences of url."""
    n = content.count(url)
    if n == 0:
        return content, 0
    content = content.replace(url, '')
    # clean dangling punctuation left right before/after where url was:
    # e.g. "see (url)" -> "see ()" ; "ref: url," -> "ref: ,"
    content = re.sub(r'\(\s*\)', '', content)
    log.append(f"{fname}: removed {n} bare url -> {url[:70]}")
    return content, n


def clean_dangling_lines(content):
    """Remove lines that became empty or trivial remnants after removal."""
    out_lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        # trivial remnants: empty, lone list/dash/colon ends, lone parens
        if re.fullmatch(r'(\s*[-*]\s*)|(\s*[：:]\s*)|(\s*参考\s*[：:]?\s*)|(\s*>\s*)', stripped):
            continue
        out_lines.append(line)
    # collapse triple+ newlines left by removals
    content = '\n'.join(out_lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content


def main():
    dead_urls = load_dead_urls()
    print(f"Dead URLs to process: {len(dead_urls)}")

    log = []
    total_files = 0
    total_ops = 0

    for root, dirs, files in os.walk(POSTS):
        for fn in sorted(files):
            if not fn.endswith('.md'):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, POSTS)
            with open(path, encoding='utf-8') as f:
                original = f.read()

            # 1) fix apple avif -> png
            content, n_fix = FIX_AVIF.subn(r'\1.png)', original)
            if n_fix:
                log.append(f"{rel}: fixed {n_fix} apple .avif -> .png")

            # 2) process outside code fences only:
            #    split by fences, keep fence segments untouched
            segments = re.split(r'(```.*?```)', content, flags=re.DOTALL)
            ops = 0
            for i, seg in enumerate(segments):
                if seg.startswith('```'):
                    continue
                for url in dead_urls:
                    if url not in seg:
                        continue
                    seg, n1 = unlink_mdlinks(seg, url, log, rel)
                    seg, n2 = remove_bare(seg, url, log, rel)
                    ops += n1 + n2
                segments[i] = seg
            content = ''.join(segments)

            if ops:
                content = clean_dangling_lines(content)
                total_ops += ops
                total_files += 1

            if content != original:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

    with open(LOG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log))

    print(f"Files modified: {total_files}")
    print(f"Total removal operations: {total_ops}")
    print(f"Log: {LOG}")
    print(f"\nLog lines: {len(log)}")


if __name__ == '__main__':
    main()
