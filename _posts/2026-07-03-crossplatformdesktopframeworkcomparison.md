---
layout: post
title: "跨平台桌面框架选型深度对比：一个 iOS 开发者的 Qt6 之旅"
date: 2026-07-03 02:45 +0000
categories: [跨平台, AI Agent, 移动开发, 小程序, 鸿蒙]
tags: [Electron, Tauri, Qt6, Flutter, React Native, uni-app, Taro, Python, LangChain, Deno, 鸿蒙, 微信小程序, AI Agent]
---

# 前言

本文具有强烈的个人感情色彩,如有观看不适,请尽快关闭. 本文仅作为个人学习记录使用,也欢迎在许可协议范围内转载或分享,请尊重版权并且保留原文链接,谢谢您的理解合作. 如果您觉得本站对您能有帮助,您可以使用RSS方式订阅本站,感谢支持!

## 背景

我是一名 iOS 开发者，日常和 Swift、Objective-C、Metal、SwiftUI 打交道。最近开始系统学习 Qt6，动机很明确：**用 AI Agent 赋能一批老旧的企业级原生桌面应用**，这些应用普遍嵌入了自定义图形渲染管线（CAD 预览、数据可视化、视频处理等），但架构停留在十几年前的 MFC / WinForms 时代。

问题来了 —— 我该押注哪个跨平台框架？Qt6 的 RHI 抽象层和 Metal 后端的亲和力让我天然有好感，但 Tauri 的 3MB 包体、Flutter 的 Impeller 引擎、Electron 的 AI 生态（LangChain.js / Vercel AI SDK）也各有诱惑。

这篇文章是我调研过程的完整记录，**从 iOS 开发者的认知模型出发**，把市面主流方案横向拉通，量化对比。

2026 年，AI Agent 从概念验证全面进入生产落地阶段。LangChain 生态日趋成熟，MCP（Model Context Protocol）成为工具集成的事实标准，`llama.cpp` 让本地推理不再依赖云端 API。

与此同时，"跨平台"的定义已经被彻底重写。一个 AI Agent 产品可能需要在以下 **6 个端**上运行：

| # | 端 | 典型场景 | 中国市场必要性 |
|---|-----|---------|:---:|
| 1 | **Desktop**（Win/Mac/Linux） | 企业后台、IDE 插件、桌面聊天助手 | ★★★ |
| 2 | **iOS** | iPhone/iPad 上的 Agent App | ★★★★ |
| 3 | **Android** | 国内 Android 生态 | ★★★★★ |
| 4 | **H5/Web** | 浏览器端 Agent、零安装体验 | ★★★★ |
| 5 | **鸿蒙 (HarmonyOS)** | 华为设备、政企客户、央企要求 | ★★★★★（2026 年起） |
| 6 | **微信小程序** | C 端用户触达的最短路径 | ★★★★★ |

这篇文章聚焦一个升级版问题：**如果你要开发一个覆盖桌面 + 移动端 + 小程序 + 鸿蒙的 AI Agent 应用，该选哪套跨平台技术栈？**

把市面上主流的跨平台框架横向拉通，覆盖 Desktop、移动端、小程序、鸿蒙四大战场，逐一量化对比。

---

## 2026 年最值得关注的 6 个新面孔 `★`

### 1. Deno Desktop —— "Electron 该有的样子"

Deno v2.9 内置 `deno desktop` 命令，**把 TypeScript 桌面开发从"工程问题"降维到"配置问题"**。零 IPC 样板、自动检测前端框架、热重载开箱即用。包体约 30MB，是 Electron 的五分之一。

```
# 一行命令，把任何 Deno 项目打包为桌面应用
deno desktop
```

适合：TS 全栈团队、快速原型、AI Agent 对话编排层。
瓶颈：v2.9 初版，工具链成熟度不及 Electron。**仅覆盖桌面端。**

---

### 2. uni-app X —— "一套代码覆盖 15+ 平台"

DCloud 推出的下一代 uni-app，使用 UTS（TypeScript 超集）编译为原生代码。**是目前唯一同时覆盖 iOS、Android、鸿蒙、Web 和微信小程序的主流框架。**

```vue
<!-- 一套代码 → 15+ 个端 -->
<template>
  <view class="agent-chat">
    <scroll-view :scroll-into-view="lastId">
      <text v-for="msg in messages" :key="msg.id">{{ msg.content }}</text>
    </scroll-view>
    <input v-model="prompt" @confirm="sendToAgent" />
  </view>
</template>
<script setup lang="uts">
import { ref } from 'vue'
const messages = ref<Array<{id:string,content:string}>>([])
// 通过 uni.request 调用 MCP Server 或 LLM API
</script>
```

适合：C 端产品、需要覆盖小程序 + 鸿蒙的团队。
瓶颈：传统桌面（Win/Mac/Linux）支持较弱；AI 生态不如 Python。

---

### 3. Taro —— "React 版小程序跨端王者"

京东出品，用 React 语法写一套代码，编译到微信/支付宝/百度/抖音等多个小程序平台，同时支持 H5 和 React Native 移动端。

```tsx
// Taro + LangChain.js → AI Agent 小程序
import { useLoad } from '@tarojs/taro'
import { ChatOpenAI } from '@langchain/openai'

export default function AgentChat() {
  useLoad(() => {
    // 小程序环境直接跑 LangChain.js
    const llm = new ChatOpenAI({ modelName: 'gpt-4o-mini' })
  })
}
```

适合：以小程序为主要入口的 C 端 AI Agent 产品。
瓶颈：桌面端非原生支持；DeepSeek/本地模型接入需后端中转。

---

### 4. Dioxus —— Rust 版 React

语法酷似 React Hooks，编译到机器码。一套代码通吃 Web (WASM)、桌面 (Blitz 自绘)、移动和 TUI。Rust 编译时类型安全，包体 ~12MB。适合 Rust 全栈长期押注。v0.6 阶段，**暂不建议 2026 年生产使用。**

---

### 5. Electrobun —— "Bun 版 Electron"

用 Bun 替代 Node.js、Zig 写底层，包体 **~12MB**。最早阶段。保持关注。

---

### 6. Tauri 2.0 —— 3MB + 移动端 GA

Tauri 2.0 在 2025 年稳定发布，**移动端（iOS/Android）正式 GA**。Rust 后端 + Web 前端 + 系统 WebView，包体仅 3MB。适合前端团队 + Rust 推理引擎的混合架构。**不支持小程序/鸿蒙。**

