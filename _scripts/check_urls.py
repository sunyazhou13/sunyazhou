#!/usr/bin/env python3
"""Check all extracted URLs concurrently using curl, output JSON report."""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_urls.json"
OUTPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_results.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# Domains where HEAD is rejected; and domains that always block bots — treat 403 as OK
KNOWN_HEAD_REJECT = ("developer.apple.com",)
BOT_BLOCK_403_OK = ("leetcode.cn", "mp.weixin.qq.com", "zhuanlan.zhihu.com",
                    "www.jianshu.com", "juejin.im", "juejin.cn", "www.zhihu.com",
                    "baike.baidu.com", "pan.baidu.com", "www.bilibili.com",
                    "space.bilibili.com", "item.jd.com", "www.raywenderlich.com",
                    "www.kodeco.com", "stackoverflow.com", "www.cnblogs.com",
                    "blog.csdn.net", "weibo.com", "www.weibo.com")


def curl_check(url: str) -> dict:
    """Check URL: HEAD first, then GET if HEAD unusable. Returns status dict."""
    def run(args):
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=20)
            code = p.returncode
            out = p.stdout
            return code, out
        except subprocess.TimeoutExpired:
            return 28, ""

    def parse_http_code(out: str) -> int:
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("HTTP/"):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    return int(parts[1])
        return 0

    # HEAD request
    head_args = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "-I", "-L", "--max-time", "15", "--max-redirs", "5",
                 "-A", UA, url]
    try:
        p = subprocess.run(head_args, capture_output=True, text=True, timeout=20)
        sc = p.stdout.strip()
        if sc.isdigit():
            status = int(sc)
        else:
            status = 0
    except subprocess.TimeoutExpired:
        status = 0

    # HEAD rejected or blocked -> try GET (range to avoid big download)
    if status in (0, 403, 405, 406, 501, 999) or status >= 500:
        host_in_block = any(d in url for d in BOT_BLOCK_403_OK)
        get_args = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                    "-L", "--max-time", "20", "--max-redirs", "5",
                    "-r", "0-2047", "-A", UA, url]
        try:
            p = subprocess.run(get_args, capture_output=True, text=True, timeout=25)
            gs = p.stdout.strip()
            gstatus = int(gs) if gs.isdigit() else 0
        except subprocess.TimeoutExpired:
            gstatus = 0
        # 403 on GET from known bot-blocking sites = effectively alive
        if gstatus == 403 and host_in_block:
            return {"url": url, "status": gstatus, "verdict": "alive(403-bot-block)",
                    "note": "site blocks bots but page likely exists"}
        if gstatus == 206:  # partial content from range request = alive
            gstatus = 200
        if gstatus != 0 and gstatus < 400:
            return {"url": url, "status": gstatus, "verdict": "alive", "note": ""}
        # HEAD 403 but GET failed differently — for bot-block domains treat HEAD 403 as alive
        if status == 403 and host_in_block:
            return {"url": url, "status": status, "verdict": "alive(403-bot-block)",
                    "note": "site blocks bots but page likely exists"}
        status = gstatus if gstatus else status

    if 200 <= status < 300:
        return {"url": url, "status": status, "verdict": "alive", "note": ""}
    if status in (301, 302, 303, 307, 308):
        return {"url": url, "status": status, "verdict": "redirect-ok", "note": ""}
    if status == 403:
        return {"url": url, "status": status, "verdict": "blocked(403)", "note": "forbidden — may need login or anti-bot"}
    if status == 401:
        return {"url": url, "status": status, "verdict": "auth-required", "note": ""}
    if status == 404 or status == 410:
        return {"url": url, "status": status, "verdict": "DEAD", "note": "not found"}
    if status in (0, 28):
        return {"url": url, "status": status, "verdict": "TIMEOUT/DNS", "note": "unreachable or DNS dead"}
    if status == 6:
        return {"url": url, "status": status, "verdict": "DEAD", "note": "DNS failure"}
    if status == 7:
        return {"url": url, "status": status, "verdict": "DEAD", "note": "connection refused"}
    if status == 60:
        return {"url": url, "status": status, "verdict": "cert-error", "note": "SSL cert problem"}
    return {"url": url, "status": status, "verdict": "ERROR", "note": ""}


def main():
    with open(INPUT, encoding='utf-8') as f:
        url_map = json.load(f)

    urls = list(url_map.keys())
    print(f"Checking {len(urls)} URLs with 64 workers...", file=sys.stderr)

    results = {}
    done = 0
    with ThreadPoolExecutor(max_workers=64) as ex:
        futs = {ex.submit(curl_check, u): u for u in urls}
        for fut in as_completed(futs):
            u = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {"url": u, "status": -1, "verdict": "ERROR", "note": str(e)}
            r["refs"] = url_map[u]
            results[u] = r
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(urls)} done", file=sys.stderr)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    # summary
    from collections import Counter
    c = Counter(r["verdict"] for r in results.values())
    print("\nSummary:")
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {v:4d}  {k}")


if __name__ == '__main__':
    main()
