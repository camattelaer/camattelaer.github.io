---
layout: single
author_profile: true
---

## Latest Posts

## Latest Posts

{% assign latest_compchem = site["computational-chemistry"] | sort: "date" | reverse | first %}
{% assign latest_sysadmin = site.sysadmin | sort: "date" | reverse | first %}

{% if latest_compchem %}
### Computational Chemistry
{% include archive-single.html post=latest_compchem type="list" %}
{% endif %}

{% if latest_sysadmin %}
### Sysadmin
{% include archive-single.html post=latest_sysadmin type="list" %}
{% endif %}

Welcome to my personal website.

Work in progress...