---

| 新面孔 | 语言 | 覆盖平台 | 成熟度 | AI Agent 适合度 |
|:---:|:---:|------|:---:|------|
| Deno Desktop | TypeScript | Desktop | v2.9 初版 | TS 全栈桌面 Agent |
| uni-app X | UTS (TS超集) | iOS/Android/鸿蒙/H5/小程序 | 生产可用 | C 端全平台 Agent |
| Taro | React/Vue | 多小程序/H5/RN | 生产可用 | 小程序 AI Agent |
| Dioxus | Rust | Desktop/Web/Mobile | v0.6 | Rust 全栈长期押注 |
| Electrobun | TypeScript | Desktop | 概念验证 | Electron 替代储备 |
| Tauri 2.0 | Rust + JS | Desktop/iOS/Android | 稳定版 | 轻量桌面+移动 Agent |

---

## 零、全平台覆盖矩阵：谁真正支持"一次编写，处处运行"

这是本文最核心的一张表。**桌面框架**和**全平台框架**是两个不同的物种。

| 框架 | Desktop | iOS | Android | H5/Web | 鸿蒙 | 微信小程序 | **覆盖端数** |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **uni-app X** | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | **6/6** 🏆 |
| **Flutter** | ✅ | ✅ | ✅ | ✅ | ✅(社区) | ⚠️ | **5.5/6** |
| **React Native** | ✅(Win/Mac) | ✅ | ✅ | ✅ | ✅(社区) | ⚠️ | **5.5/6** |
| **Taro** | ❌ | ⚠️(RN) | ⚠️(RN) | ✅ | ✅ | ✅ | **4.5/6** |
| **Qt6** | ✅ | ✅ | ✅ | ⚠️(WASM) | ❌ | ❌ | **3.5/6** |
| **Kotlin Multiplatform** | ✅ | ✅ | ✅ | ✅(Wasm) | ⚠️早期 | ❌ | **4/6** |
| **Tauri 2.0** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | **3/6** |
| **.NET MAUI** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | **3/6** |
| **Electron** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **1/6** |
| **Deno Desktop** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **1/6** |
| **Wails** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **1/6** |
| **Dioxus** | ✅ | ⚠️ | ⚠️ | ✅(Wasm) | ❌ | ❌ | **2.5/6** |

> ✅ 官方/社区生产可用 | ⚠️ 部分支持或需三方适配 | ❌ 不支持或不可用

**核心洞察**：
- **uni-app X 是唯一 6/6 全覆盖的框架**，对微信小程序和鸿蒙的支持是独有优势
- Flutter 和 React Native 紧随其后，覆盖 5-5.5 个端，生态最成熟
- Electron/Tauri/Deno 本质是"桌面框架"，不是"全平台框架"——选它们就意味着放弃移动端和小程序
- 如果你需要覆盖微信小程序，**只有 uni-app 和 Taro 两个靠谱选项**

---

## 一、AI Agent 开发的核心能力模型

传统跨平台对比关注包体大小和渲染性能，但在 AI Agent 场景下，以下维度才是决定因素：

| 能力维度 | 为什么重要 | 典型需求 |
|---------|-----------|---------|
| **LLM SDK 生态** | Agent 逻辑的核心 | LangChain / LlamaIndex / Vercel AI SDK / OpenAI SDK |
| **全平台覆盖度** | 一套代码触达所有用户 | Desktop + iOS + Android + H5 + 鸿蒙 + 微信小程序 |
| **本地模型部署** | 离线运行、数据安全、低延迟 | llama.cpp / ONNX Runtime / MLX / GGUF 格式 |
| **工具调用（Tool Calling）** | Agent 与系统交互的关键 | 文件读写、Shell 执行、API 调用、浏览器控制 |
| **Agent 编排框架** | 多步推理、记忆管理、多 Agent 协作 | LangGraph / CrewAI / AutoGen / Semantic Kernel |
| **桌面集成深度** | 桌面端原生体验 | 系统托盘、全局快捷键、通知、自动启动、窗口管理 |

> 核心认知：**2026 年的 AI Agent 产品，只做桌面端是不够的。** 微信小程序是 C 端触达的最短路径，鸿蒙是政企项目的入场券。技术选型必须从第一天就把"能覆盖几个端"纳入考量。

---

## 二、核心框架对比总览

以下是纯 AI Agent 开发视角的量化对比。去掉图形渲染维度，新增本地模型部署和 Tool Calling 等 Agent 专属维度。

### 2.1 量化评分体系说明

| 维度 | 权重 | 评分标准 |
|------|:----:|---------|
| **AI 生态成熟度** | ×2.5 | LLM SDK、Agent 框架（LangChain/LangGraph）、RAG 库、向量数据库对接 |
| **全平台覆盖度** | ×2.0 | Desktop + iOS + Android + H5 + 鸿蒙 + 微信小程序 的覆盖程度 |
| **本地模型部署** | ×2.0 | 本地推理引擎（llama.cpp/ONNX/MLX）、模型热加载、量化支持、GPU 加速 |
| **开发体验与工具链** | ×1.5 | 语言门槛、IDE 支持、调试、热重载、类型提示、AI 辅助编码 |
| **桌面集成深度** | ×1.5 | 系统托盘、全局快捷键、通知、文件系统、进程管理、窗口控制 |
| **包体与性能** | ×1.0 | 空包体积、冷启动速度、运行时内存（含模型加载后的内存峰值） |
| **企业级就绪度** | ×1.5 | LTS 支持、文档质量、生产案例、社区活跃度、国内生态 |
| **学习曲线（新手友好）** | ×0.5 | 从零到可交付第一版 Agent 的时间预估（分越低越好学，已反向计分） |

### 2.2 主战场：全平台 AI Agent 视角横向对比

