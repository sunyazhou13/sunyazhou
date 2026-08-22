#!/usr/bin/env python3
"""Consolidate final link check results, apply manual corrections, generate HTML report."""
import json
import re
from collections import defaultdict

INPUT = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_final.json"
OUTPUT_JSON = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_check_report_data.json"
OUTPUT_HTML = "/Users/sunyazhou/Documents/sunyazhou/_scripts/link_report.html"

# Manual corrections from individual verification
ALIVE_OVERRIDES = [
    "https://github.com/RetVal/objc-runtime/blob/master/runtime/objc-private.h",
    "https://github.com/apple/swift-evolution/blob/master/proposals/0107-unsaferawpointer.md",
    "https://github.com/apple/swift-evolution/blob/master/proposals/0138-unsaferawbufferpointer.md",
    "https://github.com/apple/swift-evolution/blob/master/proposals/0202-random-unification.md",
    "https://github.com/gscalzo/Nimbo/blob/main/Sources/NimboCLI/Tools/ReadFile.swift",
]
DEAD_OVERRIDES = [
    "https://github.com/facebook/AsyncDisplayKit/blob/master/AsyncDisplayKit%2FDetails%2FTransactions%2F_ASAsyncTransactionGroup.m",
    "https://github.com/AFNetworking/AFNetworking/blob/master/AFNetworking%2FAFURLConnectionOperation.m",
]
# Fixed in source during this session
FIXED_IN_SOURCE = [
    "http://sunyazhou.com/2017/03/17/Learning-AV-Foundation-AVAudioPlayer/",
    "https://www.sunyazhou.com/2017/03/17/Learning-AV-Foundation-AVAudioPlayer/",
    "http://www.sunyazhou.com/2017/06/20/enable-static-analyer/",
    "https://www.sunyazhou.com/2017/09/29/20170929MarkdownTable/",
    "https://www.sunyazhou.com/2017/10/16/20171016UIViewRendering/",
    "https://www.sunyazhou.com/2017/10/25/20171025markdownSkill/",
    "https://www.sunyazhou.com/2020/08/08/20200808iOSinterviewAnswers/",
    "https://www.sunyazhou.com/tags/iOS%E9%9D%A2%E8%AF%95%E9%A2%98/",
    "https://www.sunyazhou.com/images/logo2.jpg",
    "http://localhost:4000/2017/03/20/Access-privacy-sensitive-data-private-access-permission/",
    "http://localhost:4000/2017/02/10/build-hexo-blog-Tutorial/",
]
GFW_DOMAINS = ("wikipedia.org",)
# Example/demo URLs intentionally kept
EXAMPLE_URLS = ["https://www.sunyazhou.com/xxproject/Specs.git"]

DEAD_IMAGE_BEDS = ("piimg.com", "bqimg.com", "bpimg.com", "sinaimg.cn", "wsimg.cn")


def classify(url, verdict):
    domain = re.match(r'https?://([^/]+)', url).group(1)
    if url in FIXED_IN_SOURCE:
        return "fixed"
    if url in ALIVE_OVERRIDES:
        return "alive"
    if url in DEAD_OVERRIDES:
        return "dead"
    if url in EXAMPLE_URLS:
        return "example"
    if any(d in domain for d in GFW_DOMAINS):
        return "gfw"
    if any(d in domain for d in DEAD_IMAGE_BEDS):
        return "dead-img"
    if verdict in ("alive", "redirect-ok", "alive(403-bot-block)"):
        return "alive"
    if verdict == "DEAD":
        return "dead"
    if verdict in ("blocked(403)", "auth-required"):
        return "blocked"
    if verdict in ("TIMEOUT/DNS", "ERROR"):
        return "unreachable"
    return "unknown"


