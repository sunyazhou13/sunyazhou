#!/usr/bin/env python3
"""
博客运行时资源加载检查 (Runtime Resource Check)

两层检查：
  Layer 1 (HTTP)：全量页面，逐页 GET，解析 HTML 提取所有资源引用，
                  对每个资源发起 HTTP 请求检查状态码和响应时间。
  Layer 2 (Headless)：抽样页面（首页 + 随机 N 篇文章），用 Playwright
                       无头浏览器渲染，捕获 JS console error、
                       失败的网络请求、DOM 结构完整性、懒加载资源、
                       外部 CDN 可用性。

用法:
  python3 tools/runtime-check.py --base-url http://127.0.0.1:14000
  python3 tools/runtime-check.py --base-url http://127.0.0.1:14000 --headless 10
  python3 tools/runtime-check.py --base-url http://127.0.0.1:14000 --no-headless

依赖:
  Layer 1: requests (pip install requests)
  Layer 2: playwright (pip install playwright && playwright install chromium)
"""

import argparse
import os
import re
import random
import sys
import time
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

# 推导项目根目录和 _site 路径（兼容直接运行和 exec 调用）
try:
    _SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = _SCRIPT_DIR.parent
except NameError:
    PROJECT_ROOT = Path.cwd()
SITE_DIR = PROJECT_ROOT / "_site"

# 颜色
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"

pass_count = 0
fail_count = 0
warn_count = 0
skip_count = 0


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


def skip_msg(msg):
    global skip_count
    print(f"  {CYAN}[SKIP]{NC} {msg}")
    skip_count += 1


def section(title):
    print(f"\n{CYAN}{'=' * 60}{NC}")
    print(f"{CYAN}  {title}{NC}")
    print(f"{CYAN}{'=' * 60}{NC}")


# ============================================================
# Layer 1: HTTP 全量检查
# ============================================================

class ResourceExtractor(HTMLParser):
    """从 HTML 中提取所有资源引用，同时检测 SEO/结构问题"""

    def __init__(self, page_url):
        super().__init__()
        self.page_url = page_url
        self.resources = []  # (url, resource_type, tag, line)
        self.inline_scripts = 0
        self.has_title = False
        self.has_meta_description = False
        self.has_canonical = False
        self.has_og_image = False
        self.mixed_content = []  # (resource_url, tag)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        line = self.getpos()[0]

        # SEO/结构检测
        if tag == "title":
            self.has_title = True
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name == "description":
                self.has_meta_description = True
            if prop == "og:image":
                self.has_og_image = True
        if tag == "link":
            if attrs_dict.get("rel", "").lower() == "canonical":
                self.has_canonical = True

        # <link rel="stylesheet" href="...">
        if tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "")
            if href and not href.startswith(("data:", "mailto:", "tel:", "#")):
                if "stylesheet" in rel:
                    self.resources.append((href, "css", tag, line))
                elif "icon" in rel or "apple-touch" in rel or "manifest" in rel:
                    self.resources.append((href, "favicon", tag, line))
                elif "preload" in rel or "prefetch" in rel:
                    self.resources.append((href, "preload", tag, line))

        # <script src="...">
        elif tag == "script":
            src = attrs_dict.get("src", "")
            if src and not src.startswith(("data:", "inline")):
                self.resources.append((src, "js", tag, line))
                # 混合内容检测：https 页面引用 http 资源
                if src.startswith("http://"):
                    self.mixed_content.append((src, tag))
            else:
                self.inline_scripts += 1

        # <img src="...">
        elif tag == "img":
            src = attrs_dict.get("src", "") or attrs_dict.get("data-src", "")
            if src and not src.startswith(("data:", "blob:")):
                self.resources.append((src, "img", tag, line))

        # <source src="..."> (for <picture> and <video>/<audio>)
        elif tag == "source":
            src = attrs_dict.get("src", "")
            if not src and attrs_dict.get("srcset"):
                src = attrs_dict.get("srcset", "").split()[0]
            if src and not src.startswith(("data:", "blob:")):
                self.resources.append((src, "media", tag, line))

        # <use href="..."> (SVG sprite references)
        elif tag == "use":
            href = attrs_dict.get("href", "") or attrs_dict.get("xlink:href", "")
            if href and not href.startswith("#"):
                self.resources.append((href, "svg", tag, line))

        # <iframe src="...">
        elif tag == "iframe":
            src = attrs_dict.get("src", "")
            if src and not src.startswith(("data:", "about:")):
                self.resources.append((src, "iframe", tag, line))


