---
layout: page
title: 工具
---

这里收录一些纯前端小工具。所有处理都在你的浏览器本地完成，**文件不会被上传到任何服务器**。

<div class="tools-landing">

{% assign enabled_tools = site.data.tools | where: "enabled", true %}

{% if enabled_tools.size == 0 %}

<p>暂无可用工具。</p>

{% else %}

<div class="tools-grid">
{% for tool in enabled_tools %}
<a class="tools-card" href="{{ tool.path }}">
  <span class="tools-card-head">
    <i class="{{ tool.icon }}"></i>
    <span class="tools-card-title">{{ tool.title }}</span>
  </span>
  <span class="tools-card-desc">{{ tool.description }}</span>
  <span class="tools-card-cta">打开工具 <i class="fas fa-angle-right"></i></span>
</a>
{% endfor %}
</div>

{% endif %}

</div>

<style>
.tools-landing { margin-top: 1rem; }
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.tools-card {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 1.2rem 1.3rem;
  border: 1px solid rgba(128, 128, 128, 0.35);
  border-radius: 10px;
  color: inherit;
  text-decoration: none !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.tools-card:hover {
  border-color: #2f6fde;
  box-shadow: 0 2px 12px rgba(47, 111, 222, 0.15);
}
.tools-card-head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1.1rem;
  font-weight: 500;
}
.tools-card-head i { color: #2f6fde; }
.tools-card-desc {
  font-size: 0.9rem;
  opacity: 0.75;
  line-height: 1.6;
}
.tools-card-cta {
  margin-top: auto;
  font-size: 0.85rem;
  color: #2f6fde;
}
[mode='dark'] .tools-card:hover { border-color: #5b8ff0; }
[mode='dark'] .tools-card-head i,
[mode='dark'] .tools-card-cta { color: #5b8ff0; }
</style>
