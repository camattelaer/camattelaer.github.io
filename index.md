---
layout: single
classes: wide
author_profile: true
---

Welcome to my personal website.

Work in progress...

## Latest Posts

<div class="homepage-featured">

  <div class="featured-box">
    <h3>Computational Chemistry</h3>
    {% assign compchem_sorted = site["computational-chemistry"] | sort: "date" | reverse %}
    {% for post in compchem_sorted limit:1 %}
      {% include archive-single.html type="list" %}
    {% endfor %}
  </div>

  <div class="featured-box">
    <h3>Sysadmin</h3>
    {% assign sysadmin_sorted = site.sysadmin | sort: "date" | reverse %}
    {% for post in sysadmin_sorted limit:1 %}
      {% include archive-single.html type="list" %}
    {% endfor %}
  </div>

</div>