def main():
    with open(INPUT, encoding='utf-8') as f:
        results = json.load(f)

    buckets = defaultdict(list)
    for url, r in results.items():
        cat = classify(url, r['verdict'])
        buckets[cat].append({
            "url": url,
            "status": r["status"],
            "refs": r["refs"],
        })

    for cat in buckets:
        buckets[cat].sort(key=lambda x: x["url"])

    stats = {k: len(v) for k, v in buckets.items()}
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({"stats": stats, "buckets": buckets}, f, ensure_ascii=False, indent=1)

    # ---- HTML ----
    CAT_META = {
        "dead": ("确认死链 (404/410/DNS失败)", "#d32f2f", "链接已失效，建议修复或移除"),
        "dead-img": ("死图床图片", "#d32f2f", "新浪系图床2019年集体关停，文章图片已丢失"),
        "fixed": ("本次已修复（自域名旧链接）", "#2e7d32", "Hexo时代旧格式URL，已替换为线上验证200的新地址"),
        "gfw": ("大陆网络不可达（非死链）", "#f57c00", "Wikipedia被墙，链接本身全球可访问"),
        "blocked": ("反爬拦截/需登录 (403)", "#f57c00", "站点存活但屏蔽了程序访问"),
        "unreachable": ("无法连接", "#d32f2f", "服务器无响应或域名失效"),
        "example": ("示例代码URL（保留）", "#555", "教程中的示例命令，非真实资源"),
        "alive": ("正常", "#2e7d32", ""),
    }

    total_refs = sum(len(item["refs"]) for items in buckets.values() for item in items)

    rows_html = ""
    for cat in ["fixed", "dead", "dead-img", "unreachable", "gfw", "blocked", "example"]:
        if cat not in buckets:
            continue
        title, color, desc = CAT_META[cat]
        items = buckets[cat]
        rows_html += f'<div class="file-group"><h3 style="color:{color};border-color:{color}">{title} <span class="badge">{len(items)} 个URL / {sum(len(i["refs"]) for i in items)} 处引用</span></h3>\n'
        rows_html += f'<p class="note">{desc}</p>\n<table>\n<tr><th>URL</th><th>状态</th><th>引用位置</th></tr>\n'
        for item in items:
            refs = ", ".join(f'{r[0]}:{r[1]}' for r in item["refs"][:4])
            more = f' <em>+{len(item["refs"])-4}处</em>' if len(item["refs"]) > 4 else ""
            url_short = item["url"] if len(item["url"]) < 90 else item["url"][:87] + "..."
            rows_html += f'<tr><td class="url">{url_short}</td><td>{item["status"]}</td><td class="note">{refs}{more}</td></tr>\n'
        rows_html += "</table></div>\n"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>博客外部资源链接检查报告</title>
<style>
:root {{
  --bg: #ffffff; --card-bg: #f8f9fa; --text: #1a1a1a; --text-sec: #555;
  --border: #e0e0e0; --accent: #0066cc; --table-header: #f0f4f8;
}}
body {{ font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  max-width: 1100px; margin: 0 auto; padding: 24px 20px; background: var(--bg); color: var(--text); line-height: 1.7; }}
h1 {{ font-size: 1.6em; border-bottom: 2px solid var(--accent); padding-bottom: 8px; }}
h2 {{ font-size: 1.25em; margin-top: 32px; color: var(--accent); }}
h3 {{ font-size: 1.05em; margin-top: 20px; border-left: 3px solid; padding-left: 8px; }}
.stats {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }}
.stat-card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 12px 20px; text-align: center; flex: 1; min-width: 110px; }}
.stat-card .num {{ font-size: 1.8em; font-weight: 700; color: var(--accent); }}
.stat-card .label {{ font-size: 0.85em; color: var(--text-sec); }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 0.85em; }}
th {{ background: var(--table-header); padding: 8px 10px; text-align: left; border: 1px solid var(--border); }}
td {{ padding: 8px 10px; border: 1px solid var(--border); vertical-align: top; word-break: break-all; }}
td.url {{ font-family: ui-monospace, Menlo, monospace; font-size: 0.92em; }}
.note {{ color: var(--text-sec); font-size: 0.9em; }}
.badge {{ font-size: 0.7em; font-weight: normal; background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 10px; padding: 2px 10px; margin-left: 8px; color: var(--text-sec); }}
.summary-box {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin: 16px 0; }}
.footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--border); font-size: 0.85em; color: var(--text-sec); }}
</style>
</head>
<body>
<h1>博客外部资源链接检查报告</h1>
<p>检查日期：2026年8月22日 | 扫描 216 篇文章（含英文版） | 提取 {len(results)} 个唯一 URL / {total_refs} 处引用</p>

