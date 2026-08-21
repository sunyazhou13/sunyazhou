#!/usr/bin/env python3
"""
博客资源完整性检查
扫描 _site 中所有 HTML/CSS/JS 资源引用，验证是否存在且非空。
"""

import os
import re
import sys
import json
from pathlib import Path
from html.parser import HTMLParser

# 动态推导 _site 路径（相对于脚本所在目录的上级 _site）
SITE_DIR = Path(__file__).resolve().parent.parent / "_site"

# 颜色
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

pass_count = 0
fail_count = 0
warn_count = 0

def pass_msg(msg):
    global pass_count
    print(f"  {GREEN}[PASS]{NC} {msg}")
    pass_count += 1

def fail_msg(msg):
    global fail_count
    print(f"  {RED}[FAIL]{NC} {msg}")
    fail_count += 1

def warn_msg(msg):
    global warn_count
    print(f"  {YELLOW}[WARN]{NC} {msg}")
    warn_count += 1

def info_msg(msg):
    print(f"  {BLUE}[INFO]{NC} {msg}")

def section(title):
    print(f"\n{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"{BLUE}  {title}{NC}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")

# ============================================================
# 1. 收集所有 HTML/CSS/JS 文件中的资源引用
# ============================================================

class ResourceCollector(HTMLParser):
    """解析 HTML，提取所有资源引用"""
    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path
        self.resources = []  # (url, type, source_file, line_no)
        self.has_title = False
        self.has_body = False
        self.body_content_len = 0
        self.has_sidebar = False
        self.has_footer = False
        self.has_head = False
        self.has_nav = False
        self.has_article = False
        self.img_alt_missing = 0
        self.total_img = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self.has_title = True
        if tag == "body":
            self.has_body = True
        if tag == "header" or (tag == "div" and attrs_dict.get("id") == "header"):
            self.has_head = True
        if tag == "aside" or attrs_dict.get("class","").find("sidebar") >= 0:
            self.has_sidebar = True
        if tag == "footer":
            self.has_footer = True
        if tag == "nav":
            self.has_nav = True
        if tag == "article":
            self.has_article = True
        if tag == "body":
            self.body_content_len = 0

        # <img src>
        if tag == "img":
            self.total_img += 1
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            if not alt:
                self.img_alt_missing += 1
            if src and not src.startswith(("http", "//", "data:", "#", "mailto:")):
                self.resources.append((src, "img", "html"))

        # <link href>
        if tag == "link":
            href = attrs_dict.get("href", "")
            rel = attrs_dict.get("rel", "")
            if href and not href.startswith(("http", "//", "data:", "#", "mailto:")):
                rtype = "css" if "stylesheet" in rel else "link"
                self.resources.append((href, rtype, "html"))

        # <script src>
        if tag == "script":
            src = attrs_dict.get("src", "")
            if src and not src.startswith(("http", "//", "data:", "#", "mailto:")):
                self.resources.append((src, "js", "html"))

        # <source srcset>
        if tag == "source":
            srcset = attrs_dict.get("srcset", "")
            if srcset:
                for s in srcset.split(","):
                    url = s.strip().split(" ")[0]
                    if url and not url.startswith(("http", "//", "data:", "#")):
                        self.resources.append((url, "source", "html"))

    def handle_data(self, data):
        if self.has_body:
            self.body_content_len += len(data.strip())

def resolve_path(url, base_dir, site_dir):
    """将相对 URL 解析为文件系统路径

    - 以 / 开头的绝对路径（如 /assets/css/post.css）基于 site_dir 解析
    - 其他相对路径（如 ../images/foo.png）基于 base_dir（HTML 文件所在目录）解析
    """
    # 去除 query string 和 fragment
    url = url.split("?")[0].split("#")[0]
    # 绝对路径：基于站点根目录解析
    if url.startswith("/"):
        return site_dir / url[1:]
    return base_dir / url

# ============================================================
# 2. 扫描所有 HTML 文件
# ============================================================

section("检查 1/7: HTML 资源引用完整性")

html_files = sorted(SITE_DIR.rglob("*.html"))
info_msg(f"扫描 {len(html_files)} 个 HTML 文件...")

all_missing = []
all_empty = []
total_resources = 0
total_img_alt_missing = 0
pages_missing_structure = []

for html_file in html_files:
    try:
        content = html_file.read_text(encoding="utf-8", errors="replace")
    except:
        continue

    collector = ResourceCollector(html_file.parent)
    try:
        collector.feed(content)
    except:
        pass

    rel_path = html_file.relative_to(SITE_DIR)

    # 检查资源引用
    for url, rtype, source in collector.resources:
        total_resources += 1
        resolved = resolve_path(url, html_file.parent, SITE_DIR)
        if not resolved.exists():
            all_missing.append((str(rel_path), url, rtype))
        elif resolved.stat().st_size == 0:
            all_empty.append((str(rel_path), url, rtype))

    # alt 属性检查
    total_img_alt_missing += collector.img_alt_missing

    # 页面结构检查（只检查文章页面）
    if "/posts/" in str(rel_path) or rel_path.match("*/202[0-9]/*"):
        structure = []
        if not collector.has_body:
            structure.append("body")
        if not collector.has_footer:
            structure.append("footer")
        if not collector.has_nav:
            structure.append("nav")
        if not collector.has_article:
            structure.append("article")
        if structure:
            pages_missing_structure.append((str(rel_path), structure))

if not all_missing:
    pass_msg(f"所有 {total_resources} 个资源引用均存在")
else:
    fail_msg(f"{len(all_missing)} 个资源引用缺失")
    # 按类型分组显示
    missing_by_type = {}
    for page, url, rtype in all_missing[:50]:
        if rtype not in missing_by_type:
            missing_by_type[rtype] = []
        missing_by_type[rtype].append(f"{page} → {url}")
    for rtype, items in missing_by_type.items():
        print(f"      {rtype} 缺失 ({len(items)} 个):")
        for item in items[:5]:
            print(f"        {item}")
        if len(items) > 5:
            print(f"        ... 还有 {len(items)-5} 个")

if all_empty:
    warn_msg(f"{len(all_empty)} 个资源文件为空")
    for page, url, rtype in all_empty[:5]:
        print(f"      {page} → {url} ({rtype})")
else:
    pass_msg("无空资源文件")

# ============================================================
# 3. 检查关键页面结构
# ============================================================

section("检查 2/7: 关键页面结构完整性")

key_pages = [
    ("index.html", ["body", "footer", "nav"]),
    ("404.html", ["body"]),
    ("feed.xml", []),
    ("sitemap.xml", []),
]

for page_name, expected_tags in key_pages:
    page_path = SITE_DIR / page_name
    if not page_path.exists():
        fail_msg(f"{page_name} 不存在")
        continue
    size = page_path.stat().st_size
    if size < 100:
        fail_msg(f"{page_name} 文件过小 ({size} bytes)")
    else:
        pass_msg(f"{page_name} ({size} bytes)")

# 检查 tabs 页面
tabs_dir = SITE_DIR / "tabs"
if tabs_dir.exists():
    tab_pages = list(tabs_dir.glob("*.html")) + list(tabs_dir.glob("*/index.html"))
    for tab in tab_pages:
        if tab.stat().st_size < 100:
            fail_msg(f"tab {tab.name} 过小")
        else:
            pass_msg(f"tab {tab.name} ({tab.stat().st_size} bytes)")
else:
    fail_msg("tabs 目录不存在")

# ============================================================
# 4. CSS 文件内容检查
# ============================================================

section("检查 3/7: CSS 文件和字体引用")

css_files = list(SITE_DIR.rglob("*.css"))
info_msg(f"找到 {len(css_files)} 个 CSS 文件")

font_refs = []
css_url_refs = []
for css_file in css_files:
    try:
        content = css_file.read_text(encoding="utf-8", errors="replace")
    except:
        continue

    # 检查 url() 引用
    urls = re.findall(r'url\(["\']?([^)"\']+)["\']?\)', content)
    for url in urls:
        if url.startswith(("http", "//", "data:", "#")):
            if "fonts.googleapis" in url or "fonts.gstatic" in url:
                font_refs.append((str(css_file.relative_to(SITE_DIR)), url))
            continue
        css_url_refs.append((str(css_file.relative_to(SITE_DIR)), url, css_file.parent))

if css_files:
    pass_msg(f"{len(css_files)} 个 CSS 文件存在")
else:
    fail_msg("无 CSS 文件")

# 检查 CSS 中引用的本地资源
css_missing = []
for css_file_rel, url, css_dir in css_url_refs:
    url_clean = url.split("?")[0].split("#")[0]
    if url_clean.startswith("/"):
        resolved = SITE_DIR / url_clean[1:]
    else:
        resolved = css_dir / url_clean
    if not resolved.exists():
        css_missing.append((css_file_rel, url))

if not css_missing:
    pass_msg(f"CSS 中 {len(css_url_refs)} 个本地资源引用均存在")
else:
    fail_msg(f"CSS 中 {len(css_missing)} 个资源引用缺失")
    for css_file_rel, url in css_missing[:5]:
        print(f"      {css_file_rel} → {url}")

# 字体检查
if font_refs:
    pass_msg(f"Google Fonts 引用 {len(font_refs)} 处（外部资源，需网络加载）")
    for css_file_rel, url in font_refs[:2]:
        print(f"      {css_file_rel} → {url[:80]}...")

# 检查本地字体文件
local_fonts = list(SITE_DIR.rglob("*.woff*")) + list(SITE_DIR.rglob("*.ttf")) + list(SITE_DIR.rglob("*.otf"))
if local_fonts:
    pass_msg(f"本地字体文件 {len(local_fonts)} 个")
    for f in local_fonts[:3]:
        print(f"      {f.relative_to(SITE_DIR)} ({f.stat().st_size} bytes)")
else:
    info_msg("无本地字体文件（使用 Google Fonts CDN）")

# ============================================================
# 5. JS 文件检查
# ============================================================

section("检查 4/7: JavaScript 文件完整性")

js_files = list(SITE_DIR.rglob("*.js"))
info_msg(f"找到 {len(js_files)} 个 JS 文件")

js_empty = []
for js_file in js_files:
    if js_file.stat().st_size == 0:
        js_empty.append(str(js_file.relative_to(SITE_DIR)))

if not js_empty:
    pass_msg(f"{len(js_files)} 个 JS 文件均非空")
else:
    fail_msg(f"{len(js_empty)} 个空 JS 文件")
    for f in js_empty[:5]:
        print(f"      {f}")

# 检查 JS 文件大小分布
if js_files:
    sizes = [f.stat().st_size for f in js_files]
    total_js = sum(sizes)
    info_msg(f"JS 总大小: {total_js/1024:.1f} KB, 平均: {total_js/len(js_files)/1024:.1f} KB")

# ============================================================
# 6. 图片资源检查
# ============================================================

section("检查 5/7: 图片资源完整性")

img_files = list(SITE_DIR.rglob("*.png")) + list(SITE_DIR.rglob("*.jpg")) + \
            list(SITE_DIR.rglob("*.jpeg")) + list(SITE_DIR.rglob("*.gif")) + \
            list(SITE_DIR.rglob("*.svg")) + list(SITE_DIR.rglob("*.webp"))

info_msg(f"找到 {len(img_files)} 个图片文件")

img_empty = []
img_oversized = []
for img_file in img_files:
    size = img_file.stat().st_size
    if size == 0:
        img_empty.append(str(img_file.relative_to(SITE_DIR)))
    elif size > 5 * 1024 * 1024:  # >5MB
        img_oversized.append((str(img_file.relative_to(SITE_DIR)), size))

if not img_empty:
    pass_msg(f"{len(img_files)} 个图片文件均非空")
else:
    fail_msg(f"{len(img_empty)} 个空图片文件")
    for f in img_empty[:5]:
        print(f"      {f}")

if img_oversized:
    warn_msg(f"{len(img_oversized)} 个图片超过 5MB（建议压缩）")
    for f, s in img_oversized[:3]:
        print(f"      {f} ({s/1024/1024:.1f} MB)")
else:
    pass_msg("无超大图片文件")

# alt 属性检查
if total_img_alt_missing > 0:
    warn_msg(f"{total_img_alt_missing} 个 <img> 缺少 alt 属性（影响无障碍和 SEO）")
else:
    pass_msg("所有 <img> 均有 alt 属性")

# ============================================================
# 7. 文章页面内容检查
# ============================================================

section("检查 6/7: 文章页面内容完整性")

post_dirs = set()
for html_file in html_files:
    rel = str(html_file.relative_to(SITE_DIR))
    # 匹配 /2022/04/title/index.html 等文章路径
    m = re.match(r"(20\d{2}/\d{2}/[^/]+)/index\.html", rel)
    if m:
        post_dirs.add(m.group(1))

info_msg(f"找到 {len(post_dirs)} 篇文章页面")

if len(post_dirs) > 0:
    # 抽样检查 10 篇文章
    sampled = sorted(post_dirs)[:10]
    empty_posts = []
    no_title = []
    no_article = []
    very_short = []

    for post_slug in sampled:
        post_file = SITE_DIR / post_slug / "index.html"
        try:
            content = post_file.read_text(encoding="utf-8", errors="replace")
        except:
            empty_posts.append(post_slug)
            continue

        # 检查内容长度
        # 去除 HTML 标签后的文本长度
        text_only = re.sub(r'<[^>]+>', '', content)
        text_only = re.sub(r'\s+', '', text_only)
        text_len = len(text_only)

        if text_len < 100:
            very_short.append((post_slug, text_len))

        # 检查是否有 <article> 标签
        if "<article" not in content:
            no_article.append(post_slug)

        # 检查是否有 <title>
        if "<title>" not in content:
            no_title.append(post_slug)

    if not empty_posts:
        pass_msg(f"抽样 10 篇文章均非空")
    else:
        fail_msg(f"{len(empty_posts)} 篇文章为空")
        for p in empty_posts:
            print(f"      {p}")

    if not no_title:
        pass_msg("抽样文章均有 <title> 标签")
    else:
        fail_msg(f"{len(no_title)} 篇文章缺少 <title>")

    if not no_article:
        pass_msg("抽样文章均有 <article> 结构")
    else:
        warn_msg(f"{len(no_article)} 篇文章缺少 <article> 标签")

    if not very_short:
        pass_msg("抽样文章内容长度正常 (>100 字符)")
    else:
        warn_msg(f"{len(very_short)} 篇文章内容过短")
        for p, l in very_short:
            print(f"      {p} (文本仅 {l} 字符)")

    # 检查 polyglot 多语言文章
    en_posts = [p for p in post_dirs if f"/en/" in p or p.startswith("en/")]
    if en_posts:
        pass_msg(f"Polyglot EN 文章: {len(en_posts)} 篇")
    else:
        # 检查是否有 /en/ 目录
        en_dir = SITE_DIR / "en"
        if en_dir.exists():
            en_html = list(en_dir.rglob("*.html"))
            pass_msg(f"Polyglot /en/ 页面: {len(en_html)} 个")
        else:
            warn_msg("Polyglot /en/ 目录不存在")
else:
    fail_msg("未找到文章页面")

# ============================================================
# 8. SEO 和 meta 标签检查
# ============================================================

section("检查 7/7: SEO 和 Meta 标签完整性")

# 检查首页 SEO
index_file = SITE_DIR / "index.html"
if index_file.exists():
    content = index_file.read_text(encoding="utf-8", errors="replace")

    checks = [
        ("<title>", "title 标签"),
        ('name="description"', "meta description"),
        ('property="og:title"', "Open Graph title"),
        ('property="og:description"', "Open Graph description"),
        ('property="og:url"', "Open Graph URL"),
        ('property="og:image"', "Open Graph image"),
        ('name="twitter:card"', "Twitter Card"),
        ('rel="canonical"', "canonical URL"),
        ('lang=', "lang 属性"),
    ]

    for pattern, name in checks:
        if pattern in content:
            pass_msg(f"首页 {name}")
        else:
            warn_msg(f"首页缺少 {name}")

    # 检查 structured data (JSON-LD)
    if '"@type"' in content and '"application/ld+json"' in content:
        pass_msg("首页 JSON-LD 结构化数据")
    else:
        warn_msg("首页缺少 JSON-LD 结构化数据")

# 检查文章页 SEO
if post_dirs:
    sample_post = SITE_DIR / sorted(post_dirs)[0] / "index.html"
    if sample_post.exists():
        content = sample_post.read_text(encoding="utf-8", errors="replace")

        checks = [
            ("<title>", "title 标签"),
            ('property="og:type"', "og:type (article)"),
            ('property="article:published_time"', "article 发布时间"),
            ('rel="canonical"', "canonical URL"),
        ]

        for pattern, name in checks:
            if pattern in content:
                pass_msg(f"文章页 {name}")
            else:
                warn_msg(f"文章页缺少 {name}")

# ============================================================
# 汇总
# ============================================================

section("资源完整性检查汇总")

total = pass_count + fail_count + warn_count
print()
print(f"  {GREEN}PASS{NC}: {pass_count} / {total}")
print(f"  {RED}FAIL{NC}: {fail_count} / {total}")
print(f"  {YELLOW}WARN{NC}: {warn_count} / {total}")
print()

# 统计
print(f"  {BLUE}资源统计{NC}:")
print(f"    HTML 页面:   {len(html_files)}")
print(f"    CSS 文件:    {len(css_files)}")
print(f"    JS 文件:     {len(js_files)}")
print(f"    图片文件:    {len(img_files)}")
print(f"    资源引用:    {total_resources}")
print(f"    缺失资源:    {len(all_missing)}")
print(f"    空文件:      {len(all_empty)}")
print(f"    文章页面:    {len(post_dirs)}")
print()

if fail_count == 0:
    if warn_count == 0:
        print(f"  {GREEN}========================================{NC}")
        print(f"  {GREEN}  ALL PASSED - 资源完整性 OK{NC}")
        print(f"  {GREEN}========================================{NC}")
    else:
        print(f"  {YELLOW}========================================{NC}")
        print(f"  {YELLOW}  PASSED with {warn_count} warning(s){NC}")
        print(f"  {YELLOW}========================================{NC}")
    sys.exit(0)
else:
    print(f"  {RED}========================================{NC}")
    print(f"  {RED}  FAILED: {fail_count} error(s){NC}")
    print(f"  {RED}========================================{NC}")
    sys.exit(1)