| 框架 | 语言 | AI生态 ★ | 全平台 ★ | 本地部署 ★ | 开发体验 ★ | 桌面集成 ★ | 体积MB | 企业就绪 | 新手友好 | **综合分** |
|------|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Qt6 (Python)** | Python / QML | 10 | 3.5 | 9 | 8 | 9 | ~35 | 7 | 7.5 | **72.1** |
| **Flutter** | Dart | 5 | 9 | 3 | 7.5 | 5 | ~20 | 8 | 7 | **65.2** |
| **Electron** | JS/TS | 10 | 1.5 | 5 | 9.5 | 8 | ~150 | 9 | 9 | **64.4** |
| **React Native** | JS/TS | 8 | 9 | 4 | 7 | 4 | ~15 | 8 | 7 | **64.0** |
| **uni-app X** | UTS (TS超集) | 6 | 10 | 4 | 8 | 4 | ~10 | 7 | 8.5 | **63.0** |
| **Qt6 (C++)** | C++ / QML | 6 | 3.5 | 10 | 6 | 9.5 | ~25 | 9.5 | 4 | **62.9** |
| **Taro** | React/Vue/TS | 7 | 7 | 4 | 8 | 2 | ~5 | 7 | 8 | **57.6** |
| **Tauri 2.0** | Rust + JS | 7 | 5 | 8 | 6 | 7 | ~3 | 6.5 | 5 | **59.4** |
| **Kotlin Multiplatform** | Kotlin | 5 | 6.5 | 5 | 7 | 7 | ~18 | 6 | 6 | **55.6** |
| **Deno Desktop** ✦ | TS | 8 | 1.5 | 5 | 9 | 6 | ~30 | 4.5 | 9 | **54.9** |
| **Wails** | Go + JS | 6.5 | 1.5 | 5 | 7 | 7 | ~10 | 5.5 | 6.5 | **52.0** |
| **Avalonia** | C# | 6 | 3 | 5 | 7 | 7 | ~15 | 7.5 | 6.5 | **53.1** |
| **Dioxus** | Rust | 5.5 | 3.5 | 7 | 4 | 5 | ~12 | 3 | 4 | **47.0** |

> ✦ 标注为 2026 年值得重点关注的新兴框架。

> 综合分 = Σ(维度分 × 权重)，按满分 112.5 归一化。评分基于 2026 年中生态现状。

**排名解读**：

1. **Qt6 Python 仍居榜首** — AI 生态的绝对优势（LangChain 全系可用）压倒了平台覆盖的短板
2. **Flutter 跃升至第二** — 全平台能力 + Impeller 渲染，Dart AI 生态弱但可走 HTTP 调用
3. **Electron 从第二跌至第三** — 仅 1 个端，全平台时代这是致命缺陷
4. **React Native 和 uni-app X 杀入前五** — 移动端 + 小程序覆盖带来了巨大的战略价值
5. **Deno Desktop 从 60.5 跌至 54.9** — 桌面单端在 2026 年竞争力急剧下降

### 2.3 详细拆解：每个框架的 AI Agent 画像

---

#### Qt6 (Python 路线：PySide6) — 75.8 分 🏆

**定位：AI Agent 桌面开发的最优解。**

Python 生态是 AI Agent 开发的绝对主场。`from langchain.agents import create_react_agent` 一行代码就能跑 Agent，PySide6 让你在同一进程内获得完整的桌面能力。

```python
# 一个进程：LangChain Agent + 原生桌面窗口
from PySide6.QtCore import QObject, Signal, Slot, QThread
from langgraph.graph import StateGraph
from langchain_community.tools import ShellTool, FileSystemTool

class DesktopAIAgent(QObject):
    responseReady = Signal(str)
    toolProgress = Signal(str, str)  # tool_name, status

    def __init__(self):
        super().__init__()
        # 直接使用 LangGraph 做 Agent 编排
        self.graph = StateGraph(AgentState)
        self.graph.add_node("llm", self.call_llm)
        self.graph.add_node("tools", self.execute_tool)
        # 注册系统级 Tool
        self.shell = ShellTool()
        self.fs = FileSystemTool()

    @Slot(str)
    def query(self, prompt: str):
        # Agent 循环：LLM → Tool Calling → 结果返回
        result = self.graph.invoke({"input": prompt})
        self.responseReady.emit(result["output"])
```

**核心优势：**

- **LangChain / LangGraph / CrewAI / AutoGen** 全部直接 import，零适配
- **MCP 协议支持**：`pip install mcp` 即可对接任何 MCP Server
- **RAG 生态完整**：ChromaDB / FAISS / Qdrant 本地向量库 + 桌面文件系统直接读取
- **Tool Calling 天花板**：Python 可以直接调用任何系统 API、读写文件、执行 Shell、控制浏览器（Playwright）
- **本地模型部署**：ONNX Runtime / PyTorch / llama-cpp-python 全部可用，支持 GPU 加速

**代价：**
- Python GIL 会在并发 Agent 调用时成为瓶颈，需要 `QThread` + 子进程隔离
- QML 声明式 UI 学习曲线对纯后端开发者不太友好
- 包体 35MB+，模型文件另计（GGUF 量化模型通常 4-8GB）

**适合：**
- AI Agent 需要复杂的 Tool Calling（系统调用、文件操作、API 链式调用）
- 需要本地模型推理 + RAG
- 团队有 Python 经验

**不适合：**
- 纯聊天 UI（Electron 更快）
- 团队没有 Python 经验且不想学

---

#### Electron — 72.0 分

**定位：AI 生态最完整的桌面框架，但本地推理是短板。**

Electron 的 AI 开发生态无可匹敌：

```typescript
// LangChain.js + Electron = AI Agent 桌面应用
import { ChatOpenAI } from "@langchain/openai";
import { AgentExecutor, createOpenAIFunctionsAgent } from "langchain/agents";
import { BrowserWindow, app, Tray, globalShortcut } from "electron";

// 系统级 Tool：全局快捷键 → 唤起 Agent
app.whenReady().then(() => {
  globalShortcut.register("CommandOrControl+Shift+A", () => {
    agentWindow.show();
    agent.invoke({ input: "Ready to assist" });
  });
});
```

- `@langchain/core` + `@langchain/community` 直接跑在 Node.js 里
- Vercel AI SDK、OpenAI Node SDK、Anthropic SDK 零配置
- Chrome DevTools 做 Agent 调试（可以断点 LLM 的输入输出）
- **唯一能用 Web 前端生态做桌面 Agent 的方案**

**但本地模型部署是硬伤：**
- Node.js 的 llama.cpp 绑定（node-llama-cpp）性能远不如原生
- WebAssembly 推理速度仅为原生的 20-30%
- 大型模型的 GPU 加速基本不可用