<div class="stats">
  <div class="stat-card"><div class="num">{len(results)}</div><div class="label">唯一URL</div></div>
  <div class="stat-card"><div class="num">{stats.get('alive',0)+stats.get('blocked',0)}</div><div class="label">存活/拦截</div></div>
  <div class="stat-card"><div class="num">{stats.get('fixed',0)}</div><div class="label">本次已修复</div></div>
  <div class="stat-card"><div class="num">{stats.get('dead',0)+stats.get('dead-img',0)+stats.get('unreachable',0)}</div><div class="label">死链/不可达</div></div>
</div>

<div class="summary-box">
<h2 style="margin-top:0">检查方法</h2>
<ol>
<li><b>提取</b>：正则扫描全部 .md 文章中的 http/https 链接（Markdown链接、图片、裸URL）</li>
<li><b>三轮检测</b>：64并发HEAD初检 → 8并发GET复检 → 2并发+0.3s间隔慢速终检（本机代理无法承受高并发，初轮误报已全部排除）</li>
<li><b>人工复核</b>：GitHub深链、Wikipedia、Apple文档、自域名链接逐个单测验证</li>
<li><b>误报处理</b>：知乎/简书/LeetCode等反爬站点403视为存活；Wikipedia为大陆网络不可达非死链</li>
</ol>
</div>

<h2>附加发现：inspector.js 控制台报错</h2>
<div class="summary-box">
<p><b>结论：与博客无关，是浏览器插件注入的脚本。</b></p>
<ul>
<li><code>inspector.js</code> 在博客源码与构建产物（_site）中均不存在</li>
<li>博客全部 JS 资源（jQuery、MathJax、simple-jekyll-search、Chirpy主题脚本）grep 检查 0 处 <code>responseType='arraybuffer'</code> 使用</li>
<li>该报错是插件A用 arraybuffer 发请求、插件B（inspector.js）钩住 XHR 后错误读 responseText 所致</li>
<li><b>验证方法</b>：无痕模式（禁用插件）打开 localhost:4000，报错消失即可确认</li>
</ul>
</div>

<h2>分类明细</h2>
{rows_html}

<div class="footer">
<p>自域名死链修复明细（11篇文章×中英双语，共28处）：</p>
<ul class="note">
<li>Learning-AV-Foundation-AVAudioPlayer（旧slug）→ /2017/03/LearningAVFoundationAVAudioPlayer/</li>
<li>enable-static-analyer → /2017/06/EnableStaticAnalyer/</li>
<li>20170929MarkdownTable → /2017/09/MarkdownTable/</li>
<li>20171016UIViewRendering → /2017/10/UIViewRendering/</li>
<li>20171025markdownSkill → /2017/10/MarkdownSkill/</li>
<li>20200808iOSinterviewAnswers → /2020/08/iOSinterviewAnswers2/</li>
<li>tags/iOS面试题（标签页不存在）→ /2020/07/iOSinterviewAnswers1/</li>
<li>images/logo2.jpg（演示图失效）→ 文章内真实图片 album1.avif</li>
<li>localhost:4000 ×2（本地调试残留）→ 线上正式URL</li>
</ul>
<p>所有替换URL均已在线上逐一验证返回200。</p>
</div>
</body>
</html>"""
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\nReport written: {OUTPUT_HTML}")


if __name__ == '__main__':
    main()
