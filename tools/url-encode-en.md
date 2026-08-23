---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 66a6a10d0836fcca0ea80e5efce6d346_3c39ee229f3f11f1a65b525400826444
    ReservedCode1: N8X7i8kbDOKq1E7/mZqEakGod1eS5jTXYOFd4BBCeUAzlOSLIXRJA1cchFR64hj4pWvmHDZMVJTyy8oeMjgoCKYXVRixAmzvx+pUCkldD1oWBQF9a6UOhsiwG19mAa5YJ4Ulp3ZzpYPF7/mceyLFQDBdYzrj6RPHaiXen2vq6n+6m7O7OmLMU9ecYMI=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 66a6a10d0836fcca0ea80e5efce6d346_3c39ee229f3f11f1a65b525400826444
    ReservedCode2: N8X7i8kbDOKq1E7/mZqEakGod1eS5jTXYOFd4BBCeUAzlOSLIXRJA1cchFR64hj4pWvmHDZMVJTyy8oeMjgoCKYXVRixAmzvx+pUCkldD1oWBQF9a6UOhsiwG19mAa5YJ4Ulp3ZzpYPF7/mceyLFQDBdYzrj6RPHaiXen2vq6n+6m7O7OmLMU9ecYMI=
---



Convert text to and from percent encoding (URL encoding, `%20`, `%2F`, etc.) in both directions. Supports two modes — `encodeURIComponent` and `encodeURI` — with one-click swap between the two and one-click copy. Everything runs locally in your browser — your content is never uploaded.

<link rel="stylesheet" href="/assets/tools/url-encode/app.css">

<div id="ue-app">

  <div class="ue-mode-bar">
    <label class="ue-mode">
      <input type="radio" name="ue-mode" id="ue-comp" checked>
      <span>encodeURIComponent (encodes all reserved characters, for parameter values)</span>
    </label>
    <label class="ue-mode">
      <input type="radio" name="ue-mode" id="ue-uri">
      <span>encodeURI (keeps URL structure characters, for whole URLs)</span>
    </label>
  </div>

  <div class="ue-field">
    <span class="ue-field-tag" id="ue-src-tag">Input</span>
    <textarea id="ue-src" spellcheck="false" rows="5" placeholder="Type the text to encode or decode here…"></textarea>
  </div>

  <div class="ue-actions">
    <button type="button" class="ue-btn" id="ue-encode">Encode ▾ (→ %20)</button>
    <button type="button" class="ue-btn" id="ue-decode">Decode ▴ (← %20)</button>
    <button type="button" class="ue-btn" id="ue-swap">⇄ Swap (each click switches once)</button>
    <button type="button" class="ue-btn" id="ue-copy">Copy result</button>
    <button type="button" class="ue-btn" id="ue-clear">Clear</button>
  </div>

  <div class="ue-field">
    <span class="ue-field-tag" id="ue-dst-tag">Result</span>
    <textarea id="ue-dst" spellcheck="false" rows="5" readonly placeholder="Result…"></textarea>
  </div>

  <p class="ue-status" id="ue-status" role="status"></p>

</div>

<script src="/assets/tools/url-encode/app.js" defer></script>
*（内容由AI生成，仅供参考）*
