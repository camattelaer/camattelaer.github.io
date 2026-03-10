---
layout: single
author_profile: true
title: Welcome to my personal website.
---

## About me

## Why make a website?

I started this website for two reasons.

1) Some things took a while to figure out - and perhaps also some wrong purchases when it comes to hardware. I want to share my experiences for people with similar interest and who are looking for information to start with either computational chemistry or "sysadmin" related topics (i.e. building your own workstation, NAS, or installing scientific software). 

2) On a more personal note, I was on the lookout for hobbies that would only require several minutes of time for some sense of achievement. Maintaining a website, gathering info for a post on said website or actually writing that post seemed like an excellent way of spending just a few minutes doing things I enjoy.

A third reason that came across my mind might be reaching people who are not so fortunate with available hardware. If you come across this website and would be in need of technical assistance with calculations or hardware to run them on. Please feel free to reach out. Remember that it is just me running this joint and I have a full time job and three small children so I will not be able to provide on-the-fly responses.

## Software

I prefer scientific software that is free for academic or personal use. Here is a non-exhaustive list of software I have experience with and available on my system:

- Molecular dynamics: AMBER, Gromacs, OpenMM
- Quantum chemistry: ORCA, Gamess
- General molecular modeling: Atomic Simulation Environment (ASE),
- Data analysis/maths: Python, Julia

Most of the posts on the website will relate to the software mentioned in the list above.

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
