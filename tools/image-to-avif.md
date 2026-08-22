---
layout: page
title: 图片转 AVIF
icon: fas fa-image
---

把 PNG、JPEG、WebP、GIF、BMP、SVG 批量转成 AVIF。所有转换都在你的浏览器里本地完成，**图片不会上传到任何服务器**。

**编码引擎**：优先使用浏览器原生编码（Chrome / Edge 121+，解码走浏览器原生管线、支持硬件加速），不支持时自动回退到 WASM（libaom，来自 Squoosh 的 jsquash 移植）。首次使用 WASM 引擎需要下载约 3.5 MB 的编码器。

几点说明：

- 支持批量：可以一次拖入多张图片，甚至直接拖入整个文件夹
- 同一批里文件重名（比如两个不同目录的 `photo.png`）会自动加 `-1`、`-2` 序号后缀
- 动图（GIF / 动画 WebP）只取第一帧，列表里会明确标注
- 已经是 AVIF 的文件会直接跳过，避免二次有损压缩
- 质量滑杆数值越高画质越好、体积越大，一般 50–70 就够博客配图用
- WASM 引擎较慢属于正常现象（AVIF 编码本身就重），大批量建议用 Chrome / Edge 走原生路径

<link rel="stylesheet" href="/assets/tools/avif/app.css">

<div id="avt-app">

  <div class="avt-banner">
    <span class="avt-badge" id="avt-engine-badge">正在检测编码引擎…</span>
    <span class="avt-hint">所有转换都在本机浏览器完成，图片不会上传</span>
  </div>

  <div class="avt-drop" id="avt-drop" tabindex="0" role="button" aria-label="选择或拖入图片">
    <input type="file" id="avt-input" multiple hidden accept="image/png,image/jpeg,image/webp,image/gif,image/bmp,image/svg+xml,image/avif">
    <i class="far fa-images"></i>
    <p class="avt-drop-title">拖入图片或文件夹，或点击选择文件</p>
    <p class="avt-drop-sub">支持 PNG · JPEG · WebP · GIF · BMP · SVG · AVIF，可多选</p>
  </div>

  <div class="avt-options">
    <label>质量 <output id="avt-q-val">60</output>
      <input type="range" id="avt-quality" min="10" max="100" step="1" value="60">
    </label>
    <label>编码引擎
      <select id="avt-engine">
        <option value="auto" selected>自动（优先原生）</option>
        <option value="native">仅原生 Canvas</option>
        <option value="wasm">仅 WASM</option>
      </select>
    </label>
    <label>压缩速度
      <select id="avt-speed">
        <option value="9">快</option>
        <option value="8" selected>均衡</option>
        <option value="6">极致压缩</option>
      </select>
    </label>
    <label>限制最大宽度
      <select id="avt-maxw">
        <option value="0" selected>不限</option>
        <option value="2560">2560px</option>
        <option value="1920">1920px</option>
        <option value="1280">1280px</option>
        <option value="960">960px</option>
      </select>
    </label>
    <div class="avt-actions">
      <button type="button" class="avt-btn avt-btn-primary" id="avt-convert" disabled>开始转换</button>
      <button type="button" class="avt-btn" id="avt-zip" disabled>打包下载 ZIP</button>
      <button type="button" class="avt-btn" id="avt-clear" disabled>清空</button>
    </div>
  </div>

  <div class="avt-summary" id="avt-summary" hidden></div>

  <ul class="avt-list" id="avt-list"></ul>

</div>

<script type="module" src="/assets/tools/avif/app.js"></script>
