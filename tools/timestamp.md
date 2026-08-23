---
layout: page
title: 时间戳转换
icon: fas fa-clock
---

实时显示当前日期时间（精确到毫秒），支持 Unix 时间戳与日期互转，优先兼容 Apple `NSDate.timeIntervalSince1970` 带毫秒的 Double 格式。提供 Swift / Objective-C 获取时间戳的 API 示例。所有计算均在浏览器本地完成。

几点说明：

- 当前时间：每 50ms 刷新，精确到毫秒，同时显示 Unix 秒 / 毫秒 / Apple Double 三种时间戳和 ISO 8601 格式
- 时间戳 → 日期：输入时间戳自动识别格式（10 位秒 / 13 位毫秒 / Apple Double 带小数如 `1692800123.456`），输出本地时间、UTC、ISO 8601
- 日期 → 时间戳：选择日期时间（可选毫秒），输出 Unix 秒 / 毫秒 / Apple Double 三种格式
- 代码示例：Swift 和 Objective-C 获取时间戳、时间戳转 Date、格式化字符串、ISO8601 等常用 API

<link rel="stylesheet" href="/assets/tools/timestamp/app.css">

<div id="ts-app">

  <!-- 实时时钟 -->
  <div class="ts-clock">
    <div class="ts-clock-date" id="ts-now-date"></div>
    <div>
      <span class="ts-clock-time" id="ts-now-time">--:--:--</span><span class="ts-clock-ms" id="ts-now-ms"></span>
    </div>
    <div class="ts-clock-ts">
      <div class="ts-clock-ts-item"><span class="ts-clock-ts-label">秒</span><code class="ts-clock-ts-val" id="ts-now-ts"></code></div>
      <div class="ts-clock-ts-item"><span class="ts-clock-ts-label">毫秒</span><code class="ts-clock-ts-val" id="ts-now-ts-ms"></code></div>
      <div class="ts-clock-ts-item"><span class="ts-clock-ts-label">Apple</span><code class="ts-clock-ts-val" id="ts-now-ts-apple"></code></div>
    </div>
    <code class="ts-clock-iso" id="ts-now-iso"></code>
    <button type="button" class="ts-btn ts-btn-copy" id="ts-copy-now">复制 Apple 时间戳</button>
  </div>

  <!-- 时间戳 → 日期 -->
  <div class="ts-panel">
    <h2 class="ts-title">时间戳 → 日期</h2>
    <p class="ts-hint">输入时间戳（自动识别秒 / 毫秒 / Apple Double 如 <code>1692800123.456</code>）</p>
    <div class="ts-row">
      <input type="text" class="ts-input" id="ts-input" placeholder="1692800123.456 或 1692800123 或 1692800123456" spellcheck="false" autocomplete="off">
      <button type="button" class="ts-btn ts-btn-primary" id="ts-convert">转换</button>
    </div>
    <div class="ts-result" id="ts-result"></div>
  </div>

  <!-- 日期 → 时间戳 -->
  <div class="ts-panel">
    <h2 class="ts-title">日期 → 时间戳</h2>
    <div class="ts-row">
      <label class="ts-label" for="ts-date-input">日期</label>
      <input type="date" class="ts-date-input" id="ts-date-input">
      <label class="ts-label" for="ts-time-input">时间</label>
      <input type="time" class="ts-date-input" id="ts-time-input" step="1" value="00:00:00">
      <label class="ts-label" for="ts-ms-input">毫秒</label>
      <input type="number" class="ts-date-input" id="ts-ms-input" min="0" max="999" value="0" style="width:5rem">
      <button type="button" class="ts-btn ts-btn-primary" id="ts-date-convert">转换</button>
    </div>
    <div class="ts-result" id="ts-date-result"></div>
  </div>

  <!-- 代码示例 -->
  <div class="ts-panel">
    <h2 class="ts-title">API 示例代码</h2>
    <div class="ts-tabs" id="ts-code-tabs">
      <button type="button" class="ts-tab ts-tab-active" data-lang="swift">Swift</button>
      <button type="button" class="ts-tab" data-lang="objc">Objective-C</button>
    </div>
    <pre class="ts-code-block"><code id="ts-code-output"></code></pre>
    <button type="button" class="ts-btn ts-btn-copy" id="ts-copy-code">复制代码</button>
  </div>

  <div class="ts-error" id="ts-error" hidden></div>

</div>

<script type="module" src="/assets/tools/timestamp/app.js"></script>