def discover_pages(base_url, requests_lib):
    """从 sitemap.xml 发现所有页面 URL，并归一化到 base_url 域名"""
    sitemap_url = urljoin(base_url, "/sitemap.xml")
    try:
        resp = requests_lib.get(sitemap_url, timeout=10)
        if resp.status_code != 200:
            warn_msg(f"sitemap.xml 返回 {resp.status_code}，回退到文件系统扫描")
            return _discover_from_filesystem(base_url)
        urls = re.findall(r"<loc>(.*?)</loc>", resp.text)
        base_parsed = urlparse(base_url)
        html_urls = []
        for url in urls:
            if url.endswith(".xml") or url.endswith(".css") or url.endswith(".js"):
                continue
            # 归一化：无论 sitemap 中 URL 指向生产域名还是 localhost，
            # 统一替换为 base_url 的 scheme+netloc，只保留 path
            parsed = urlparse(url)
            normalized = f"{base_parsed.scheme}://{base_parsed.netloc}{parsed.path}"
            if parsed.query:
                normalized += f"?{parsed.query}"
            html_urls.append(normalized)
        return html_urls
    except Exception as e:
        warn_msg(f"获取 sitemap.xml 失败: {e}，回退到文件系统扫描")
        return _discover_from_filesystem(base_url)


def _discover_from_filesystem(base_url):
    """从 _site 目录扫描所有 HTML 页面，构建 URL 列表"""
    if not SITE_DIR.exists():
        return [base_url]
    parsed = urlparse(base_url)
    base_path = parsed.path.rstrip("/")
    urls = []
    for html_file in sorted(SITE_DIR.rglob("*.html")):
        rel = html_file.relative_to(SITE_DIR)
        if rel.name == "index.html":
            url_path = f"{base_path}/{rel.parent}/"
        else:
            url_path = f"{base_path}/{rel}"
        url_path = url_path.replace("//", "/")
        urls.append(f"{parsed.scheme}://{parsed.netloc}{url_path}")
    return urls


# 响应时间阈值（秒）
SLOW_THRESHOLD = 3.0
VERY_SLOW_THRESHOLD = 10.0


