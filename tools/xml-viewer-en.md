---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 66a6a10d0836fcca0ea80e5efce6d346_3a7773609f3f11f1a65b525400826444
    ReservedCode1: MuW0xKlAivlag9zLtExNRca+Dfda+2O9X+Pzh+U2G5MUMso9ceVXey2L4QjD8Be8ql6eyHXdaH/HL9FCMZbj+877sY9c3FyQKhfPC0g48mMATRreIq/A+7q19jAEP4KnGWprQClN8IopUP6mwd/A8N4BmPH8QLCuHpg0CLVhWlmoutrKTHXlFtX4TKA=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 66a6a10d0836fcca0ea80e5efce6d346_3a7773609f3f11f1a65b525400826444
    ReservedCode2: MuW0xKlAivlag9zLtExNRca+Dfda+2O9X+Pzh+U2G5MUMso9ceVXey2L4QjD8Be8ql6eyHXdaH/HL9FCMZbj+877sY9c3FyQKhfPC0g48mMATRreIq/A+7q19jAEP4KnGWprQClN8IopUP6mwd/A8N4BmPH8QLCuHpg0CLVhWlmoutrKTHXlFtX4TKA=
---



Paste any XML / RSS / SML snippet to browse it as a structured tree; supports formatting, squeezing into a single line, one-click copy and download. Everything runs locally in your browser — your content is never uploaded.

<link rel="stylesheet" href="/assets/tools/xml-viewer/app.css">

<div id="xv-app">
  <textarea id="xv-input" spellcheck="false" aria-label="XML input"></textarea>

  <div class="xv-bar">
    <button type="button" class="xv-btn xv-btn-ghost" id="xv-sample" aria-label="Load sample">Sample</button>
    <button type="button" class="xv-btn" id="xv-fmt">Format</button>
    <button type="button" class="xv-btn" id="xv-minify">Minify</button>
    <button type="button" class="xv-btn" id="xv-copy">Copy</button>
    <button type="button" class="xv-btn" id="xv-download">Download .xml</button>
    <button type="button" class="xv-btn" id="xv-tree-window">New window</button>
    <span class="xv-status" id="xv-status" role="status" aria-hidden="true"></span>
  </div>

  <div class="xv-error" id="xv-error" hidden></div>

  <div class="xv-placeholder" id="xv-placeholder">
    <p>No XML content yet.</p>
    <p>Click "Sample" to load a demo, or paste your XML above.</p>
  </div>

  <div class="xv-tree-wrap" id="xv-tree-wrap" hidden>
    <div class="xv-tree-head">
      <span class="xv-meta" id="xv-tree-meta"></span>
      <input type="search" class="xv-tree-search" id="xv-tree-search" placeholder="Search nodes…" aria-label="Search nodes">
      <button type="button" class="xv-btn" id="xv-tree-expand">Expand all</button>
      <button type="button" class="xv-btn" id="xv-tree-collapse">Collapse deep</button>
    </div>
    <div class="xv-tree" id="xv-tree" role="tree"></div>
  </div>
</div>

<script src="/assets/tools/xml-viewer/app.js" defer></script>
*（内容由AI生成，仅供参考）*
