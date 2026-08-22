#!/usr/bin/env bash
# newpost.sh - 创建中/英/双语博客文章（支持正文模板）
#
# 用法:
#   bash tools/newpost.sh "My Post Title"          # 默认：双语（_posts/en/ 不存在时只建中文）
#   bash tools/newpost.sh zh "My Post Title"       # 只创建中文文章 (_posts/)
#   bash tools/newpost.sh en "My Post Title"       # 只创建英文文章 (_posts/en/)
#   bash tools/newpost.sh both "My Post Title"     # 强制创建双语：中文 + 英文副本 (_posts/en/)
#
# 正文模板（类似 hexo 的 scaffolds）:
#   中文模板: tools/scaffolds/post.md       （前言等通用文案）
#   英文模板: tools/scaffolds/post.en.md
#   新建文章时模板内容会自动追加到 front matter 之后，修改模板即对所有新文章生效。
#   模板文件不存在时跳过注入。
#
# 说明:
#   - 无 lang 参数时默认双语：检测 _posts/en/ 目录，存在则同时建英文版，
#     不存在则只建中文版。
#   - jekyll-compose 0.12.0 的 post 命令路径写死为 _posts/，不支持语言子目录，
#     本脚本创建后自动移动/复制到 _posts/en/。
#   - polyglot 开启了 lang_from_path: true，英文文章放入 _posts/en/ 即被识别为
#     en 语言，无需在 front matter 手写 lang。
#   - 中英文版本保持相同文件名（相同 slug + 日期），polyglot 才会把它们识别为
#     同一篇文章的互译，生成 hreflang 和语言切换链接。
#   - 标题请用英文（jekyll-compose 的 slug 化会丢弃非 ASCII 字符，中文标题会
#     生成空 slug），创建后再把 front matter 里的 title 改成中文。

set -euo pipefail

usage() {
  grep '^#' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

[[ $# -ge 1 ]] || usage

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EN_DIR="$ROOT/_posts/en"

# 解析参数：第一个参数若是 zh/en/both 且后面还有标题，则按显式模式；否则视为标题
if [[ "$1" == zh || "$1" == en || "$1" == both ]] && [[ $# -ge 2 ]]; then
  LANG_ARG="$1"
  TITLE="$2"
else
  TITLE="$1"
  # 默认模式：_posts/en/ 存在则双语，否则只建中文
  if [[ -d "$EN_DIR" ]]; then
    LANG_ARG="both"
  else
    LANG_ARG="zh"
  fi
fi

create_post() {
  local out
  # 输出形如 "New post created at \e[36m_posts/xxx.md\e[0m "，需去掉前缀和 ANSI 颜色码
  out=$(cd "$ROOT" && bundle exec jekyll post "$TITLE" 2>&1 | grep "New post created at" | sed -e $'s/\x1b\\[[0-9;]*m//g' -e 's/^New post created at //' -e 's/[[:space:]]*$//')
  echo "$out"
}

# 返回指定语言的模板路径，不存在则输出空
scaffold_for() {
  local lang="$1" s
  if [[ "$lang" == "en" ]]; then
    s="$ROOT/tools/scaffolds/post.en.md"
  else
    s="$ROOT/tools/scaffolds/post.md"
  fi
  [[ -f "$s" ]] && echo "$s" || true
}

# 将模板内容追加到文章正文（jekyll-compose 生成的文件以 "---\n" 结尾，直接追加即可）
apply_scaffold() {
  local file="$1" lang="$2" s
  s=$(scaffold_for "$lang")
  [[ -z "$s" ]] && return 0
  printf '\n' >> "$file"
  cat "$s" >> "$file"
}

# 将 jekyll-compose 生成的块状数组 front matter 归一化为行内数组风格，
# 与全站既有文章保持一致，也避免块状 categories 触发 create_pages.sh 的
# 历史缺陷（"- iOS" 行被当成分类名生成 --ios.html 非法 YAML 页面）
normalize_front_matter() {
  local file="$1"
  ruby -e '
    path = ARGV[0]
    content = File.read(path)
    if content =~ /\A---\n(.*?)\n---\n/m
      fm = Regexp.last_match(1)
      body = Regexp.last_match.post_match
      %w[categories tags].each do |key|
        fm = fm.gsub(/^#{key}:\n((?:- .*\n)+)/) do
          items = Regexp.last_match(1).scan(/^- (.*)$/).flatten.map(&:strip)
          "#{key}: [#{items.join(", ")}]\n"
        end
      end
      File.write(path, "---\n#{fm}\n---\n#{body}")
    end
  ' "$file"
}

FILE=$(create_post)
if [[ -z "$FILE" || ! -f "$ROOT/$FILE" ]]; then
  echo "错误: 文章创建失败"
  exit 1
fi

normalize_front_matter "$ROOT/$FILE"

case "$LANG_ARG" in
  zh)
    apply_scaffold "$ROOT/$FILE" zh
    echo "中文文章已创建: $FILE"
    ;;
  en)
    [[ -d "$EN_DIR" ]] || mkdir -p "$EN_DIR"
    mv "$ROOT/$FILE" "$EN_DIR/"
    apply_scaffold "$EN_DIR/$(basename "$FILE")" en
    echo "英文文章已创建: _posts/en/$(basename "$FILE")"
    ;;
  both)
    [[ -d "$EN_DIR" ]] || mkdir -p "$EN_DIR"
    # 先复制干净的英文版（未注入中文模板），再分别注入各自模板
    cp "$ROOT/$FILE" "$EN_DIR/$(basename "$FILE")"
    apply_scaffold "$ROOT/$FILE" zh
    apply_scaffold "$EN_DIR/$(basename "$FILE")" en
    echo "双语文章已创建:"
    echo "  中文: $FILE"
    echo "  英文: _posts/en/$(basename "$FILE")"
    echo "请分别编辑两份文件，英文版记得把 title 改成英文。"
    ;;
esac
