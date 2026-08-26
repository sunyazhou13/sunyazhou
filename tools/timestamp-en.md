---
layout: page
title: Timestamp Converter
icon: fas fa-clock
lang: en
permalink: /tools/timestamp/
tool_css: /assets/tools/timestamp/app.css
---

Real-time clock with millisecond precision, Unix timestamp ↔ date conversion with Apple `NSDate.timeIntervalSince1970` Double format support, and Swift / Objective-C API examples. All processing is local in your browser.

Notes:

- Current time: refreshes every 50ms, millisecond precision, showing Unix seconds / milliseconds / Apple Double alongside ISO 8601
- Timestamp → Date: auto-detects format (10-digit seconds / 13-digit milliseconds / Apple Double with decimal like `1692800123.456`), outputs local time, UTC, ISO 8601
- Date → Timestamp: pick date and time (optional milliseconds), outputs Unix seconds / milliseconds / Apple Double
- Code examples: Swift and Objective-C APIs for getting timestamps, converting timestamps to Date, formatting strings, ISO8601

<div id="ts-app">

  <div class="ts-clock">
    <div class="ts-clock-date" id="ts-now-date"></div>
    <div>
      <span class="ts-clock-time" id="ts-now-time">--:--:--</span><span class="ts-clock-ms" id="ts-now-ms"></span>
    </div>
    <div class="ts-clock-ts">
      <div class="ts-clock-ts-item"><span class="ts-clock-ts-label">sec</span><code class="ts-clock-ts-val" id="ts-now-ts"></code></div>
      <div class="ts-clock-ts-item"><span class="ts-clock-ts-label">ms</span><code class="ts-clock-ts-val" id="ts-now-ts-ms"></code></div>
      <div class="ts-clock-ts-item"><span class="ts-clock-ts-label">Apple</span><code class="ts-clock-ts-val" id="ts-now-ts-apple"></code></div>
    </div>
    <code class="ts-clock-iso" id="ts-now-iso"></code>
    <button type="button" class="ts-btn ts-btn-copy" id="ts-copy-now">Copy Apple Timestamp</button>
  </div>

  <div class="ts-panel">
    <h2 class="ts-title">Timestamp → Date</h2>
    <p class="ts-hint">Enter a timestamp (auto-detect: seconds / milliseconds / Apple Double like <code>1692800123.456</code>)</p>
    <div class="ts-row">
      <input type="text" class="ts-input" id="ts-input" placeholder="1692800123.456 or 1692800123 or 1692800123456" spellcheck="false" autocomplete="off">
      <button type="button" class="ts-btn ts-btn-primary" id="ts-convert">Convert</button>
    </div>
    <div class="ts-result" id="ts-result"></div>
  </div>

  <div class="ts-panel">
    <h2 class="ts-title">Date → Timestamp</h2>
    <div class="ts-row">
      <label class="ts-label" for="ts-date-input">Date</label>
      <input type="date" class="ts-date-input" id="ts-date-input">
      <label class="ts-label" for="ts-time-input">Time</label>
      <input type="time" class="ts-date-input" id="ts-time-input" step="1" value="00:00:00">
      <label class="ts-label" for="ts-ms-input">ms</label>
      <input type="number" class="ts-date-input" id="ts-ms-input" min="0" max="999" value="0" style="width:5rem">
      <button type="button" class="ts-btn ts-btn-primary" id="ts-date-convert">Convert</button>
    </div>
    <div class="ts-result" id="ts-date-result"></div>
  </div>

  <div class="ts-panel">
    <h2 class="ts-title">API Examples</h2>
    <div class="ts-tabs" id="ts-code-tabs">
      <button type="button" class="ts-tab ts-tab-active" data-lang="swift">Swift</button>
      <button type="button" class="ts-tab" data-lang="objc">Objective-C</button>
    </div>
    <pre class="ts-code-block"><code id="ts-code-output"></code></pre>
    <button type="button" class="ts-btn ts-btn-copy" id="ts-copy-code">Copy Code</button>
  </div>

  <div class="ts-error" id="ts-error" hidden></div>

</div>

<script type="module" src="/assets/tools/timestamp/app.js"></script>