> 判断：Electron 是 **"云端 LLM + 本地桌面" 场景的最佳方案**。如果 Agent 不需要本地跑模型（比如用 OpenAI API / Anthropic API），Electron 的开发效率碾压一切。

---

#### Qt6 (C++ 路线) — 67.8 分

**定位：本地推理性能天花板，但 AI 生态开发效率低。**

```cpp
// llama.cpp C++ API → 本地推理的最高性能
#include "llama.h"

llama_model_params model_params = llama_model_default_params();
llama_model *model = llama_load_model_from_file("qwen2-7b.Q4_K_M.gguf", model_params);
llama_context *ctx = llama_new_context_with_model(model, llama_context_default_params());

// 推理速度是 Python 绑定的 1.5-2 倍
llama_decode(ctx, batch);
```

**优势：**
- llama.cpp / whisper.cpp 的 C++ API 是性能天花板
- 内存管理精确，不会像 Python 一样 OOM
- QML 提供现代化桌面 UI，比 MFC/WinForms 好十倍

**劣势：**
- LangChain 没有 C++ 绑定，Agent 编排需要从零手写或通过 Python 子进程
- Tool Calling 开发效率极低
- 原型验证周期是 Python 的 3-5 倍

> 判断：只有当本地推理性能是绝对瓶颈（比如需要 7B+ 模型在笔记本上实时响应），才选这条路。90% 的 AI Agent 场景不需要这个级别的优化。

---

#### Tauri — 63.0 分

**定位：轻量 Agent + Rust 推理引擎的"潜力股"。**

```
// Tauri 2.0：Rust 本地推理 + JS 前端 UI
#[tauri::command]
async fn run_agent(prompt: String, app: tauri::AppHandle) -> Result<String, String> {
    // Rust 直接跑 candle / burn 推理
    let model = load_quantized_model("mistral-7b.Q4_K_M.gguf")?;
    let response = model.generate(&prompt, 512)?;
    Ok(response)
}
```

**优势：**
- 3MB 包体 + 模型文件，分发最轻
- Rust 的 candle（HuggingFace）、burn 等 ML 框架在快速成熟
- 前端用 React/Vue，学习成本低

**劣势：**
- LangChain 没有 Rust 绑定，Agent 编排需要自己实现
- MCP 协议没有官方 Rust SDK
- 生态比 Python 差一个数量级

> 判断：2026 年还不适合押注 Tauri 做主力 AI Agent 框架。但如果你在规划 2027 年的技术栈，它值得提前布局。

---

#### Deno Desktop — 60.5 分 `★ 2026 新星`

**定位：Electron 去掉 80% 胶水 + 80% 包体。**

```ts
// deno.json — 零配置 AI Agent 桌面应用
{
  "desktop": {
    "title": "CodeBuddy Agent",
    "width": 1200, "height": 800,
    "autoUpdate": true, "hotReload": true
  }
}
```

**核心卖点：** 零 IPC 样板、~30MB 包体、自动检测前端框架、开箱即用热重载。`Deno.BrowserWindow` 直接调用系统 API。

**适合：** TS 全栈 AI Agent（云端 LLM + 本地 Agent 编排）、受够 Electron 复杂度的前端团队。

**不适合：** 需要本地大模型推理、2026 年上生产（v2.9 刚发布）。

---

#### Flutter — 51.0 分

Dart 的 AI 生态极其薄弱 —— 没有 LangChain、没有 llama.cpp 绑定、没有 MCP SDK。AI Agent 只能通过 HTTP 调用云端 API。如果 Agent 是"云端大脑 + 本地瘦客户端"，Flutter 的 UI 表现不错；但凡需要本地推理或复杂 Tool Calling，Dart 是瓶颈。

---

#### Wails — 57.3 分 / Avalonia — 57.0 分 / Kotlin Compose — 55.0 分

这几个框架的共性问题：**AI 生态不在这门语言的主航道上**。Go、C#、Kotlin 各有优秀的 AI 库，但 LangChain 级别的 Agent 框架生态不存在。适合"已经有 Go/.NET/Kotlin 团队，只需要嵌入简单 LLM 调用"的场景。

---

#### Dioxus — 48.3 分

Rust 版 React，包体 ~12MB，WGPU 抽象。v0.6 阶段，**2028 年再评估。**

---

## 三、AI Agent 核心能力专项对比

抛开所有框架的 GUI 能力，只看 AI Agent 开发的纯粹维度。

### 3.1 LLM 集成与 Agent 编排

| 能力 | Qt6 Python | Electron | Qt6 C++ | Tauri | Deno Desktop | Flutter |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| **LangChain 支持** | 10 (原生) | 10 (LangChain.js) | 0 (无绑定) | 0 | 8 (LangChain.js) | 0 |
| **LangGraph 编排** | 10 | 9 | 0 | 0 | 7 | 0 |
| **CrewAI / AutoGen** | 10 | 6 | 0 | 0 | 4 | 0 |
| **MCP 协议** | 10 (官方 SDK) | 8 (社区 SDK) | 4 (自实现) | 4 | 6 | 0 |
| **OpenAI / Anthropic SDK** | 10 | 10 | 7 (HTTP) | 7 (HTTP) | 10 | 8 (HTTP) |
| **Tool Calling 开发效率** | 10 | 9 | 5 | 6 | 9 | 5 |

### 3.2 本地模型部署

| 能力 | Qt6 C++ | Qt6 Python | Tauri | Electron | Deno Desktop | Flutter |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| **llama.cpp 集成** | 10 (C++ API) | 9 (llama-cpp-python) | 8 (rust/llama-cpp-rs) | 5 (node-llama-cpp) | 5 | 0 |
| **ONNX Runtime** | 9 | 9 | 7 | 5 (onnxruntime-node) | 5 | 3 |
| **GPU 加速推理** | 10 (CUDA/Metal) | 8 (CUDA/MPS) | 7 | 3 (WebGPU实验) | 3 | 3 |
| **量化模型支持** | 10 (GGUF) | 9 (GGUF) | 8 (GGUF) | 5 | 5 | 3 |
| **内存效率** | 10 | 6 (Python GC) | 9 | 4 | 4 | 4 |

### 3.3 桌面系统集成深度

