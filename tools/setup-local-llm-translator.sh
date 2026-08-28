#!/usr/bin/env bash
# macOS 一键装好本地免费翻译环境：Homebrew → Ollama → 启动服务 → 拉 Qwen2.5 → 验证
# 仅支持 macOS（Darwin），其他平台直接退出。
set -euo pipefail

echo "🚀 本地免费翻译环境一键安装（macOS）"

# 仅 macOS
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "❌ 本脚本仅支持 macOS，当前系统：$(uname -s)" >&2
  exit 1
fi

# 1. Homebrew
if ! command -v brew >/dev/null 2>&1; then
  echo "▶ 安装 Homebrew ..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "✓ Homebrew 已安装"
fi

# 2. Ollama
if ! command -v ollama >/dev/null 2>&1; then
  echo "▶ 安装 Ollama ..."
  brew install ollama
else
  echo "✓ Ollama 已安装"
fi

# 3. 启动服务（若未运行）
if ! curl -s -o /dev/null http://localhost:11434/api/tags; then
  echo "▶ 后台启动 Ollama 服务 ..."
  nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
  for i in $(seq 1 30); do
    if curl -s -o /dev/null http://localhost:11434/api/tags; then break; fi
    sleep 1
  done
else
  echo "✓ Ollama 服务已在运行"
fi

# 4. 拉模型
echo "▶ 拉取模型（7B 推荐 + 3B 轻量，首次需下载几 GB）..."
ollama pull qwen2.5:7b
ollama pull qwen2.5:3b

# 5. 验证
echo "▶ 验证 ..."
ollama list
if curl -s -o /dev/null http://localhost:11434/api/tags; then
  echo "✅ Ollama 服务在线，模型已就绪"
  echo "   命令行翻译：echo '你好' | ollama run qwen2.5:7b"
  echo "   或打开博客工具页 /tools/md-translator/（需 jekyll serve 本地地址）"
else
  echo "⚠️ 服务未起来，请手动 ollama serve 后重试" >&2
  exit 1
fi
