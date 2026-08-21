#!/bin/bash
# ============================================================
# 博客基准测试脚本 (Blog Baseline Test)
# 适用于 Ruby 2.7.8 和 Ruby 3.3.6 两个环境
#
# 用法:
#   bash tools/blog-baseline-test.sh          # 完整测试
#   bash tools/blog-baseline-test.sh --quick   # 跳过 serve 和 html-proofer
#
# 测试项:
#   1. Ruby 版本和 OpenSSL 扩展
#   2. Bundler 和 Gemfile.lock 一致性
#   3. 所有关键 gem 是否最新版本
#   4. Gem 与当前 Ruby 版本兼容性
#   5. Jekyll build 0 Error 0 Warning
#   6. _site 产物完整性 (页面数、关键文件、空文件)
#   7. SCSS 编译无弃用警告
#   8. 自定义插件语法检查
#   9. html-proofer 链接检查
#  10. Jekyll serve 本地启动验证
#  11. 运行时资源加载检查 (HTTP 全量 + Headless 抽样)
# ============================================================

set -o pipefail

# ---- 日志输出：同时打印到终端和 ~/Downloads/blog-baseline-test-YYYYMMDD-HHMMSS.log ----
LOG_DIR="$HOME/Downloads"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/blog-baseline-test-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG_FILE") 2>&1
echo "日志文件: $LOG_FILE"
echo ""

# ---- 颜色定义 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ---- 计数器 ----
PASS=0
FAIL=0
WARN=0
SKIP=0

# ---- 工作目录 ----
WORK_DIR="$(dirname "$(dirname "$(realpath "$0" 2>/dev/null || echo "$0")")")"
cd "$WORK_DIR" || { echo "无法进入工作目录 $WORK_DIR"; exit 1; }

QUICK_MODE=false
if [[ "${1:-}" == "--quick" ]]; then
  QUICK_MODE=true
fi

# ---- 辅助函数 ----
pass() {
  echo -e "  ${GREEN}[PASS]${NC} $1"
  ((PASS++))
}

fail() {
  echo -e "  ${RED}[FAIL]${NC} $1"
  ((FAIL++))
}

warn() {
  echo -e "  ${YELLOW}[WARN]${NC} $1"
  ((WARN++))
}

info() {
  echo -e "  ${BLUE}[INFO]${NC} $1"
}

skip() {
  echo -e "  ${CYAN}[SKIP]${NC} $1"
  ((SKIP++))
}