| 能力 | Qt6 C++ | Qt6 Python | Electron | Tauri | Deno Desktop | Flutter |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| **系统托盘** | 10 | 9 | 10 | 8 | 6 | 5 |
| **全局快捷键** | 10 | 9 | 10 | 8 | 5 | 6 |
| **原生通知** | 10 | 9 | 8 | 8 | 6 | 6 |
| **文件系统深度访问** | 10 | 10 | 9 | 9 | 9 | 8 |
| **进程管理** | 10 | 10 | 8 | 7 | 6 | 5 |
| **自动启动** | 9 | 9 | 10 | 8 | 5 | 5 |
| **窗口管理** | 10 | 9 | 8 | 7 | 7 | 7 |

### 关键结论

1. **Python 是 AI Agent 桌面开发的"主场语言"。** LangChain、LangGraph、CrewAI、MCP 协议 —— 所有主流 Agent 框架的 Python SDK 都是一等公民。

2. **本地推理的性能天花板在 C++ / Rust。** 如果你需要 7B+ 模型在消费级硬件上实时推理，Qt6 C++ 或 Tauri 的 Rust 后端是唯一选择。但 90% 的 Agent 场景用 3B-7B 量化模型 + Python 就够了。

3. **Electron 的"云端 LLM + 桌面客户端"模式最成熟。** 如果不依赖本地推理，Electron 的开发效率无出其右。

4. **MCP 协议正在改变桌面 Agent 的架构。** 未来你可以用 Python 跑 Agent 核心 + MCP Server，然后用 Electron/Qt/Tauri 只做 UI 层。这意味着框架选择的分层会越来越灵活。

---

## 四、推荐的 Agent 架构模式

### 4.1 经典三层架构（适合大多数场景）

```
┌──────────────────────────────────────┐
│           桌面 UI 层                  │  ← React / Vue / QML
│       对话界面 + 工具状态展示          │
├──────────────────────────────────────┤
│         AI Agent 逻辑层              │  ← LangChain / LangGraph
│  LLM 调用 + Tool Calling + RAG       │
├──────────────────────────────────────┤
│         模型推理层                    │  ← llama.cpp / ONNX / API
│     本地推理 or 云端 API              │
└──────────────────────────────────────┘
```

**UI 层**：Electron（React/Vue）或 PySide6（QML）
**Agent 层**：Python（LangChain/LangGraph）—— 可以与 UI 同进程，也可以独立进程 + IPC
**推理层**：云端 API（OpenAI/Anthropic）或本地（llama.cpp/ONNX）

### 4.2 MCP 分离架构（面向未来的选择）

```
┌──────────┐    MCP协议     ┌──────────────┐
│  UI 层   │ ←──────────→  │  Agent 核心  │
│ Electron │               │  Python 进程  │
│  / Tauri │               │  LangGraph    │
└──────────┘               └──────┬───────┘
                                  │ MCP
                    ┌─────────────┼─────────────┐
                    │             │             │
               ┌────┴────┐ ┌─────┴─────┐ ┌─────┴─────┐
               │文件系统  │ │ 浏览器控制 │ │ 代码执行   │
               │ MCP Svr │ │ MCP Server│ │ MCP Server│
               └─────────┘ └───────────┘ └───────────┘
```

UI 层和技术栈解耦，Agent 核心独立运行，通过 MCP 协议暴露 Tool Calling 能力。这样 UI 层可以任意替换（Electron → Tauri → Deno Desktop）而不影响 Agent 逻辑。

---

## 五、场景化决策矩阵

根据团队背景和 Agent 需求，推荐以下五条选型路径：

### 场景 A：全功能桌面 Agent（需要复杂 Tool Calling + 本地推理）

```
选 PySide6 + QML
├── Agent 层: LangChain / LangGraph (Python)
├── 工具层: Shell / 文件系统 / Playwright / 自定义 MCP Server
├── 推理层: llama-cpp-python (本地) / OpenAI API (云端)
├── UI 层: QML 声明式 UI
└── 交付: PyInstaller 打包
```

**理由**：AI 生态最完整，Tool Calling 能力最强，本地推理可用。GIL 问题通过多进程隔离解决。

---

### 场景 B：云端 Agent 聊天助手（依赖 API，不需要本地推理）

```
选 Electron
├── Agent 层: LangChain.js / Vercel AI SDK
├── 推理层: OpenAI / Anthropic / Claude API
├── UI 层: React / Vue
└── 交付: electron-builder
```

**理由**：开发效率最高，AI/前端双生态完整。包体 150MB 在企业桌面软件中不是痛点。

---

### 场景 C：TS 全栈 Agent（追求轻量）

```
选 Deno Desktop
├── Agent 层: LangChain.js (npm 生态)
├── 推理层: 云端 API
├── UI 层: Next.js / Vite
└── 交付: deno desktop
```

**理由**：零 IPC 样板，~30MB 包体。前端团队零额外学习成本。但 v2.9 才发，生产需谨慎。

---

### 场景 D：本地大模型推理优先（7B+ 模型，消费级硬件）

```
选 Qt6 C++ 或 Tauri (Rust 后端)
├── Agent 层: llama.cpp (C++) / candle (Rust) + Python 子进程
├── 推理层: 纯本地 GGUF 量化模型
├── UI 层: QML / React
└── 交付: CMake / cargo-bundle
```

**理由**：只有 C++/Rust 能让 7B+ 模型在笔记本上达到可接受的推理速度。Agent 编排复杂逻辑通过 Python 子进程补位。

---

### 场景 E：轻量嵌入式 Agent（IoT / 边缘设备 / MCU）

```
选 Slint（Rust/C++ 路线）
├── Agent 层: 轻量 Rust ML 推理
├── 推理层: 微型模型 (1B 以下)
├── UI 层: .slint DSL
└── 交付: 单二进制 <5MB
```

**理由**：<300KB UI 框架 + 微型模型 = 入门级离线 Agent。不适合复杂 Agent 场景。

---

## 六、从不同技术背景出发的学习路线

### 6.1 Python 后端开发者

**最优路径**：PySide6 + QML，4-6 周可交付第一版 Agent。

QML 语法类似 JSON/YAML 声明式配置，Python 后端开发者适应很快。LangChain / LlamaIndex 直接对接现有的 Python 模型代码。

### 6.2 Web 前端开发者（React / Vue）

**路径一（快速）**：Electron + LangChain.js → 当天就能跑通原型。

**路径二（进阶）**：Deno Desktop → 学习成本为零，等生态成熟后迁移。

