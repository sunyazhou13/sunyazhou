#!/usr/bin/env python3
"""Final slow recheck: sequential with delays, for URLs still failing after retry."""
import json
import subprocess
import sys
import time

INPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_retry.json"
OUTPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_final.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def get_status(url):
    # plain GET, follow redirects, no extra headers
    args = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "-L", "--max-time", "25", "--max-redirs", "8", "-A", UA, url]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=30)
        s = p.stdout.strip()
        return int(s) if s.isdigit() else 0
    except subprocess.TimeoutExpired:
        return 0


def main():
    with open(INPUT, encoding='utf-8') as f:
        results = json.load(f)

    todo = [u for u, r in results.items()
            if r['verdict'] in ('TIMEOUT/DNS', 'ERROR')]
    print(f"Slow recheck of {len(todo)} URLs (2 workers + 0.3s delay)...", file=sys.stderr)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    updates = {}
    done = 0
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {}
        for u in todo:
            futs[ex.submit(get_status, u)] = u
            time.sleep(0.3)
        for fut in as_completed(futs):
            u = futs[fut]
            try:
                status = fut.result()
            except Exception:
                status = 0
            old = results[u]
            if 200 <= status < 400:
                updates[u] = {**old, "status": status, "verdict": "alive",
                              "note": f"slow-recheck ok (was {old['verdict']})"}
            elif status == 404 or status == 410:
                updates[u] = {**old, "status": status, "verdict": "DEAD",
                              "note": f"slow-recheck 404/410 (was {old['verdict']})"}
            elif status == 403:
                updates[u] = {**old, "status": status, "verdict": "blocked(403)",
                              "note": f"slow-recheck 403 (was {old['verdict']})"}
            else:
                updates[u] = {**old, "note": f"slow-recheck failed: {status}"}
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(todo)}", file=sys.stderr)

    results.update(updates)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    from collections import Counter
    c = Counter(r["verdict"] for r in results.values())
    print("\nFinal summary:")
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {v:4d}  {k}")


if __name__ == '__main__':
    main()
