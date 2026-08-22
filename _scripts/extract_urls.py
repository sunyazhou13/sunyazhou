#!/usr/bin/env python3
"""Extract all external URLs from blog posts for link checking."""
import os
import re
import json
from collections import defaultdict

POSTS_DIR = "/Users/sunyazhou/Documents/sunyazhou/_posts"
OUTPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_urls.json"

# Match markdown links, images, and bare URLs
URL_RE = re.compile(r'https?://[^\s<>"\)\]\u4e00-\u9fff]+')

# Extensions that are likely downloadable/binary, still check but mark type
IMG_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.svg', '.ico')

def normalize(url: str) -> str:
    # strip trailing punctuation commonly glued to URLs
    url = url.rstrip('.,;:!?)\'"')
    # strip markdown leftovers
    url = url.rstrip('}(')
    return url

def main():
    url_map = defaultdict(list)  # url -> [ (file, line_no) ]

    for root, dirs, files in os.walk(POSTS_DIR):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        for m in URL_RE.finditer(line):
                            url = normalize(m.group(0))
                            if len(url) < 12:
                                continue
                            rel = os.path.relpath(path, POSTS_DIR)
                            entry = (rel, i)
                            if entry not in url_map[url]:
                                url_map[url].append(entry)
            except Exception as e:
                print(f"Error reading {path}: {e}")

    urls = sorted(url_map.keys())
    result = {u: url_map[u] for u in urls}

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    # stats
    domains = defaultdict(int)
    for u in urls:
        m = re.match(r'https?://([^/]+)', u)
        if m:
            domains[m.group(1)] += 1
    print(f"Total unique URLs: {len(urls)}")
    print(f"Total references: {sum(len(v) for v in url_map.values())}")
    print("\nTop 30 domains:")
    for d, c in sorted(domains.items(), key=lambda x: -x[1])[:30]:
        print(f"  {c:4d}  {d}")

if __name__ == '__main__':
    main()