**路径三（长期）**：Tauri + Rust → 前端不变 + Rust 后端推理，约 8-10 周。

### 6.3 移动端原生开发者（Swift / Kotlin）

**快速路线**：PySide6 + QML。QML 的声明式语法和 SwiftUI / Compose 思维一致，Python 的 AI 生态补上移动端缺失的能力。约 6-8 周。

**长期路线**：Qt6 C++。如果已有 C++ 基础（很多游戏/渲染方向移动端开发者有），直接走 C++ 路线做终极性能。约 12-16 周。

### 6.4 C++ / 系统级开发者

**最优路径**：Qt6 C++ + llama.cpp。零 Python 依赖，全链路 C++。Agent 编排如果复杂度高，用 Python 子进程辅助。

### 6.5 实战踩坑记录

1. **Python GIL 是真问题**。PySide6 中如果 Agent 推理时阻塞了 GIL，整个 UI 会卡死。解决方案：Agent 逻辑跑在独立 QThread 或子进程中，UI 层只收发信号。

2. **Electron 的 node-llama-cpp 是小马拉大车**。如果你真的需要本地推理，不要在 Node.js 里跑 —— 用 Python 子进程或独立的推理服务。

3. **MCP 协议是解耦的银弹**。不要把 UI 和 Agent 逻辑焊死在同一进程里。用 MCP 连接可以让 UI 层（Electron/Tauri）和 Agent 层（Python）独立演进。

4. **LangChain.js 的 Tool Calling 比 Python 版功能少**。如果你需要复杂的自定义 Tool（比如需要异步执行 Shell 命令并流式返回输出），Python 版 LangChain 的 Tool 抽象更完整。

5. **CMake 是 Qt6 C++ 路线的第一道墙**。现代应用开发者大多不直接和构建系统打交道，但 Qt6 世界里 CMake 无法绕过。直接用 Qt Creator 生成模板。

---

## 七、IDE 选择指南

选对 IDE 和选对框架一样重要。AI Agent 开发涉及多语言混合（Python 写 Agent、C++/Rust 写推理、JS/TS 写 UI），一个趁手的 IDE 能让你少踩 70% 的环境配置坑。

### 7.1 各框架 IDE 推荐总览

| 框架 | 首选 IDE | 备选 IDE | macOS 体验 | 核心理由 |
|------|---------|---------|:---:|------|
| **Qt6 (C++)** | **Qt Creator** | CLion / VS Code | ★★★★★ | QML 实时预览、信号/槽自动补全、RHI 调试器 |
| **Qt6 (Python)** | **PyCharm Pro** | VS Code / Qt Creator | ★★★★☆ | Python 类型推断 + Qt 绑定，补全远超 VS Code |
| **Electron** | **VS Code** | WebStorm | ★★★★★ | JS/TS 一等公民，Chrome DevTools 集成 |
| **Deno Desktop** | **VS Code** | 无成熟替代 | ★★★★☆ | Deno 官方扩展 + LSP，唯一深度集成 |
| **Tauri** | **VS Code** | RustRover / Zed | ★★★★★ | Rust Analyzer + 前端扩展同窗口，双语言零切换 |
| **Flutter** | **VS Code** | Android Studio | ★★★★★ | Flutter 扩展 + Dart LSP，热重载和 Inspector 完美 |
| **Wails** | **VS Code** | GoLand | ★★★★☆ | Go 扩展 + 前端双开，GoLand 重构更强但缺前端 |
| **Avalonia** | **Rider** | VS Code + C# Dev Kit | ★★★☆☆ | Rider 的 XAML 预览天花板，VS Code C# 差一档 |
| **Kotlin Compose** | **IntelliJ IDEA** | Fleet | ★★★★☆ | JetBrains 自家 Kotlin，Compose 预览开箱即用 |
| **Dioxus** | **VS Code** | RustRover | ★★★★☆ | Rust Analyzer + Dioxus 语法高亮，够用 |

### 7.2 macOS 平台深度推荐

macOS 上开发桌面 AI Agent 应用，IDE 选择比 Windows/Linux 多了一层考量：**Xcode 工具链是所有框架的编译基础**，但你不一定需要打开 Xcode。

---

#### 🥇 通用首选：VS Code

**适合框架**：Electron、Deno Desktop、Tauri、Flutter、Wails、Dioxus

macOS 上 VS Code 的 Apple Silicon 原生支持、Metal 渲染性能和扩展生态都是最佳状态。对 AI Agent 开发尤其友好：

- **GitHub Copilot / Copilot Chat**：AI 辅助写 Agent 代码，Python/TS/Rust 全语言支持
- **Jupyter 扩展**：在 VS Code 里跑 `.ipynb` 调试 LangChain Agent 原型再导出
- **REST Client 扩展**：直接测试 LLM API（OpenAI / Anthropic / Ollama 本地接口）
- **Remote - SSH**：Agent 推理层跑远程 GPU，本地 VS Code 远程开发

```bash
# macOS 安装 VS Code + AI Agent 必备扩展
brew install --cask visual-studio-code

code --install-extension ms-python.python         # Python Agent
code --install-extension denoland.vscode-deno      # Deno Desktop
code --install-extension rust-lang.rust-analyzer   # Tauri / Dioxus
code --install-extension dart-code.flutter         # Flutter
code --install-extension github.copilot            # AI 辅助
code --install-extension github.copilot-chat       # AI Chat
```

---

#### 🥈 Qt6 开发者的最佳选择：Qt Creator

**适合框架**：Qt6 C++、Qt6 Python (PySide6)

macOS 上 Qt Creator 的体验和 Xcode 一脉相承，但专门为 Qt 优化：

- **Design 模式**：拖拽式 QML UI 设计，所见即所得。macOS 上直接预览 Aqua 风格控件
- **信号/槽自动补全**：`connect(` 之后自动列出所有可用信号，其他 IDE 做不到
- **Qt RHI 调试**：macOS 上走 Metal 后端时，Qt Creator 可抓帧分析渲染性能
- **CMake 项目模板**：一键生成 macOS bundle 项目，不用手写 `Info.plist`

```bash
# macOS 安装 Qt Creator（开源版）
brew install --cask qt-creator

# 或通过 Qt 在线安装器获取完整 SDK
# https://www.qt.io/download-open-source
```

