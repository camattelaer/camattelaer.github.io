---
layout: single
author_profile: true
---

## Latest Posts

### Computational Chemistry
{% assign compchem_sorted = site["computational-chemistry"] | sort: "date" | reverse %}
{% for post in compchem_sorted limit:1 %}
  {% include archive-single.html type="list" %}
{% endfor %}

### Sysadmin
{% assign sysadmin_sorted = site.sysadmin | sort: "date" | reverse %}
{% for post in sysadmin_sorted limit:1 %}
  {% include archive-single.html type="list" %}
{% endfor %}

Welcome to my personal website.

Work in progress...
