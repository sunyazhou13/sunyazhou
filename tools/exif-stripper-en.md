---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 66a6a10d0836fcca0ea80e5efce6d346_3b21d3a79f3f11f1a238525400e6dd8f
    ReservedCode1: Z05BejYXFB5rXX09euDAmCGeu8rYeH4LsrMSslWRpTmzFS0xojVENTpQpdnklHLZg+mx/MlrxRbMbZTkhGlGq6ul/xbXJrrkS7Xa/MAR/EPSH/Pdl+NctjsIp/MG6yAn+ShY5aMBC8nMVHRZsc2fGjKtuaG05WGpfy134aWLEkAaytu3qWPuTIxRLWE=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 66a6a10d0836fcca0ea80e5efce6d346_3b21d3a79f3f11f1a238525400e6dd8f
    ReservedCode2: Z05BejYXFB5rXX09euDAmCGeu8rYeH4LsrMSslWRpTmzFS0xojVENTpQpdnklHLZg+mx/MlrxRbMbZTkhGlGq6ul/xbXJrrkS7Xa/MAR/EPSH/Pdl+NctjsIp/MG6yAn+ShY5aMBC8nMVHRZsc2fGjKtuaG05WGpfy134aWLEkAaytu3qWPuTIxRLWE=
---



Upload a JPEG / PNG image and all of its EXIF metadata is parsed and displayed automatically (camera, model, shooting time, GPS coordinates, etc.). Strip every metadata field with one click to download a sanitized image, with a before/after file-size comparison. Everything runs locally in your browser — your images are never uploaded.

<link rel="stylesheet" href="/assets/tools/exif-stripper/app.css">

<div id="exif-stripper-app">

  <div class="exif-stripper-drop" id="exif-stripper-drop" tabindex="0" role="button" aria-label="Choose or drop an image">
    <input type="file" id="exif-stripper-file" accept="image/jpeg,image/jpg,image/png" hidden>
    <i class="fas fa-image"></i>
    <p class="exif-stripper-drop-title">Drop an image or click to select JPEG / PNG</p>
    <p class="exif-stripper-drop-sub">Parses and shows all metadata first, then strips it with one click · drag &amp; drop supported</p>
  </div>

  <div class="exif-stripper-info" id="exif-stripper-info" hidden></div>

  <div class="exif-stripper-actions" id="exif-stripper-actions" hidden>
    <button type="button" class="exif-stripper-btn exif-stripper-btn-primary" id="exif-stripper-strip">Strip all metadata</button>
    <button type="button" class="exif-stripper-btn" id="exif-stripper-download" disabled>Download cleaned image</button>
    <button type="button" class="exif-stripper-btn" id="exif-stripper-reset">Choose again</button>
    <span class="exif-stripper-status" id="exif-stripper-status" role="status"></span>
  </div>

  <div class="exif-stripper-stats" id="exif-stripper-stats" hidden>
    <div class="exif-stripper-stat" id="exif-stripper-stat-before"></div>
    <div class="exif-stripper-stat" id="exif-stripper-stat-diff"></div>
  </div>

  <div class="exif-stripper-sec" id="exif-stripper-sec" hidden>
    <h3>Metadata details (<span id="exif-stripper-count"></span>)</h3>
    <div class="exif-stripper-table-wrap">
      <table class="exif-stripper-table">
        <thead><tr><th>Group</th><th>Field</th><th>Value</th></tr></thead>
        <tbody id="exif-stripper-tbody"></tbody>
      </table>
    </div>
  </div>

</div>

<script src="/assets/tools/exif-stripper/app.js" defer></script>
*（内容由AI生成，仅供参考）*