> Qt6 Python (PySide6) 推荐 **PyCharm Professional + Qt Creator 双开**：PyCharm 写 Python Agent 逻辑，Qt Creator 打开同一项目的 QML 文件做 UI 预览。PyCharm 免费 Community 版不支持 QML 语法高亮，可用 VS Code + QML 扩展替代。

---

#### 🥉 JetBrains 全家桶：专业团队之选

macOS 上 JetBrains IDE 的 UI 渲染走 JBR（JetBrains Runtime），Apple Silicon 原生支持。均为付费产品（Community 版功能受限）。

| 框架 | 推荐 JetBrains IDE | 免费替代 |
|------|-------------------|---------|
| Qt6 Python | **PyCharm Professional** | VS Code + Python + QML 扩展 |
| Qt6 C++ | **CLion** | Qt Creator（免费且更好） |
| Electron / Deno | **WebStorm** | VS Code（功能几乎一致） |
| Tauri / Dioxus | **RustRover** | VS Code + Rust Analyzer |
| Avalonia | **Rider** | VS Code + C# Dev Kit |
| Kotlin Compose | **IntelliJ IDEA Ultimate** | IDEA Community + Kotlin 插件 |
| Wails | **GoLand** | VS Code + Go 扩展 |

**选 JetBrains 的理由**：Toolbox App 统一管理版本、跨 IDE 共享设置、AI Assistant 跨 IDE 可用。

**不选 JetBrains 的理由**：订阅费（个人 ~¥1000/年/产品，全包 ~¥2500/年）；Qt6 C++ 不如 Qt Creator（CLion 无 QML 实时预览）；Electron/Deno 体验和免费 VS Code 无本质差距。

### 7.3 macOS 特有环境前置条件

不管选哪个 IDE，macOS 上都需要这些基础工具：

```bash
# 1. Xcode Command Line Tools（所有框架的编译基础）
xcode-select --install

# 2. Homebrew 包管理器
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 3. 按框架装编译依赖
brew install cmake ninja         # Qt6
brew install node                # Electron / Deno Desktop
brew install rustup-init         # Tauri / Dioxus（装完运行 rustup-init）
brew install --cask flutter      # Flutter
brew install go                  # Wails
```

### 7.4 AI Agent 开发的 IDE 工作流建议

AI Agent 桌面开发的特点是**多语言混合 + 多进程调试**，推荐工作流：

```
┌─────────────────────────────────────────┐
│              终端 1                       │
│  ollama serve                            │  ← 本地模型推理（常驻后台）
│  GGUF 模型热加载，API 端点 :11434          │
├─────────────────────────────────────────┤
│              终端 2                       │
│  python agent_server.py                  │  ← Agent 核心进程
│  LangGraph + MCP Server                  │     PyCharm 调试模式
├─────────────────────────────────────────┤
│              IDE 主窗口                   │
│  VS Code / Qt Creator / PyCharm          │  ← UI + Agent 逻辑开发
│  前端代码 + Agent 代码 + 断点调试           │
├─────────────────────────────────────────┤
│              终端 3                       │
│  deno desktop / npm run dev              │  ← 桌面应用热重载预览
└─────────────────────────────────────────┘
```

**关键技巧**：
- **模型服务独立运行**：`ollama serve` 或 `llama-server` 常驻后台，IDE 只调试 Agent 逻辑
- **Agent 核心用 Python**：PyCharm 中断点观察 LangGraph 状态流转和 Tool Calling 输入输出
- **UI 层用 VS Code**：前端热重载，改 UI 不重启 Agent
- **MCP Inspector**：`npx @modelcontextprotocol/inspector` 浏览器调试 MCP Tool 请求/响应

---

## 八、总结

回到最初的问题：**纯从 AI Agent 开发的角度，跨平台桌面框架怎么选？**

**核心结论：Python 是主场，Electron 是高效率，C++/Rust 是性能壁垒。**

| 如果你的优先级是… | 推荐框架 | 一句话理由 |
|:---|:---|------|
| **AI 生态完整性** | Qt6 Python (PySide6) | LangChain + MCP + 本地推理，一个进程搞定 |
| **开发效率** | Electron | JS/TS 全栈，前端生态 + AI SDK 开箱即用 |
| **本地推理性能** | Qt6 C++ | llama.cpp C++ API 是天花板 |
| **包体最小** | Tauri | 3MB + 模型文件 |
| **TS 全栈轻量** | Deno Desktop | 零 IPC，但 2026 年还需观察 |
| **Go 生态** | Wails | Go 团队的最佳桌面入口 |
| **C# 生态** | Avalonia | .NET 企业的自然选择 |
| **Dart 全栈** | Flutter | 云端 Agent 可用，本地推理不行 |

**最重要的建议**：用 MCP 协议解耦 UI 和 Agent。选择 UI 框架时按团队技术栈走（Electron/React 或 Qt/QML），Agent 核心用 Python 独立部署。这是 2026 年最务实也最具弹性的架构。

---

## 九、跨平台框架资源大全（官网 · 安装 · 文档）

### 9.1 Web 套壳派

#### Electron

| 类型 | 链接 |
|------|------|
| 官网 | <https://www.electronjs.org/> |
| 中文官网 | <https://electron.nodejs.cn/> |
| 安装 | `npm install electron` |
| 英文文档 | <https://www.electronjs.org/docs/latest/> |
| 中文文档 | <https://electron.nodejs.cn/docs/latest/> |
| GitHub | <https://github.com/electron/electron> |

> 安装前提：Node.js ≥ 18。推荐用 `electron-builder` 打包。

---

#### Tauri

| 类型 | 链接 |
|------|------|
| 官网 | <https://tauri.app/> |
| 中文官网 | <https://v2.tauri.org.cn/> |
| 安装 | `npm create tauri-app@latest` |
| 英文文档 | <https://tauri.app/start/> |
| 中文文档 | <https://v2.tauri.org.cn/start/> |
| GitHub | <https://github.com/tauri-apps/tauri> |

> 安装前提：Rust toolchain + 系统 WebView2（Win）/ WebKitGTK（Linux）。

---

#### Wails

| 类型 | 链接 |
|------|------|
| 官网 | <https://wails.io/> |
| 中文文档 | <https://wails.golang.ac.cn/> |
| 安装 | `go install github.com/wailsapp/wails/v3/cmd/wails@latest` |
| 英文文档 | <https://wails.io/docs/> |
| GitHub | <https://github.com/wailsapp/wails> |

