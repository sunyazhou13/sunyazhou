#!/bin/bash
#
# Using HTML-proofer to test site.
#
# Requirement: https://github.com/gjtorikian/html-proofer
#
# Usage: bash /path/to/test.sh [indicated path]
#
# v2.0
# https://github.com/cotes2020/jekyll-theme-chirpy
# © 2020 Cotes Chung
# MIT Licensed

DEST=_site
URL_IGNORE=cdn.jsdelivr.net

if [[ -n $1 && -d $1 ]]; then
  DEST=$1
fi

# 检测 html-proofer 主版本号，5.x 的 CLI 选项使用 kebab-case
HP_MAJOR=$(bundle exec ruby -e 'puts Gem::Specification.find_by_name("html-proofer").version.to_s.split(".").first' 2>/dev/null)

if [ "$HP_MAJOR" = "5" ]; then
  # html-proofer 5.x: --check-html 已移除，--ignore-empty-alt 和 --allow-hash-href 默认 true
  # --no-enforce-https: 跳过 http:// 链接检查（微博分享链接等）
  # 忽略 Polyglot 生成的 /tags/ /categories/ /en/404 链接（目标页面不存在）
  bundle exec htmlproofer "$DEST" \
    --disable-external \
    --no-enforce-https \
    --ignore-urls "$URL_IGNORE,/tags/,/categories/,/en/404\\.html"
else
  # html-proofer 4.x: snake_case 选项
  bundle exec htmlproofer "$DEST" \
    --disable-external \
    --check-html \
    --empty_alt_ignore \
    --allow_hash_href \
    --url_ignore "$URL_IGNORE"
fi