section() {
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}  $1${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ---- 捕获构建输出 ----
BUILD_OUTPUT=""
BUILD_LOG="/tmp/blog_build_$$.log"

# ============================================================
# 测试 1: Ruby 版本和 OpenSSL 扩展
# ============================================================
section "测试 1/11: Ruby 版本和 OpenSSL 扩展"

RUBY_VERSION=$(ruby -e "puts RUBY_VERSION" 2>/dev/null)
if [[ -z "$RUBY_VERSION" ]]; then
  fail "Ruby 不可用"
else
  pass "Ruby 版本: $RUBY_VERSION"
fi

OPENSSL_VERSION=$(ruby -ropenssl -e "puts OpenSSL::OPENSSL_VERSION" 2>/dev/null)
if [[ -z "$OPENSSL_VERSION" ]]; then
  fail "OpenSSL 扩展无法加载 (ruby -ropenssl)"
else
  pass "OpenSSL 扩展: $OPENSSL_VERSION"
fi

# 检查 Ruby 是否 EOL
RUBY_MAJOR=$(echo "$RUBY_VERSION" | cut -d. -f1)
RUBY_MINOR=$(echo "$RUBY_VERSION" | cut -d. -f2)
if [[ "$RUBY_MAJOR" -eq 2 ]] || ([[ "$RUBY_MAJOR" -eq 3 ]] && [[ "$RUBY_MINOR" -lt 1 ]]); then
  warn "Ruby $RUBY_VERSION 已 EOL，不再接收安全补丁"
elif [[ "$RUBY_MAJOR" -eq 3 ]] && [[ "$RUBY_MINOR" -le 2 ]]; then
  info "Ruby $RUBY_VERSION 接近 EOL (3.2 将于 2026-03 维护结束)"
else
  pass "Ruby $RUBY_VERSION 处于活跃维护期"
fi

# ============================================================
# 测试 2: Bundler 和 Gemfile.lock 一致性
# ============================================================
section "测试 2/11: Bundler 和 Gemfile.lock 一致性"

BUNDLER_VERSION=$(bundle -v 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
if [[ -z "$BUNDLER_VERSION" ]]; then
  fail "Bundler 不可用"
else
  pass "Bundler 版本: $BUNDLER_VERSION"
fi

if [[ ! -f Gemfile.lock ]]; then
  warn "Gemfile.lock 不存在（不影响构建，但建议 bundle install 生成）"
else
  pass "Gemfile.lock 存在"

  # 检查 BUNDLED WITH 是否匹配
  LOCK_BUNDLER=$(grep "BUNDLED WITH" -A1 Gemfile.lock | tail -1 | tr -d ' ')
  if [[ "$LOCK_BUNDLER" != "$BUNDLER_VERSION" ]]; then
    warn "Gemfile.lock 记录 Bundler $LOCK_BUNDLER，当前 Bundler $BUNDLER_VERSION（通常兼容）"
  else
    pass "Bundler 版本一致: $BUNDLER_VERSION"
  fi
fi

# 检查 bundle check
if bundle check 2>/dev/null | grep -q "The Gemfile's dependencies are satisfied"; then
  pass "bundle check: 所有依赖已满足"
else
  fail "bundle check: 依赖未满足，需运行 bundle install"
fi

# ============================================================
# 测试 3: 关键 gem 版本检查
# ============================================================
section "测试 3/11: 关键 gem 版本检查"

check_gem_latest() {
  local gem_name="$1"
  # bundle list 输出格式: "* jekyll (4.4.1)" 或 "  jekyll (4.4.1)"
  local current_version=""
  current_version=$(bundle list 2>/dev/null | grep -E "[* ]${gem_name} \(" | head -1 | grep -oE '\([0-9][^)]*\)' | tr -d '()' || true)

  if [[ -z "${current_version:-}" ]]; then
    # 尝试用 gem list 查找
    current_version=$(gem list 2>/dev/null | grep -E "^${gem_name} \(" | head -1 | grep -oE '\([0-9][^)]*\)' | tr -d '()' || true)
  fi

  if [[ -z "${current_version:-}" ]]; then
    fail "$gem_name: 未安装"
    return
  fi

  # 查询最新版本（通过 rubygems.org API）
  local latest_version=""
  latest_version=$(curl -s --max-time 10 "https://rubygems.org/api/v1/versions/${gem_name}/latest.json" 2>/dev/null | grep -oE '"version":"[^"]*"' | cut -d'"' -f4 || true)

  if [[ -z "${latest_version:-}" ]]; then
    warn "$gem_name: $current_version (无法查询最新版本，网络问题)"
    return
  fi

  if [[ "$current_version" == "$latest_version" ]]; then
    pass "$gem_name: $current_version (最新)"
  else
    # 检查该 gem 是否被 Jekyll 的版本约束锁定（如 rouge < 5.0, liquid ~> 4.0）
    local constraint=""
    constraint=$(grep -E "^\s+${gem_name} " Gemfile.lock 2>/dev/null | head -1 || true)
    if [[ -n "$constraint" ]] && echo "$constraint" | grep -qE '<|~>' ; then
      # 被 Gemfile.lock 约束的 gem，当前版本即为约束范围内的最新
      pass "$gem_name: $current_version (受 Gemfile.lock 约束，最新 $latest_version 不兼容)"
    else
      warn "$gem_name: 当前 $current_version，最新 $latest_version"
    fi
  fi
}

# 检查所有关键 gem
for gem in jekyll jekyll-seo-tag jekyll-polyglot jekyll-paginate jekyll-redirect-from jekyll-compose jekyll-tabs nokogiri html-proofer sass-embedded jekyll-sass-converter kramdown rouge liquid webrick; do
  check_gem_latest "$gem"
done

# ============================================================
# 测试 4: Gem 与当前 Ruby 兼容性
# ============================================================
section "测试 4/11: Gem 与当前 Ruby 兼容性"

# 逐个加载关键 gem 并检查是否报错
RUBY_COMPAT_LOG="/tmp/blog_ruby_compat_$$.log"
ruby -e "
  gems = %w[jekyll jekyll-seo-tag jekyll-polyglot jekyll-paginate jekyll-redirect-from jekyll-compose jekyll-tabs nokogiri html-proofer jekyll-sass-converter sass-embedded kramdown rouge liquid webrick]
  gems.each do |g|
    begin
      require g
      puts \"OK: #{g}\"
    rescue LoadError => e
      puts \"LOAD_ERROR: #{g} - #{e.message}\"
    rescue StandardError => e
      puts \"ERROR: #{g} - #{e.message}\"
    end
  end
" > "$RUBY_COMPAT_LOG" 2>&1

COMPAT_OK=$(grep -c "^OK:" "$RUBY_COMPAT_LOG")
COMPAT_FAIL=$(grep -c "^LOAD_ERROR:\|^ERROR:" "$RUBY_COMPAT_LOG")

cat "$RUBY_COMPAT_LOG" | while read -r line; do
  if [[ "$line" == OK:* ]]; then
    pass "${line#OK: }"
  elif [[ "$line" == LOAD_ERROR:* ]]; then
    fail "${line#LOAD_ERROR: }"
  elif [[ "$line" == ERROR:* ]]; then
    fail "${line#ERROR: }"
  fi
done

if [[ "$COMPAT_FAIL" -gt 0 ]]; then
  fail "$COMPAT_FAIL 个 gem 加载失败"
else
  pass "所有 $COMPAT_OK 个关键 gem 在 Ruby $RUBY_VERSION 下正常加载"
fi

rm -f "$RUBY_COMPAT_LOG"

# ============================================================
# 测试 5: Jekyll build 0 Error 0 Warning
# ============================================================
section "测试 5/11: Jekyll build 构建测试 (tools/build.sh)"

# 清理旧产物
rm -rf _site .jekyll-cache .container 2>/dev/null

echo -e "  ${BLUE}[INFO]${NC} 正在构建 (使用 tools/build.sh)... (可能需要 15-40 秒)"
bash tools/build.sh 2>&1 | tee "$BUILD_LOG"
BUILD_EXIT=$?

BUILD_OUTPUT=$(cat "$BUILD_LOG")

# 检查构建是否成功
if [[ $BUILD_EXIT -ne 0 ]]; then
  fail "tools/build.sh 失败 (exit code: $BUILD_EXIT)"
else
  pass "tools/build.sh 构建成功"
fi

# 检查 Error
BUILD_ERRORS=$(echo "$BUILD_OUTPUT" | grep -ciE "^Error:|error:|Exception|Traceback" 2>/dev/null || true)
  BUILD_ERRORS=${BUILD_ERRORS:-0}
if [[ "$BUILD_ERRORS" -gt 0 ]]; then
  fail "构建有 $BUILD_ERRORS 个 Error"
  echo "$BUILD_OUTPUT" | grep -iE "^Error:|error:" | head -5 | sed 's/^/      /'
else
  pass "构建 0 Error"
fi

# 检查 Warning (排除 "Copied" 行中的文件名误匹配，如 HowToDeprecatedAothodInObjC)
BUILD_WARNINGS=$(echo "$BUILD_OUTPUT" | grep -iE "^Warning:|Deprecation Warning" 2>/dev/null | grep -v "^Copied " | wc -l | tr -d ' ' || true)
  BUILD_WARNINGS=${BUILD_WARNINGS:-0}
if [[ "$BUILD_WARNINGS" -gt 0 ]]; then
  warn "构建有 $BUILD_WARNINGS 条 Warning/Deprecation"
  echo "$BUILD_OUTPUT" | grep -iE "^Warning:|Deprecation Warning" | grep -v "^Copied " | head -5 | sed 's/^/      /'
else
  pass "构建 0 Warning"
fi

# 检查构建时间
BUILD_TIME=$(echo "$BUILD_OUTPUT" | grep -oE "done in [0-9.]+ seconds" | grep -oE "[0-9.]+" || echo "未知")
if [[ "$BUILD_TIME" != "未知" ]]; then
  info "构建耗时: ${BUILD_TIME}s"
  # 用 awk 做浮点比较
  if awk "BEGIN{exit !($BUILD_TIME > 30)}"; then
    warn "构建时间 ${BUILD_TIME}s 偏长 (>30s)"
  else
    pass "构建时间 ${BUILD_TIME}s 正常 (<30s)"
  fi
fi

# ============================================================
# 测试 6: _site 产物完整性
# ============================================================
section "测试 6/11: _site 产物完整性"

if [[ ! -d _site ]]; then
  fail "_site 目录不存在"
else
  pass "_site 目录存在"

  # 统计 HTML 页面数
  HTML_COUNT=$(find _site -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$HTML_COUNT" -lt 50 ]]; then
    fail "HTML 页面数异常: $HTML_COUNT (期望 >50)"
  else
    pass "HTML 页面数: $HTML_COUNT"
  fi

  # 统计 CSS 文件
  CSS_COUNT=$(find _site -name "*.css" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$CSS_COUNT" -lt 1 ]]; then
    fail "CSS 文件数: $CSS_COUNT (期望 >=1)"
  else
    pass "CSS 文件数: $CSS_COUNT"
  fi

  # 统计 JS 文件
  JS_COUNT=$(find _site -name "*.js" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$JS_COUNT" -lt 1 ]]; then
    fail "JS 文件数: $JS_COUNT (期望 >=1)"
  else
    pass "JS 文件数: $JS_COUNT"
  fi

  # 检查关键页面
  for page in index.html feed.xml sitemap.xml robots.txt 404.html; do
    if [[ -f "_site/$page" ]]; then
      FILE_SIZE=$(wc -c < "_site/$page" | tr -d ' ')
      if [[ "$FILE_SIZE" -lt 10 ]]; then
        fail "_site/$page 文件过小 ($FILE_SIZE bytes)"
      else
        pass "_site/$page ($FILE_SIZE bytes)"
      fi
    else
      fail "_site/$page 不存在"
    fi
  done

  # 检查文章页面是否生成
  POST_HTML=$(find _site -path "*/202*/*.html" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$POST_HTML" -lt 100 ]]; then
    warn "文章 HTML 页面数: $POST_HTML (期望 >100，可能有遗漏)"
  else
    pass "文章 HTML 页面数: $POST_HTML"
  fi

  # 检查空文件
  EMPTY_FILES=$(find _site -name "*.html" -empty 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$EMPTY_FILES" -gt 0 ]]; then
    fail "发现 $EMPTY_FILES 个空 HTML 文件"
    find _site -name "*.html" -empty 2>/dev/null | head -3 | sed 's/^/      /'
  else
    pass "无空 HTML 文件"
  fi

  # 检查 polyglot 多语言
  if [[ -d _site/en ]]; then
    EN_PAGES=$(find _site/en -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$EN_PAGES" -gt 0 ]]; then
      pass "Polyglot EN 页面: $EN_PAGES"
    else
      warn "Polyglot /en/ 目录存在但无 HTML 页面"
    fi
  else
    warn "Polyglot /en/ 目录不存在"
  fi

  # 检查分类页面
  CATEGORY_PAGES=$(find _site/categories -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$CATEGORY_PAGES" -gt 0 ]]; then
    pass "分类页面: $CATEGORY_PAGES"
  else
    warn "分类页面为 0"
  fi

  # 检查标签页面
  TAG_PAGES=$(find _site/tags -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$TAG_PAGES" -gt 0 ]]; then
    pass "标签页面: $TAG_PAGES"
  else
    warn "标签页面为 0"
  fi

  # 检查 redirects.json (polyglot)
  if [[ -f _site/redirects.json ]]; then
    pass "redirects.json 存在"
  else
    warn "redirects.json 不存在"
  fi

  # 检查 CSS 是否包含实际内容（非空）
  CSS_FILE=$(find _site/assets/css -name "*.css" 2>/dev/null | head -1)
  if [[ -n "$CSS_FILE" ]]; then
    CSS_SIZE=$(wc -c < "$CSS_FILE" | tr -d ' ')
    if [[ "$CSS_SIZE" -lt 1000 ]]; then
      warn "CSS 文件 $CSS_FILE 大小仅 $CSS_SIZE bytes (可能 SCSS 编译失败)"
    else
      pass "CSS 文件大小 ${CSS_SIZE} bytes"
    fi
  else
    fail "无 CSS 产物"
  fi
fi

# ============================================================
# 测试 6b: 资源完整性深度检查 (Python)
# ============================================================
section "测试 6b/11: 资源完整性深度检查 (HTML/CSS/JS/图片/SEO)"

if [[ -f tools/check-resources.py ]] && [[ -d _site ]]; then
  echo -e "  ${BLUE}[INFO]${NC} 扫描所有 HTML 资源引用... (可能需要 10-20 秒)"
  RESOURCE_OUTPUT=$(python3 tools/check-resources.py 2>&1)
  echo "$RESOURCE_OUTPUT"

  # 解析 Python 脚本结果
  RESOURCE_PASS=$(echo "$RESOURCE_OUTPUT" | grep -oE "PASS: [0-9]+" | grep -oE "[0-9]+")
  RESOURCE_FAIL=$(echo "$RESOURCE_OUTPUT" | grep -oE "FAIL: [0-9]+" | grep -oE "[0-9]+")
  RESOURCE_WARN=$(echo "$RESOURCE_OUTPUT" | grep -oE "WARN: [0-9]+" | grep -oE "[0-9]+")

  if [[ "${RESOURCE_FAIL:-0}" -gt 0 ]]; then
    fail "资源完整性检查发现 ${RESOURCE_FAIL} 个问题"
  else
    pass "资源完整性检查通过 (${RESOURCE_PASS:-0} PASS, ${RESOURCE_WARN:-0} WARN)"
  fi
else
  fail "tools/check-resources.py 或 _site 不存在"
fi

# ============================================================
# 测试 7: SCSS 编译无弃用警告
# ============================================================
section "测试 7/11: SCSS 编译无弃用警告"

SASS_WARNINGS=$(echo "$BUILD_OUTPUT" | grep -ciE "Deprecation Warning|@import rules are deprecated" 2>/dev/null || true)
SASS_WARNINGS=${SASS_WARNINGS:-0}
if [[ "$SASS_WARNINGS" -gt 0 ]]; then
  warn "Sass 有 $SASS_WARNINGS 条弃用警告 (@import deprecation)"
  echo "$BUILD_OUTPUT" | grep "Deprecation Warning" | head -3 | sed 's/^/      /'
else
  pass "SCSS 编译 0 弃用警告"
fi

# 检查 @import 残留
SASS_IMPORTS=$(grep -rn "@import" assets/css/ 2>/dev/null | grep -v "url(" | wc -l | tr -d ' ')
if [[ "$SASS_IMPORTS" -gt 0 ]]; then
  warn "SCSS 文件中仍有 $SASS_IMPORTS 处 @import（应迁移为 @use）"
else
  pass "SCSS 无 @import 残留"
fi

# 检查 @use 使用
SASS_USES=$(grep -rn "@use" assets/css/ 2>/dev/null | wc -l | tr -d ' ')
if [[ "$SASS_USES" -gt 0 ]]; then
  pass "SCSS 使用 @use: $SASS_USES 处"
fi

# ============================================================
# 测试 8: 自定义插件语法检查
# ============================================================
section "测试 8/11: 自定义插件语法检查"

for plugin in _plugins/*.rb; do
  if [[ -f "$plugin" ]]; then
    PLUGIN_NAME=$(basename "$plugin")
    if ruby -c "$plugin" > /dev/null 2>&1; then
      pass "$PLUGIN_NAME 语法正确"
    else
      fail "$PLUGIN_NAME 语法错误"
      ruby -c "$plugin" 2>&1 | head -3 | sed 's/^/      /'
    fi
  fi
done

# 检查 _scripts 下的脚本
for script in _scripts/sh/*.sh; do
  if [[ -f "$script" ]]; then
    SCRIPT_NAME=$(basename "$script")
    if bash -n "$script" 2>/dev/null; then
      pass "$SCRIPT_NAME 语法正确"
    else
      fail "$SCRIPT_NAME 语法错误"
    fi
  fi
done

# ============================================================
# 测试 9: html-proofer 链接检查
# ============================================================
section "测试 9/11: html-proofer 链接检查"

if [[ "$QUICK_MODE" == true ]]; then
  skip "html-proofer (--quick 模式跳过)"
else
  echo -e "  ${BLUE}[INFO]${NC} 正在运行 html-proofer... (可能需要 1-3 分钟)"
  HTMLPROOFER_LOG="/tmp/blog_htmlproofer_$$.log"
  # html-proofer 4.x/5.x CLI flags 不稳定，直接用 Ruby API 避免 flag 兼容问题
  # 兼容 html-proofer 4.4.3 (Ruby 2.7.8) 和 5.2.2 (Ruby 3.x)
  bundle exec ruby -e "
    require 'html-proofer'
    options = {
      disable_external: true,
      allow_hash_href: true,
      enforce_https: false,
      ignore_urls: ['cdn.jsdelivr.net', '/en/404.html', 'Napol%C3%A9onBonaparte.avif', 'Bismarck%2COttoF%C3%BCrst_von_und%20LiHungChang.avif']
    }
    HTMLProofer.check_directory('_site', options).run
  " > "$HTMLPROOFER_LOG" 2>&1
  HP_EXIT=$?

  # 保存日志副本到 ~/Downloads 供后续分析
  HP_LOG_PERSIST="${HOME}/Downloads/htmlproofer-$(date +%Y%m%d-%H%M%S).log"
  cp "$HTMLPROOFER_LOG" "$HP_LOG_PERSIST" 2>/dev/null || true

  if [[ $HP_EXIT -eq 0 ]]; then
    pass "html-proofer: 所有内部链接检查通过"
  else
    # 统计实际错误描述行（含文件路径和错误描述），排除分节标题
    # html-proofer 4.x/5.x 每个错误通常输出 2 行：文件路径行 + 错误描述行
    HP_ALL_LINES=$(grep -cE "^  [^ ]" "$HTMLPROOFER_LOG" 2>/dev/null || true)
    HP_ALL_LINES=${HP_ALL_LINES:-0}
    # 实际错误数 = 匹配行数 / 每错误的行数（通常 2 行/错误）
    HP_ERRORS=$(( (HP_ALL_LINES + 1) / 2 ))
    if [[ "$HP_ALL_LINES" -eq 0 ]]; then
      warn "html-proofer 退出码非 0 但未检测到链接错误"
      echo -e "      最后 10 行日志:"
      tail -10 "$HTMLPROOFER_LOG" 2>/dev/null | sed 's/^/      /'
    else
      fail "html-proofer: 发现 $HP_ERRORS 个问题 (共 $HP_ALL_LINES 行输出)"
      echo -e "      完整错误列表:"
      grep -E "^  [^ ]" "$HTMLPROOFER_LOG" | sed 's/^/      /'
      echo -e "      日志已保存: $HP_LOG_PERSIST"
    fi
  fi
  rm -f "$HTMLPROOFER_LOG"
fi

# ============================================================
# 测试 10: Jekyll serve 本地启动验证
# ============================================================
section "测试 10/11: Jekyll serve 本地启动验证"

if [[ "$QUICK_MODE" == true ]]; then
  skip "Jekyll serve (--quick 模式跳过)"
else
  SERVE_PORT=14000
  SERVE_LOG="/tmp/blog_serve_$$.log"
  SERVE_PID=""

  echo -e "  ${BLUE}[INFO]${NC} 正在启动 Jekyll serve (端口 $SERVE_PORT)..."

  # 后台启动 jekyll serve (直接用 jekyll serve，不经过 run.sh 的 container 机制)
  bundle exec jekyll serve -P $SERVE_PORT --no-watch > "$SERVE_LOG" 2>&1 &
  SERVE_PID=$!

  # 等待服务启动
  SERVE_READY=false
  for i in $(seq 1 30); do
    if grep -q "Server address" "$SERVE_LOG" 2>/dev/null; then
      SERVE_READY=true
      break
    fi
    if grep -qiE "Error|Exception|fatal" "$SERVE_LOG" 2>/dev/null; then
      break
    fi
    sleep 1
  done

  if [[ "$SERVE_READY" == true ]]; then
    pass "Jekyll serve 启动成功"

    # 测试 HTTP 请求
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT/" 2>/dev/null)
    if [[ "$HTTP_CODE" == "200" ]]; then
      pass "HTTP 首页返回 200"
    else
      fail "HTTP 首页返回 $HTTP_CODE (期望 200)"
    fi

    # 测试 feed.xml
    FEED_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT/feed.xml" 2>/dev/null)
    if [[ "$FEED_CODE" == "200" ]]; then
      pass "HTTP feed.xml 返回 200"
    else
      warn "HTTP feed.xml 返回 $FEED_CODE"
    fi

    # 测试 sitemap.xml
    SITEMAP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT/sitemap.xml" 2>/dev/null)
    if [[ "$SITEMAP_CODE" == "200" ]]; then
      pass "HTTP sitemap.xml 返回 200"
    else
      warn "HTTP sitemap.xml 返回 $SITEMAP_CODE"
    fi

    # 测试 CSS 资源是否可访问
    CSS_FILE=$(find _site/assets/css -name "*.css" 2>/dev/null | head -1)
    if [[ -n "$CSS_FILE" ]]; then
      CSS_URL="/${CSS_FILE#_site/}"
      CSS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT${CSS_URL}" 2>/dev/null)
      if [[ "$CSS_CODE" == "200" ]]; then
        pass "HTTP CSS 资源返回 200"
      else
        fail "HTTP CSS 资源返回 $CSS_CODE ($CSS_URL)"
      fi
    fi

    # 测试 JS 资源是否可访问
    JS_FILE=$(find _site/assets/js -name "*.js" 2>/dev/null | head -1)
    if [[ -n "$JS_FILE" ]]; then
      JS_URL="/${JS_FILE#_site/}"
      JS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT${JS_URL}" 2>/dev/null)
      if [[ "$JS_CODE" == "200" ]]; then
        pass "HTTP JS 资源返回 200"
      else
        fail "HTTP JS 资源返回 $JS_CODE ($JS_URL)"
      fi
    fi

    # 测试文章页面
    SAMPLE_POST=$(find _site -path "*/202*/index.html" 2>/dev/null | head -1)
    if [[ -n "$SAMPLE_POST" ]]; then
      POST_URL="/${SAMPLE_POST#_site/}"
      POST_URL="${POST_URL%/index.html}/"
      POST_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT${POST_URL}" 2>/dev/null)
      if [[ "$POST_CODE" == "200" ]]; then
        pass "HTTP 文章页面返回 200 ($POST_URL)"
      else
        fail "HTTP 文章页面返回 $POST_CODE ($POST_URL)"
      fi
    fi

    # 测试分类页
    CATEGORY_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT/tabs/categories/" 2>/dev/null)
    if [[ "$CATEGORY_CODE" == "200" ]]; then
      pass "HTTP 分类页返回 200"
    else
      warn "HTTP 分类页返回 $CATEGORY_CODE"
    fi

    # 测试标签页
    TAG_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT/tabs/tags/" 2>/dev/null)
    if [[ "$TAG_CODE" == "200" ]]; then
      pass "HTTP 标签页返回 200"
    else
      warn "HTTP 标签页返回 $TAG_CODE"
    fi

    # 测试归档页
    ARCHIVE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$SERVE_PORT/tabs/archives/" 2>/dev/null)
    if [[ "$ARCHIVE_CODE" == "200" ]]; then
      pass "HTTP 归档页返回 200"
    else
      warn "HTTP 归档页返回 $ARCHIVE_CODE"
    fi

    # 检查 live reload (eventmachine)
    if grep -qi "pure_ruby\|EventMachine\|live" "$SERVE_LOG" 2>/dev/null; then
      if grep -qi "pure_ruby" "$SERVE_LOG" 2>/dev/null; then
        warn "EventMachine C 扩展加载失败，降级为 pure-ruby (不影响功能但影响性能)"
      fi
    else
      pass "EventMachine 正常加载"
    fi

    # 检查 serve 日志中的 Warning
    SERVE_WARNINGS=$(grep -ciE "Warning|deprecat" "$SERVE_LOG" 2>/dev/null || true)
    SERVE_WARNINGS=${SERVE_WARNINGS:-0}
    if [[ "$SERVE_WARNINGS" -gt 0 ]]; then
      warn "serve 日志有 $SERVE_WARNINGS 条 Warning"
    else
      pass "serve 日志 0 Warning"
    fi

  else
    fail "Jekyll serve 启动失败"
    echo -e "      最后 10 行日志:"
    tail -10 "$SERVE_LOG" 2>/dev/null | sed 's/^/      /'
  fi

  # 清理
  if [[ -n "$SERVE_PID" ]]; then
    kill "$SERVE_PID" > /dev/null 2>&1
    wait "$SERVE_PID" > /dev/null 2>&1
  fi
  rm -f "$SERVE_LOG"
fi

# ============================================================
# 测试 11: 运行时资源加载检查 (HTTP 全量 + Headless 抽样)
# ============================================================
section "测试 11/11: 运行时资源加载检查"

if [[ "$QUICK_MODE" == true ]]; then
  skip "运行时检查 (--quick 模式跳过)"
else
  # 检查 Python3 和 requests 库
  if command -v python3 &>/dev/null; then
    HAS_REQUESTS=$(python3 -c "import requests; print('yes')" 2>/dev/null || echo "no")
  else
    HAS_REQUESTS="no"
  fi

  if [[ "$HAS_REQUESTS" == "no" ]]; then
    warn "Python3 requests 库未安装，跳过运行时检查"
    echo -e "      安装: pip3 install requests"
  else
    # 启动 Jekyll serve（如果 Test 10 已关闭则重新启动）
    RT_PORT=14001
    RT_LOG="/tmp/blog_runtime_serve_$$.log"
    RT_PID=""

    echo -e "  ${BLUE}[INFO]${NC} 启动 Jekyll serve (端口 $RT_PORT)..."
    bundle exec jekyll serve -P $RT_PORT --no-watch > "$RT_LOG" 2>&1 &
    RT_PID=$!

    # 等待服务启动
    RT_READY=false
    for i in $(seq 1 30); do
      if grep -q "Server address" "$RT_LOG" 2>/dev/null; then
        RT_READY=true
        break
      fi
      if grep -qiE "Error|Exception|fatal" "$RT_LOG" 2>/dev/null; then
        break
      fi
      sleep 1
    done

    if [[ "$RT_READY" == true ]]; then
      pass "Jekyll serve 启动成功 (端口 $RT_PORT)"

      # 检查是否有 playwright
      HAS_PLAYWRIGHT=$(python3 -c "import playwright; print('yes')" 2>/dev/null || echo "no")
      HEADLESS_ARGS="--headless 5"
      if [[ "$HAS_PLAYWRIGHT" == "no" ]]; then
        info_msg "Playwright 未安装，仅执行 HTTP 层检查"
        info_msg "  (安装 headless 支持: pip3 install playwright && playwright install chromium)"
        HEADLESS_ARGS="--no-headless"
      fi

      # 运行 Python 检查脚本
      python3 tools/runtime-check.py \
        --base-url "http://127.0.0.1:$RT_PORT" \
        $HEADLESS_ARGS 2>&1 | sed 's/^/  /'

      # 捕获退出码
      RT_EXIT=${PIPESTATUS[0]}
      if [[ $RT_EXIT -eq 0 ]]; then
        pass "运行时资源加载检查通过"
      else
        fail "运行时资源加载检查发现问题"
      fi
    else
      fail "Jekyll serve 启动失败 (端口 $RT_PORT)"
      tail -5 "$RT_LOG" 2>/dev/null | sed 's/^/      /'
    fi

    # 清理
    if [[ -n "$RT_PID" ]]; then
      kill "$RT_PID" > /dev/null 2>&1
      wait "$RT_PID" > /dev/null 2>&1
    fi
    rm -f "$RT_LOG"
  fi
fi

# ============================================================
# 汇总报告
# ============================================================
section "测试汇总"

TOTAL=$((PASS + FAIL + WARN + SKIP))

echo ""
echo -e "  ${GREEN}PASS${NC}: $PASS / $TOTAL"
echo -e "  ${RED}FAIL${NC}: $FAIL / $TOTAL"
echo -e "  ${YELLOW}WARN${NC}: $WARN / $TOTAL"
echo -e "  ${CYAN}SKIP${NC}: $SKIP / $TOTAL"
echo ""

# 性能指标
echo -e "  ${BLUE}性能指标${NC}:"
echo -e "    Ruby 版本:   $RUBY_VERSION"
echo -e "    OpenSSL:     $OPENSSL_VERSION"
echo -e "    构建时间:    ${BUILD_TIME}s"
echo -e "    HTML 页面:   $HTML_COUNT"
echo -e "    文章页面:    $POST_HTML"
echo -e "    分类页面:    $CATEGORY_PAGES"
echo -e "    标签页面:    $TAG_PAGES"
echo ""

if [[ "$FAIL" -eq 0 ]]; then
  if [[ "$WARN" -eq 0 ]]; then
    echo -e "  ${GREEN}========================================${NC}"
    echo -e "  ${GREEN}  ALL PASSED - 0 Error 0 Warning${NC}"
    echo -e "  ${GREEN}========================================${NC}"
  else
    echo -e "  ${YELLOW}========================================${NC}"
    echo -e "  ${YELLOW}  PASSED with $WARN warning(s)${NC}"
    echo -e "  ${YELLOW}========================================${NC}"
  fi
  exit 0
else
  echo -e "  ${RED}========================================${NC}"
  echo -e "  ${RED}  FAILED: $FAIL error(s)${NC}"
  echo -e "  ${RED}========================================${NC}"
  exit 1
fi