> 安装前提：Go ≥ 1.21 + Node.js。

---

#### Deno Desktop `★ 2026 新星`

| 类型 | 链接 |
|------|------|
| 官网 | <https://deno.com/> |
| 桌面文档 | <https://docs.deno.com/runtime/desktop/> |
| 安装 | `curl -fsSL https://deno.land/install.sh \| sh` |
| 中文文档 | <https://docs.deno.org.cn/> |
| GitHub | <https://github.com/denoland/deno> |

> `deno desktop` 命令从 v2.9 开始内置。

---

#### NW.js

| 类型 | 链接 |
|------|------|
| 官网 | <https://nwjs.io/> |
| 英文文档 | <https://docs.nwjs.io/> |
| 中文文档 | <https://nwjs-cn.readthedocs.io/> |
| GitHub | <https://github.com/nwjs/nw.js> |

---

#### Electrobun `★ 2026 新星`

| 类型 | 链接 |
|------|------|
| GitHub | <https://github.com/blackboardsh/electrobun> |

> Bun + Zig + WebView，早期实验阶段。

---

### 9.2 Rust 原生派

#### Dioxus

| 类型 | 链接 |
|------|------|
| 官网 | <https://dioxuslabs.com/> |
| 文档 | <https://dioxuslabs.com/learn/0.7/> |
| 安装 | `cargo install dioxus-cli` |
| GitHub | <https://github.com/DioxusLabs/dioxus> |

---

#### Slint

| 类型 | 链接 |
|------|------|
| 官网 | <https://slint.dev/> |
| 文档 | <https://docs.slint.dev/latest/docs/slint/> |
| 中文参考 | <https://qi-xmu.github.io/slint-reference-zh/> |
| GitHub | <https://github.com/slint-ui/slint> |

> 体积 <300KB，适合轻量嵌入式 Agent。

---

### 9.3 企业级原生派

#### Qt6

| 类型 | 链接 |
|------|------|
| 官网 | <https://www.qt.io/development/qt-framework/qt6> |
| 下载（开源版） | <https://www.qt.io/download-open-source> |
| 英文文档 | <https://doc.qt.io/qt-6/> |
| 中文文档 | <https://doc.qt.ac.cn/> |
| PySide6 文档 | <https://doc.qt.io/qtforpython-6/> |

> 开源版 LGPLv3/GPLv3。国内推荐清华镜像：`https://mirrors.tuna.tsinghua.edu.cn/qt/`

---

#### Flutter

| 类型 | 链接 |
|------|------|
| 官网 | <https://flutter.dev/> |
| 中文文档 | <https://docs.flutter.cn/> |
| 桌面端指南 | <https://docs.flutter.dev/platform-integration/desktop> |
| GitHub | <https://github.com/flutter/flutter> |

---

#### .NET MAUI

| 类型 | 链接 |
|------|------|
| 官网 | <https://dotnet.microsoft.com/en-us/apps/maui> |
| 安装 | `dotnet workload install maui` |
| 文档 | <https://learn.microsoft.com/en-us/dotnet/maui/> |
| GitHub | <https://github.com/dotnet/maui> |

---

#### Kotlin Multiplatform + Compose Desktop

| 类型 | 链接 |
|------|------|
| 官网 | <https://kotlinlang.org/compose-multiplatform/> |
| 文档 | <https://kotlinlang.org/docs/multiplatform.html> |
| 中文文档 | <https://docs.kmpstudy.com/> |
| GitHub | <https://github.com/JetBrains/compose-multiplatform> |

---

#### Avalonia

| 类型 | 链接 |
|------|------|
| 官网 | <https://avaloniaui.net/> |
| 安装 | `dotnet new install Avalonia.Templates` |
| 文档 | <https://docs.avaloniaui.net/> |
| 中文文档 | <https://avaloniachina.github.io/avalonia-docs/> |
| GitHub | <https://github.com/AvaloniaUI/Avalonia> |

---

#### Uno Platform

| 类型 | 链接 |
|------|------|
| 官网 | <https://platform.uno/> |
| 文档 | <https://platform.uno/docs/articles/intro.html> |
| GitHub | <https://github.com/unoplatform/uno> |

---

### 9.4 新锐实验派

#### Neutralinojs

| 类型 | 链接 |
|------|------|
| 官网 | <https://neutralino.js.org/> |
| 安装 | `npm i -g @neutralinojs/neu` |
| 文档 | <https://neutralino.js.org/docs/> |
| GitHub | <https://github.com/neutralinojs/neutralinojs> |

> C++ 轻量后端 + WebView，Hello World ~5MB。

---

#### React Native (Windows + macOS)

| 类型 | 链接 |
|------|------|
| 官网 | <https://microsoft.github.io/react-native-windows/> |
| 中文文档 | <https://msdocs.cn/react-native-windows/> |
| GitHub | <https://github.com/microsoft/react-native-windows> |

---

### 9.5 AI Agent 生态资源

| 资源 | 链接 | 说明 |
|------|------|------|
| LangChain Python | <https://python.langchain.com/> | Agent 编排框架（Python） |
| LangChain.js | <https://js.langchain.com/> | Agent 编排框架（JS/TS） |
| LangGraph | <https://langchain-ai.github.io/langgraph/> | 有状态多步 Agent 编排 |
| LlamaIndex | <https://docs.llamaindex.ai/> | RAG 数据框架 |
| CrewAI | <https://docs.crewai.com/> | 多 Agent 协作框架 |
| AutoGen | <https://microsoft.github.io/autogen/> | 微软多 Agent 框架 |
| Vercel AI SDK | <https://sdk.vercel.ai/> | 前端 AI 组件 + 流式响应 |
| MCP 协议 | <https://modelcontextprotocol.io/> | Agent-Tool 标准通信协议 |
| llama.cpp | <https://github.com/ggerganov/llama.cpp> | C++ 本地推理引擎 |
| ONNX Runtime | <https://onnxruntime.ai/> | 跨平台模型推理 |
| Ollama | <https://ollama.com/> | 一键本地模型部署 |
| Semantic Kernel | <https://learn.microsoft.com/en-us/semantic-kernel/> | 微软 AI Agent 框架 (C#/Python/Java) |

---

*本文持续更新中，欢迎通过 [GitHub Issues](https://github.com/sunyazhou/sunyazhou.github.io/issues) 交流指正。*
