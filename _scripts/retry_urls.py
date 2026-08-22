#!/usr/bin/env python3
"""Retry suspicious results: github.com, wikipedia, opensource.apple.com, all ERROR/TIMEOUT.
Slower pace, GET with range, browser UA."""
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_results.json"
OUTPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_retry.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def get_check(url):
    args = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "-L", "--max-time", "30", "--max-redirs", "8",
            "-A", UA,
            "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "-H", "Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8",
            url]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=35)
        s = p.stdout.strip()
        return int(s) if s.isdigit() else 0
    except subprocess.TimeoutExpired:
        return 0


def main():
    with open(INPUT, encoding='utf-8') as f:
        results = json.load(f)

    # retry all TIMEOUT/DNS and ERROR verdicts
    retry_urls = [u for u, r in results.items()
                  if r['verdict'] in ('TIMEOUT/DNS', 'ERROR')]
    print(f"Retrying {len(retry_urls)} URLs with 8 workers (gentle)...", file=sys.stderr)

    updates = {}
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(get_check, u): u for u in retry_urls}
        for fut in as_completed(futs):
            u = futs[fut]
            try:
                status = fut.result()
            except Exception:
                status = 0
            old = results[u]
            if 200 <= status < 400:
                updates[u] = {**old, "status": status, "verdict": "alive",
                              "note": f"retry-ok (was {old['verdict']} {old['status']})"}
            elif status == 403:
                updates[u] = {**old, "status": status, "verdict": "blocked(403)",
                              "note": f"retry 403 (was {old['verdict']})"}
            elif status == 404 or status == 410:
                updates[u] = {**old, "status": status, "verdict": "DEAD",
                              "note": f"retry confirmed 404/410 (was {old['verdict']})"}
            else:
                updates[u] = {**old, "note": f"retry still failed: {status}"}
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(retry_urls)}", file=sys.stderr)

    # merge
    results.update(updates)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    from collections import Counter
    c = Counter(r["verdict"] for r in results.values())
    print("\nSummary after retry:")
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {v:4d}  {k}")


if __name__ == '__main__':
    main()