def run_http_check(base_url, requests_lib, max_pages=None):
    """Layer 1: HTTP 全量检查"""
    section("Layer 1: HTTP 全量资源加载检查")

    pages = discover_pages(base_url, requests_lib)
    info_msg(f"发现 {len(pages)} 个页面")

    if max_pages and len(pages) > max_pages:
        info_msg(f"限制检查前 {max_pages} 个页面（--max-pages）")
        pages = pages[:max_pages]

    total_resources = 0
    failed_resources = defaultdict(list)  # status_code -> [(page_url, resource_url, rtype)]
    page_errors = []  # (page_url, error_desc)
    slow_resources = []  # (resource_url, rtype, elapsed, page_url)
    type_ok = defaultdict(int)
    type_fail = defaultdict(int)
    seo_issues = []  # (page_url, issue)
    mixed_content_issues = []  # (page_url, resource_url, tag)
    external_resources = set()  # 收集外部资源 URL 用于抽样检查

    start_time = time.time()
    pages_checked = 0

    for page_url in pages:
        pages_checked += 1
        if pages_checked % 100 == 0:
            info_msg(f"进度: {pages_checked}/{len(pages)} 页...")

        try:
            resp = requests_lib.get(page_url, timeout=10)
        except Exception as e:
            page_errors.append((page_url, str(e)))
            continue

        if resp.status_code != 200:
            page_errors.append((page_url, f"HTTP {resp.status_code}"))
            continue

        # 跳过非 HTML 内容（如 llms-full.txt, robots.txt, .xml 等）
        content_type = resp.headers.get("Content-Type", "")
        page_path = urlparse(page_url).path
        is_html = "html" in content_type.lower() or page_path.endswith(("/", ".html", ".htm"))
        if not is_html:
            continue

        # 解析 HTML 提取资源
        extractor = ResourceExtractor(page_url)
        try:
            extractor.feed(resp.text)
        except Exception:
            pass

        # SEO 检查
        page_path = urlparse(page_url).path
        if not extractor.has_title:
            seo_issues.append((page_url, "缺少 <title>"))
        if not extractor.has_meta_description:
            seo_issues.append((page_url, "缺少 meta description"))
        if not extractor.has_canonical:
            seo_issues.append((page_url, "缺少 canonical link"))
        if not extractor.has_og_image:
            seo_issues.append((page_url, "缺少 og:image"))

        # 混合内容检测
        if base_url.startswith("https://"):
            for res_url, tag in extractor.mixed_content:
                mixed_content_issues.append((page_url, res_url, tag))

        # 逐个检查资源
        seen = set()
        for resource_url, rtype, tag, line in extractor.resources:
            abs_url = urljoin(page_url, resource_url)
            parsed = urlparse(abs_url)
            base_parsed = urlparse(base_url)

            # 收集外部资源
            if parsed.netloc and parsed.netloc != base_parsed.netloc:
                external_resources.add((abs_url, rtype))
                continue

            # 去重（同一页面同一资源只检查一次）
            key = (abs_url, rtype)
            if key in seen:
                continue
            seen.add(key)
            total_resources += 1

            try:
                res_start = time.time()
                res_resp = requests_lib.head(abs_url, timeout=10, allow_redirects=True)
                # HEAD 可能被某些服务器拒绝，降级为 GET
                if res_resp.status_code == 405:
                    res_resp = requests_lib.get(abs_url, timeout=10, stream=True)
                    res_resp.close()

                res_elapsed = time.time() - res_start
                status = res_resp.status_code

                if status == 200:
                    type_ok[rtype] += 1
                    if res_elapsed > SLOW_THRESHOLD:
                        slow_resources.append((abs_url, rtype, res_elapsed, page_url))
                else:
                    failed_resources[status].append((page_url, abs_url, rtype))
                    type_fail[rtype] += 1
            except Exception as e:
                failed_resources["EXC"].append((page_url, abs_url, f"{rtype}: {e}"))
                type_fail[rtype] += 1

    elapsed = time.time() - start_time

    # ---- 报告 ----
    info_msg(f"检查完成: {pages_checked} 页, {total_resources} 个本地资源, 耗时 {elapsed:.1f}s")

    # 页面加载
    if page_errors:
        fail_msg(f"{len(page_errors)} 个页面加载失败")
        for url, err in page_errors[:5]:
            print(f"      {url} -> {err}")
        if len(page_errors) > 5:
            print(f"      ... 还有 {len(page_errors) - 5} 个")
    else:
        pass_msg(f"全部 {pages_checked} 个页面 HTTP 200")

    # 资源加载
    total_fail = sum(type_fail.values())
    total_ok = sum(type_ok.values())
    if total_fail == 0:
        type_summary = ", ".join(f"{k}:{v}" for k, v in sorted(type_ok.items()))
        pass_msg(f"全部 {total_ok} 个本地资源加载成功 ({type_summary})")
    else:
        type_fail_str = ", ".join(f"{k}:{v}" for k, v in sorted(type_fail.items()) if v > 0)
        fail_msg(f"{total_fail} 个资源加载失败 ({type_fail_str})")
        for status, items in sorted(failed_resources.items()):
            label = "异常" if status == "EXC" else f"HTTP {status}"
            print(f"      {label} ({len(items)} 个):")
            for page_url, res_url, rtype in items[:3]:
                print(f"        [{rtype}] {res_url}")
                print(f"          <- {page_url}")
            if len(items) > 3:
                print(f"        ... 还有 {len(items) - 3} 个")

    # 慢资源
    if slow_resources:
        warn_msg(f"{len(slow_resources)} 个资源响应缓慢 (>{SLOW_THRESHOLD}s)")
        for res_url, rtype, res_time, page_url in sorted(slow_resources, key=lambda x: -x[2])[:5]:
            print(f"      [{rtype}] {res_time:.2f}s  {res_url}")
            print(f"        <- {page_url}")
        if len(slow_resources) > 5:
            print(f"      ... 还有 {len(slow_resources) - 5} 个")

    # SEO 检查
    if seo_issues:
        # 按问题类型分组统计
        issue_types = defaultdict(int)
        for _, issue in seo_issues:
            issue_types[issue] += 1
        warn_msg(f"SEO 问题: {len(seo_issues)} 项")
        for issue, count in sorted(issue_types.items(), key=lambda x: -x[1]):
            print(f"      {issue}: {count} 页")
    else:
        pass_msg("SEO 结构完整 (title/meta/canonical/og:image)")

    # 混合内容
    if mixed_content_issues:
        fail_msg(f"混合内容: {len(mixed_content_issues)} 个 http:// 资源在 https:// 页面中")
        for page_url, res_url, tag in mixed_content_issues[:3]:
            print(f"      [{tag}] {res_url}")
            print(f"        <- {page_url}")
    else:
        pass_msg("无混合内容问题")

    # 外部资源汇总
    if external_resources:
        info_msg(f"发现 {len(external_resources)} 个外部资源（CDN 等），将在 Layer 2 抽样检查")

    # 性能指标
    avg_time = elapsed / pages_checked if pages_checked > 0 else 0
    avg_res = total_resources / pages_checked if pages_checked > 0 else 0
    info_msg(f"平均每页耗时: {avg_time:.2f}s, 资源密度: {avg_res:.1f} 资源/页")

    return total_fail == 0 and not page_errors and not mixed_content_issues


