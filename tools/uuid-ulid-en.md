---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 66a6a10d0836fcca0ea80e5efce6d346_3d45ab2e9f3f11f1a65b525400826444
    ReservedCode1: K51GY2loz+UeqzAjyQjt/TSvYE2zyfZdHJ1S9rNL1z/wHHO4XcnihzUExt1Td8+GTsl1F4KEGuNpHrn/XzSBefB/P0BUolzVLX83yj3dU4fh72M3o5RYjDsxxTosAOQuuXVF58vA/Lk7ADHrhJBJWH25ojogZ9FdPGu8KaCafCXhgCpozNTKvXd6Q3A=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 66a6a10d0836fcca0ea80e5efce6d346_3d45ab2e9f3f11f1a65b525400826444
    ReservedCode2: K51GY2loz+UeqzAjyQjt/TSvYE2zyfZdHJ1S9rNL1z/wHHO4XcnihzUExt1Td8+GTsl1F4KEGuNpHrn/XzSBefB/P0BUolzVLX83yj3dU4fh72M3o5RYjDsxxTosAOQuuXVF58vA/Lk7ADHrhJBJWH25ojogZ9FdPGu8KaCafCXhgCpozNTKvXd6Q3A=
---



Generate <strong>UUID v4</strong> and <strong>ULID</strong> identifiers with one click, in batches of 1 / 10 / 100. Copy a single item, copy all, or generate another batch. Everything is generated locally in your browser (preferring <code>crypto.getRandomValues</code>) — your data is never uploaded.

<link rel="stylesheet" href="/assets/tools/uuid-ulid/app.css">

<div id="uu-app">
  <div class="uu-controls">
    <label>Type
      <select id="uu-type">
        <option value="uuid">UUID v4</option>
        <option value="ulid">ULID</option>
      </select>
    </label>
    <label>Count
      <select id="uu-count">
        <option value="1">1</option>
        <option value="10" selected>10</option>
        <option value="100">100</option>
      </select>
    </label>
    <button type="button" class="uu-btn uu-btn-primary" id="uu-gen">Generate</button>
    <button type="button" class="uu-btn" id="uu-more">Regenerate</button>
    <button type="button" class="uu-btn" id="uu-copy-all">Copy all</button>
  </div>

  <div class="uu-quick">
    <span class="uu-quick-label">Quick:</span>
    <button type="button" class="uu-btn uu-btn-sm" data-type="uuid" id="uu-quick-uuid">UUID ×1</button>
    <button type="button" class="uu-btn uu-btn-sm" data-type="ulid" id="uu-quick-ulid">ULID ×1</button>
  </div>

  <div class="uu-status" id="uu-status" role="status"></div>
  <div class="uu-list" id="uu-list"></div>
</div>

<script src="/assets/tools/uuid-ulid/app.js" defer></script>
*（内容由AI生成，仅供参考）*
