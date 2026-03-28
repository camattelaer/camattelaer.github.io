---
layout: single
author_profile: true
title: Welcome to my personal website.
---

## About me
My name is Charles-Alexandre Mattelaer. I entered computational chemistry in 2016 at the start of my PhD, drawn in by curiosity for the science itself and what we can learn from it.

I have a hands-on approach to the field: beyond the calculations, I enjoy building and maintaining the hardware they run on myself. This website is a byproduct of that: a place to document things that took me a while to figure out, so others wouldn't have to start from scratch.

I write here in the gaps between a full-time job and life with three young kids, so posts are infrequent but come when they come and originate from genuine experience. If something here is useful to you, that would exactly be the point.

## Why make a website?

This website exists for a couple of reasons.

First, some things took me longer to figure out than they should have. And I made a few hardware purchases along the way I'd rather not repeat. If you're getting started with computational chemistry or building your own workstation, NAS, or scientific software setup, I hope something here saves you some time and/or money.

Second, I was looking for a hobby that fits into the gaps of a busy day. Writing up a post, collecting notes, or just tidying a page turned out to be a surprisingly satisfying way to spend a few spare minutes on something I actually enjoy.

Perhaps as a third reason: if you've landed here and are limited by the hardware available to you, feel free to reach out. I'm happy to help where I can whether that's advice on calculations or something more hands-on. Just keep in mind that it's only me here, with a full-time job and three young kids, so don't expect a quick reply.

## Software

I prefer scientific software that is free for academic or personal use. Here is a non-exhaustive list of software I have experience with and available on my system:

- Molecular dynamics: AMBER, Gromacs, OpenMM
- Quantum chemistry: ORCA, Gamess
- General molecular modeling: Atomic Simulation Environment (ASE),
- Data analysis/maths: Python, Julia

Most of the posts on the website will relate to the software mentioned in the list above.

## Current topics for upcoming posts

| | | | | | |
|:-:|:-|:-:|:-|:-:|:-|
| 🟡 | Pending | 🔴 | In progres | 🟢 | Done |

### Molecular mechanics and dynamics

| Status |  <span style="display: inline-block; width:500px">Topic</span>  | Article |
|:------:|-------|---------|
| 🟡 | MM-GBSA and MM-PBSA: what it is & example | |
| 🟡 | Entropy and MM-GBSA | |
| 🟡 | QM/MM-GBSA | |
| 🟡 | MM-GBSA versus Steered MD | |

### Quantum mechanics

| Status |  <span style="display: inline-block; width:500px">Topic</span> | Article |
|:------:|-------|---------|
| 🔴 | HNA helical geometries | |
| 🟡 | Exploring `OPI` v2 ("Orca Python Interface") | |
| 🟡 | Exploring `MultiWFN` and non-covalent interaction (NCI) analysis | |

### Sysadmin

| Status | <span style="display: inline-block; width:500px">Topic</span> | Article |
|:------:|-------|---------|
| 🔴 | Home cluster v2 & breakdown of each node | |

<!-- | 🟢 | MM-GBSA and MM-PBSA: what it is & example | [Read →](https://yoursite.com/mm-gbsa) | -->

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