# ============================================================
# Layer 2: Headless 浏览器抽样检查
# ============================================================

def run_headless_check(base_url, requests_lib, sample_count=5, external_resources=None):
    """Layer 2: Playwright 无头浏览器深度检查"""
    section("Layer 2: Headless 浏览器渲染检查")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        skip_msg("Playwright 未安装，跳过 headless 检查")
        return True

    # 选择抽样页面：首页 + 随机 N 篇文章
    pages = discover_pages(base_url, requests_lib)
    article_pages = [p for p in pages if re.search(r"/20\d{2}/\d{2}/", p)]

    sample_pages = [base_url + "/"]  # 首页
    if article_pages:
        sample_count = min(sample_count, len(article_pages))
        sample_pages.extend(random.sample(article_pages, sample_count))

    info_msg(f"将对 {len(sample_pages)} 个页面进行 headless 渲染检查")

    total_console_errors = 0
    total_failed_requests = 0
    total_render_errors = 0
    total_lazy_failures = 0
    total_external_failures = 0
    page_results = []

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (compatible; BlogBaselineTest/1.0)"
            )

            for page_url in sample_pages:
                page = context.new_page()
                console_errors = []
                failed_requests = []
                all_requests = []

                # 捕获 console 错误，过滤本地环境噪音
                def on_console(msg, _url=page_url):
                    if msg.type != "error":
                        return
                    text = msg.text
                    # 过滤 Giscus 评论系统在本地环境产生的预期噪音
                    if "giscus.app" in text or "github.githubassets.com" in text:
                        return
                    # 过滤浏览器级资源加载错误（来自 Giscus iframe、Google Fonts 等外部资源）
                    # 这些错误在本地环境是预期的，真正的 JS 错误由 pageerror 捕获
                    if "Failed to load resource" in text:
                        return
                    console_errors.append(text)
                page.on("console", on_console)
                page.on("pageerror", lambda err: console_errors.append(str(err)) if "giscus" not in str(err).lower() else None)

                # 捕获所有网络请求（用于检测懒加载和外部资源）
                def on_response(response, _url=page_url):
                    all_requests.append((response.url, response.status, response.request.resource_type))
                    if response.status >= 400:
                        # 过滤 Giscus 评论系统在本地环境的预期 404
                        if "giscus.app" in response.url:
                            return
                        failed_requests.append((response.url, response.status))
                page.on("response", on_response)

                try:
                    response = page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
                    # 等待初始资源加载
                    page.wait_for_load_state("networkidle", timeout=10000)
                    # 滚动页面触发懒加载
                    page.evaluate("""
                        async () => {
                            await new Promise(resolve => {
                                let total = 0;
                                const step = 300;
                                const timer = setInterval(() => {
                                    window.scrollBy(0, step);
                                    total += step;
                                    if (total >= document.body.scrollHeight) {
                                        clearInterval(timer);
                                        // 滚回顶部
                                        window.scrollTo(0, 0);
                                        resolve();
                                    }
                                }, 100);
                            });
                        }
                    """)
                    # 滚动后等待网络请求完成
                    page.wait_for_timeout(2000)

                    # DOM 结构完整性检查
                    has_title = page.title() != ""
                    has_body = page.query_selector("body") is not None
                    has_content = page.evaluate("document.body.innerText.length > 100")
                    has_main = page.query_selector("main, #post-wrapper, .post-content, article") is not None
                    has_nav = page.query_selector("nav, .navbar, #sidebar") is not None

                    # CSS 是否生效（检查元素的计算样式）
                    css_applied = page.evaluate("""
                        () => {
                            const el = document.querySelector('.post-content, .post, main, body');
                            if (!el) return false;
                            const style = window.getComputedStyle(el);
                            // 如果 display:none 说明 CSS 没加载
                            return style.display !== 'none';
                        }
                    """)

                    render_ok = has_title and has_body and has_content
                    css_ok = css_applied and has_main
                except Exception as e:
                    render_ok = False
                    css_ok = False
                    console_errors.append(f"Navigation error: {e}")
                    has_nav = False
                    response = None

                total_console_errors += len(console_errors)
                total_failed_requests += len(failed_requests)
                if not render_ok:
                    total_render_errors += 1

                # 检查懒加载图片是否实际加载
                lazy_images = page.query_selector_all("img[data-src], img[loading='lazy']")
                lazy_loaded = 0
                lazy_not_loaded = 0
                for img in lazy_images:
                    src = img.get_attribute("src") or ""
                    data_src = img.get_attribute("data-src") or ""
                    if data_src and src == data_src:
                        lazy_loaded += 1
                    elif data_src and src != data_src and not src.startswith("data:"):
                        lazy_not_loaded += 1
                    elif src and not src.startswith("data:"):
                        lazy_loaded += 1
                if lazy_not_loaded > 0:
                    total_lazy_failures += lazy_not_loaded

                page_results.append({
                    "url": page_url,
                    "render_ok": render_ok,
                    "css_ok": css_ok,
                    "has_nav": has_nav,
                    "console_errors": console_errors,
                    "failed_requests": failed_requests,
                    "lazy_total": len(lazy_images),
                    "lazy_loaded": lazy_loaded,
                    "lazy_not_loaded": lazy_not_loaded,
                    "total_requests": len(all_requests),
                })

                page.close()

            # ---- 外部资源抽样检查 ----
            # 跳过本地环境无法访问的 CDN（Google Fonts 等）
            SKIP_EXT_DOMAINS = ["fonts.gstatic.com", "fonts.googleapis.com"]
            if external_resources:
                filtered_ext = [(u, t) for u, t in external_resources
                                 if not any(d in u for d in SKIP_EXT_DOMAINS)]
                if filtered_ext:
                    info_msg(f"检查 {min(len(filtered_ext), 20)} 个外部资源...")
                    ext_sample = random.sample(list(filtered_ext), min(len(filtered_ext), 20))
                    ext_page = context.new_page()
                    for ext_url, rtype in ext_sample:
                        try:
                            ext_resp = ext_page.request.head(ext_url, timeout=10000)
                            if ext_resp.status >= 400:
                                total_external_failures += 1
                                print(f"      [{rtype}] HTTP {ext_resp.status} {ext_url[:100]}")
                        except Exception:
                            total_external_failures += 1
                            print(f"      [{rtype}] 超时/失败 {ext_url[:100]}")
                    ext_page.close()

            browser.close()
    except Exception as e:
        fail_msg(f"Playwright 启动失败: {e}")
        return False

    # ---- 报告 ----
    for result in page_results:
        url_short = result["url"].replace(base_url, "") or "/"
        issues = []
        if not result["render_ok"]:
            issues.append("渲染异常")
        if not result["css_ok"]:
            issues.append("CSS 未生效")
        if result["console_errors"]:
            issues.append(f"{len(result['console_errors'])} 个 JS 错误")
        if result["failed_requests"]:
            issues.append(f"{len(result['failed_requests'])} 个失败请求")
        if result["lazy_not_loaded"]:
            issues.append(f"{result['lazy_not_loaded']} 个懒加载图片未加载")

        if not issues:
            pass_msg(f"渲染正常: {url_short} ({result['total_requests']} 请求, {result['lazy_loaded']}/{result['lazy_total']} 懒加载)")
        else:
            if not result["render_ok"]:
                fail_msg(f"渲染异常: {url_short}")
            else:
                warn_msg(f"渲染完成但有问题: {url_short} ({', '.join(issues)})")

            if result["console_errors"]:
                for err in result["console_errors"][:3]:
                    print(f"      JS: {err[:120]}")
            if result["failed_requests"]:
                for req_url, status in result["failed_requests"][:3]:
                    print(f"      [{status}] {req_url[:120]}")
            if result["lazy_not_loaded"]:
                print(f"      懒加载: {result['lazy_loaded']}/{result['lazy_total']} 已加载, {result['lazy_not_loaded']} 未加载")

    # 外部资源
    if external_resources:
        if total_external_failures == 0:
            pass_msg(f"外部资源检查通过 ({min(len(external_resources), 20)} 个抽样)")
        else:
            warn_msg(f"外部资源: {total_external_failures} 个失败")

    info_msg(f"Headless 汇总: {len(sample_pages)} 页, "
             f"{total_console_errors} JS错误, {total_failed_requests} 失败请求, "
             f"{total_render_errors} 渲染异常, {total_lazy_failures} 懒加载失败")

    return total_render_errors == 0


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="博客运行时资源加载检查")
    parser.add_argument("--base-url", default="http://127.0.0.1:14000",
                        help="Jekyll serve 基础 URL")
    parser.add_argument("--headless", type=int, default=5, nargs="?", const=5,
                        help="Headless 抽样页面数 (默认: 5)")
    parser.add_argument("--no-headless", action="store_true",
                        help="跳过 headless 检查")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="HTTP 层最大检查页面数 (默认: 全部)")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    # 检查 requests 库
    try:
        import requests
    except ImportError:
        print(f"{RED}错误: requests 库未安装{NC}")
        print(f"  安装: pip install requests")
        sys.exit(1)

    # 检查服务是否在线
    try:
        resp = requests.get(base_url + "/", timeout=5)
        if resp.status_code != 200:
            print(f"{RED}错误: {base_url} 返回 {resp.status_code}{NC}")
            sys.exit(1)
    except Exception as e:
        print(f"{RED}错误: 无法连接 {base_url}: {e}{NC}")
        print(f"  请先启动 Jekyll serve: bundle exec jekyll serve -P 14000 --no-watch")
        sys.exit(1)

    print(f"\n{CYAN}博客运行时资源加载检查{NC}")
    print(f"  目标: {base_url}")
    print(f"  时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Layer 1: HTTP 全量检查
    http_ok = run_http_check(base_url, requests, args.max_pages)

    # 收集外部资源传给 Layer 2
    external_resources = set()
    # 重新扫描一次收集外部资源（轻量操作，只看首页和几篇文章）
    pages = discover_pages(base_url, requests)
    sample_for_external = [pages[0]] if pages else []
    if len(pages) > 1:
        sample_for_external.append(pages[len(pages) // 2])
    if len(pages) > 2:
        sample_for_external.append(pages[-1])
    for page_url in sample_for_external:
        try:
            resp = requests.get(page_url, timeout=10)
            extractor = ResourceExtractor(page_url)
            extractor.feed(resp.text)
            for resource_url, rtype, tag, line in extractor.resources:
                abs_url = urljoin(page_url, resource_url)
                parsed = urlparse(abs_url)
                base_parsed = urlparse(base_url)
                if parsed.netloc and parsed.netloc != base_parsed.netloc:
                    external_resources.add((abs_url, rtype))
        except Exception:
            pass

    # Layer 2: Headless 抽样检查
    headless_ok = True
    if not args.no_headless and args.headless > 0:
        headless_ok = run_headless_check(base_url, requests, args.headless, external_resources)

    # 汇总
    section("运行时检查汇总")
    print(f"  {GREEN}PASS{NC}: {pass_count}")
    print(f"  {RED}FAIL{NC}: {fail_count}")
    print(f"  {YELLOW}WARN{NC}: {warn_count}")
    print(f"  {CYAN}SKIP{NC}: {skip_count}")
    print()

    if fail_count == 0:
        if warn_count == 0:
            print(f"  {GREEN}========================================{NC}")
            print(f"  {GREEN}  ALL PASSED{NC}")
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


if __name__ == "__main__":
    main()
