---
title: 归档
icon: fas fa-archive
type: archives
# The Archives of posts.
# v2.0
# https://github.com/cotes2020/jekyll-theme-chirpy
# © 2017-2019 Cotes Chung
# MIT License
---

> 按时间顺序排列的所有文章记录，从入门 iOS 到探索图形学，每一步都值得被记住。

<div id="archives" class="pl-xl-2">
{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" | sort: "name" | reverse %}
{% for year_group in posts_by_year %}
  {% assign year = year_group.name %}
  <span class="lead">{{ year }}</span>
  <ul class="list-unstyled">
  {% for post in year_group.items %}
    <li>
      <div>
        <span class="date day">{{ post.date | date: "%d" }}</span>
        <span class="date month small text-muted">{{ post.date | date: "%b" }}</span>
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        {% if post.categories.size > 0 %}
          {% for cat in post.categories limit:1 %}
            <span class="archive-cat-badge">{{ cat }}</span>
          {% endfor %}
        {% endif %}
      </div>
    </li>
  {% endfor %}
  </ul>
{% endfor %}
</div>
