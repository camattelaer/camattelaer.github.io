---
title: "The geometry of HNA duplexes"
date: 2026-05-30
layout: single
classes: single
author_profile: false
math: true
molecule: true
header:
  teaser: /assets/content/compchem/HNAgeometries/teaser.png
sidebar:
  - nav: "hna-geometries"
  # - title: "Disclaimer"
  #   text: "All files used for visualization or discussion are made available under the respective folder in `/assets/content/compchem`"
---

---
## Disclaimer
Files and code relevant for this post have been made available:
 - [Github](https://github.com/camattelaer/HNAduplex): scripts and data
 <!-- - [Zenodo](): code, model and raw data -->

---

## Introduction

Modified nucleosides/nucleotides formed the main research topic of my PhD. It was widely believed that HNA (1&prime;­­,5′-anhydrohexitol nucleic acids or simply hexitol nucleic acids) adopt A-type helical geometries when forming a duplex structure when I started my PhD. In the beginning of 2025, [a paper](https://academic.oup.com/nar/article/53/1/gkae1156/7915239#500070168) was published that analyzed a ternary complex between a mutated DNA polymerase, a DNA oligomer (primer) and an HNA-modified oligomer (template). The resulting structure can be visualized using PDB-code [9EMI](https://www.rcsb.org/structure/9EMI).   

The interesting part of structure 9EMI is the fact that the template HNA residues which interact with the primer DNA residues adopt a different conformation for the hexitol ring than expected. For the typical A-type duplexes, hexitol conformations are typically in $^{4′}C_{1′}$ ($C$ = chair conformation, the letter is preceded by the atom which is above the reference plane of the 4 central atoms and followed by the atom below this plane) which places the nucleobase axially. In 9EMI, these three interacting HNA residues are in a $^{1′}C_{4′}$ conformation which places the nucleobase equatorially, see Figure 1.

<!-- <div style="width: 100%; margin: 0 auto 1em auto; text-align: center;">
  <img src="{{ '/assets/images/compchem/HNAgeometries/Figure01_9EMI.jpg' | relative_url }}" 
       alt="Figure 1"
       style="width: 100%; height: auto;">
  <div style="
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
  Figure 1: Template HNA residues interacting with primer DNA residues in PDB-code 9EMI clearly position the nucleobase equatorially with respect to the hexitol ring.
  </div>
</div> -->

<figure style="margin: 1.5em 0;">
  <div id="mol-9EMI"
     style="width:100%; height:500px; position:relative; ">
  </div>

  <figcaption style="
    text-align: center;
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
  Figure 1: Interactive render of PDB 9EMI. Template HNA residues interacting with primer DNA residues clearly position the nucleobase equatorially with respect to the hexitol ring.
  </figcaption>
</figure>

## A blast from the past

Reading this paper immediately triggered a memory of a hypothesis I had towards the end of my PhD. After the conformational analysis of HNA nucleosides and the investigation into the two different chair conformations, I noticed that a B-type helical backbone combined with the $^{1′}C_{4′}$ conformation of the hexitol ring actually aligns nucleobases to form proper stacking interaction. Hence my hypothesis that alongside the (global) minimum of A-type helix for oligonucleotide duplexes, a (local) minimum exists for the B-type variant and I started investigating this late in 2020, see Figure 2. 

<div style="width: 100%; margin: 0 auto 1em auto; text-align: center;">
  <img src="{{ '/assets/content/compchem/HNAgeometries/Figure02_dropbox.jpg' | relative_url }}" 
       alt="Placeholder"
       style="width: 100%; height: auto;">
  <div style="
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
  Figure 2: Screenshot of Dropbox metadata.
  </div>
</div>

Time was limited since I neared the end of my PhD journey so I could not complete this investigation. The DFT optimization was incomplete: some imaginary frequencies remained:
```
   6:      -139.05 cm**-1 ***imaginary mode***
   7:       -21.87 cm**-1 ***imaginary mode***
```
Normal mode 6 (v006) is related to a terminal hydroxyl and as such of less interest. Normal mode 7 (v007), however, is related to overall duplex structure, see Figure 3. Although the amplitude of mode 7 is relatively low and could be considered as numerical noise, I believe it prevents drawing an actual conclusion.


<figure style="margin: 1.5em 0;">
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em; width: 100%;">
    <div style="position: relative;">
      <div id="mol-v006" style="height: 400px; position: relative; "></div>
      <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: 10; cursor: default;"></div>
    </div>
    <div style="position: relative;">
      <div id="mol-v007" style="height: 400px; position: relative; "></div>
      <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: 10; cursor: default;"></div>
    </div>
  </div>
  <figcaption style="
    display: block;
    width: 100%;
    text-align: center;
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
    Figure 3: v006 (left) and v007 (right) of a HNA dimer with a B-type helical backbone and nucleobases in equatorial conformation after optimization at ωB97X-D3/MA-Def2-SVP level of theory.
  </figcaption>
</figure>

## Goal of this post

The goal of this post is rather simple: complete the analysis of B-type helical HNA (or at least produce viable results). I will do this by focusing on two points:
1. optimize the structure of three hexamers in a duplex: HNA in A-type helical conformation (hh-A), HNA in B-type helical conformation (hh-B), and HNA-DNA in B-type helical conformation (hd-B). The first two allow to compare the electronic energy of HNA in both conformations.
2. analyze the nucleobase interactions in the three hexamers through local energy decomposition (LED) analysis. This will allow to interpret difference in hydrogen bonding (H-bonding) strength and compare stacking interactions in the three different hexamers.

## Methods

### Simulated systems

<p>Four double-stranded trinucleotide duplexes (hexamers) were constructed and analyzed, differing in sugar scaffold identity and/or helical conformation (Table 1).</p>
<div style="display: flex; align-items: flex-end; gap: 1.5em; margin-bottom: 1em;">
  <p style="flex: 1; margin: 0;">The HNA strand in hd-B occupies the template position, directly mirroring the interaction geometry observed crystallographically in PDB 9EMI. The dd-B system serves as a canonical B-type DNA reference against which the HNA-containing duplexes can be compared. All four systems carry a net charge of −4 (fully deprotonated phosphate groups, neutral nucleobases).</p>
  <div style="flex-shrink: 0; max-width: 420px;">
    <table style="border-collapse: collapse; font-size: 0.85em; width: 100%;">
      <caption style="font-family:'Palatino linotype'; font-style:italic; font-size:0.95em; color:#555; padding-bottom:6px; text-align:left;">
        Table 1: Simulated duplex systems.
      </caption>
      <thead>
        <tr style="background:#f2f2f2;">
          <th style="border:1px solid #ccc; padding:5px 8px;">System</th>
          <th style="border:1px solid #ccc; padding:5px 8px;">Strand 1 (5′→3′)</th>
          <th style="border:1px solid #ccc; padding:5px 8px;">Strand 2 (3′→5′)</th>
          <th style="border:1px solid #ccc; padding:5px 8px;">Helix type</th>
        </tr>
      </thead>
      <tbody>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">hh-A</td><td style="border:1px solid #ccc; padding:4px 8px;">HNA: T–G–T</td><td style="border:1px solid #ccc; padding:4px 8px;">HNA: A–C–A</td><td style="border:1px solid #ccc; padding:4px 8px;">A-type</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">hh-B</td><td style="border:1px solid #ccc; padding:4px 8px;">HNA: T–G–T</td><td style="border:1px solid #ccc; padding:4px 8px;">HNA: A–C–A</td><td style="border:1px solid #ccc; padding:4px 8px;">B-type</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">hd-B</td><td style="border:1px solid #ccc; padding:4px 8px;">HNA: T–G–T</td><td style="border:1px solid #ccc; padding:4px 8px;">DNA: A–C–A</td><td style="border:1px solid #ccc; padding:4px 8px;">B-type</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">dd-B</td><td style="border:1px solid #ccc; padding:4px 8px;">DNA: T–G–T</td><td style="border:1px solid #ccc; padding:4px 8px;">DNA: A–C–A</td><td style="border:1px solid #ccc; padding:4px 8px;">B-type</td></tr>
      </tbody>
    </table>
  </div>
</div>

### System construction

Initial structures were built with LEAP ([AmberTools 25](https://ambermd.org/GetAmber.php)) using the custom HNA residue library and force field parameter set from my PhD research. Starting coordinates were assembled by imposing characteristic A-type (hh-A)or B-type (hh-B, hd-B, dd-B) backbone dihedral angles on the hexitol or deoxyribose backbone. Watson–Crick base pairing was enforced throughout construction. Each system was energy-minimized with PMEMD using a flat-bottom harmonic restraint potential.

### Restrained and unrestrained GFN2-xTB pre-optimization

PMEMD-minimized structures were re-optimized at the GFN2-xTB/ALPB(water) level using [xTB](https://github.com/grimme-lab/xtb) 6.7.1 via the [Cuby4](http://cuby4.molecular.cz) interface in two sequential stages. First, the same restraint scheme applied in the PMEMD stage was retained to prevent collapse of the target conformation during initial semiempirical relaxation. Second, the restraints were removed and a fully unrestrained geometry optimization was performed to allow the structures to relax to their nearest local minimum on the GFN2-xTB potential energy surface.

### Final geometry optimization and frequency analysis with ORCA

Full geometry optimizations followed by harmonic frequency calculations were carried out with [ORCA](https://www.faccts.de/orca/) 6.1.0 at GFN2-xTB/ALPB(water) level of theory.

To confirm that each optimized structure corresponds to a true energy minimum and not a saddle point, the frequency output was inspected for imaginary frequencies. The optimization was performed until the frequency calculation yielded exclusively real frequencies. All four systems converged to true minima within the first iteration.

### Local energy decomposition analysis

Nucleobase interaction energies within each duplex were analyzed by local energy decomposition (LED) using DLPNO-CCSD/def2-SVP in ORCA 6.1.0. LED decomposes the pair interaction energy between fragment pairs into electrostatic, exchange, dispersion, and charge-transfer contributions, allowing a direct comparison of hydrogen bonding strength and $\pi$-stacking interactions across the four systems. Results are presented in a separate section. LED calculations were analyzed using [LEDAW](https://github.com/ahmetaltunfatih/LEDAW) for fragment pair (fp-LED) analysis. [CovaLED](https://pubs.acs.org/doi/10.1021/acscentsci.6c00336) approach was employed to be able to assign individual residues as fragments. 

## Results 

### Structural comparison of the four duplexes

The four optimized duplexes differ in their three-dimensional structure. A global view of each structure is shown in Figure 4. HNA residues are rendered in orange and DNA residues in blue; this coloring makes strand identification easier in the mixed hd-B system.

<figure style="margin: 1.5em 0;">
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75em; width: 100%;">

    <div style="position: relative;">
      <div id="mol-hhA" style="height: 380px; position: relative;"></div>
      <div style="position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.55); color: #fff; padding: 2px 9px; font-size: 0.82em; border-radius: 4px; letter-spacing: 0.03em;">hh-A</div>
    </div>

    <div style="position: relative;">
      <div id="mol-hhB" style="height: 380px; position: relative;"></div>
      <div style="position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.55); color: #fff; padding: 2px 9px; font-size: 0.82em; border-radius: 4px; letter-spacing: 0.03em;">hh-B</div>
    </div>

    <div style="position: relative;">
      <div id="mol-hdB" style="height: 380px; position: relative;"></div>
      <div style="position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.55); color: #fff; padding: 2px 9px; font-size: 0.82em; border-radius: 4px; letter-spacing: 0.03em;">hd-B</div>
    </div>

    <div style="position: relative;">
      <div id="mol-ddB" style="height: 380px; position: relative;"></div>
      <div style="position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.55); color: #fff; padding: 2px 9px; font-size: 0.82em; border-radius: 4px; letter-spacing: 0.03em;">dd-B</div>
    </div>

  </div>

  <div style="display: flex; justify-content: center; gap: 1.5em; margin-top: 0.6em; font-size: 0.82em; color: #555;">
    <span><span style="display:inline-block; width:12px; height:12px; background:#E07B39; border-radius:2px; margin-right:4px; vertical-align:middle;"></span>HNA residues</span>
    <span><span style="display:inline-block; width:12px; height:12px; background:#4A90D9; border-radius:2px; margin-right:4px; vertical-align:middle;"></span>DNA residues</span>
  </div>

  <figcaption style="
    display: block;
    width: 100%;
    text-align: center;
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
    Figure 4: GFN2-xTB/ALPB(water) optimized geometries of the four duplexes. Top row: hh-A (HNA/HNA A-type, left) and hh-B (HNA/HNA B-type, right). Bottom row: hd-B (HNA template / DNA primer B-type, left) and dd-B (DNA/DNA B-type, right). HNA residues are colored orange; DNA residues are colored blue.
  </figcaption>
</figure>

#### Backbone dihedrals

The HNA backbone differs topologically from the DNA backbone because the five-membered deoxyribose ring is replaced by a six-membered hexitol ring bearing an additional methylene group (C6′). Table 2 lists the topology of each dihedral.
<div style="display: flex; align-items: flex-end; gap: 1.5em; margin-bottom: 1em;">
  <p style="flex: 1; margin: 0;">The inter-nucleotide chain therefore reads O4′(n−1)–P–O6′–C6′–C5′–C4′–O4′–P(n+1), with O4′ as the 3′-linking oxygen and O6′ as the 5′-linking oxygen. This introduces one extra dihedral (γ: O6′–C6′–C5′–C4′) relative to DNA. All torsion angles were extracted directly from the GFN2-xTB/ALPB(water) optimized geometries.</p>
  <div style="flex-shrink: 0;">
    <table style="border-collapse: collapse; font-size: 0.85em; width: 100%;">
      <caption style="font-family:'Palatino linotype'; font-style:italic; font-size:0.95em; color:#555; padding-bottom:6px; text-align:left;">
        Table 2: Dihedral angle definitions.
      </caption>
      <thead>
        <tr style="background:#f2f2f2;">
          <th style="border:1px solid #ccc; padding:5px 8px;">Angle</th>
          <th style="border:1px solid #ccc; padding:5px 8px;">Atoms (HNA)</th>
          <th style="border:1px solid #ccc; padding:5px 8px;">Atoms (DNA)</th>
        </tr>
      </thead>
      <tbody>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">α</td><td style="border:1px solid #ccc; padding:4px 8px;">O4′(n−1)–P–O6′–C6′</td><td style="border:1px solid #ccc; padding:4px 8px;">O3′(n−1)–P–O5′–C5′</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">β</td><td style="border:1px solid #ccc; padding:4px 8px;">P–O6′–C6′–C5′</td><td style="border:1px solid #ccc; padding:4px 8px;">P–O5′–C5′–C4′</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">γ</td><td style="border:1px solid #ccc; padding:4px 8px;">O6′–C6′–C5′–C4′</td><td style="border:1px solid #ccc; padding:4px 8px;">O5′–C5′–C4′–C3′</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">δ</td><td style="border:1px solid #ccc; padding:4px 8px;">C6′–C5′–C4′–O4′</td><td style="border:1px solid #ccc; padding:4px 8px;">C5′–C4′–C3′–O3′</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">ε</td><td style="border:1px solid #ccc; padding:4px 8px;">C5′–C4′–O4′–P(n+1)</td><td style="border:1px solid #ccc; padding:4px 8px;">C4′–C3′–O3′–P(n+1)</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">ζ</td><td style="border:1px solid #ccc; padding:4px 8px;">C4′–O4′–P(n+1)–O6′(n+1)</td><td style="border:1px solid #ccc; padding:4px 8px;">C3′–O3′–P(n+1)–O5′(n+1)</td></tr>
        <tr><td style="border:1px solid #ccc; padding:4px 8px;">χ</td><td style="border:1px solid #ccc; padding:4px 8px;">C1′–C2′–N1/N9–C2/C4</td><td style="border:1px solid #ccc; padding:4px 8px;">O4′–C1′–N1/N9–C2/C4</td></tr>
      </tbody>
    </table>
  </div>
</div>

Computed values for all residues are given in Table 3. Terminal residues lack α (no preceding P) or ε/ζ (no following P) and are marked "—".

<div style="overflow-x: auto; margin: 1em 0;">
<table style="border-collapse: collapse; width: 100%; font-size: 0.82em;">
  <caption style="font-family:'Palatino linotype'; font-style:italic; font-size:0.95em; color:#555; padding-bottom:6px; text-align:left;">
    Table 3: Backbone dihedral angles (degrees) from GFN2-xTB/ALPB(water) optimized structures. Shading separates the two strands within each duplex; Type identifies the sugar scaffold.
  </caption>
  <thead>
    <tr style="background:#f2f2f2;">
      <th style="border:1px solid #ccc; padding:5px 8px;">System</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Type</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Res</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Name</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">α</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">β</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">γ</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">δ</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">ε</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">ζ</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">χ</th>
    </tr>
  </thead>
  <tbody>
    <!-- hh-A -->
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">hh-A</td>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">HNA</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HT5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+80.8</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+65.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−143.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−77.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−149.9</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HG</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−70.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+166.8</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+65.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+64.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−123.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−88.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−154.0</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HT3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−61.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+152.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+66.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+69.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−146.5</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HA5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+77.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+63.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−144.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−78.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−152.2</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HC</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−69.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+166.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+65.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+68.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−126.8</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−81.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−149.6</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HA3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−63.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+157.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+67.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+65.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−151.9</td>
    </tr>
    <!-- hh-B -->
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">hh-B</td>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">HNA</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HT5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+48.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+147.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+108.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−72.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−69.2</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HG</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−100.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−104.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+52.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+151.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+111.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−71.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−75.3</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HT3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−95.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−113.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+57.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+157.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−86.7</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HA5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+48.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+146.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+98.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−62.8</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−61.1</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HC</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−103.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−113.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+61.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+162.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−142.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−172.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−88.0</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HA3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−57.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+141.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+41.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+155.8</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−119.8</td>
    </tr>
    <!-- hd-B -->
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">hd-B</td>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="3">HNA</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HT5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+56.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+159.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−62.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−149.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−109.1</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HG</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−123.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+136.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+44.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+153.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−137.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−169.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−109.2</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">HT3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−54.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+142.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+43.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+155.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−118.4</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="3">DNA</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DA5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+69.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+139.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−172.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−85.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−105.2</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DC</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−64.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+166.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+53.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+108.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+118.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−61.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−114.9</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DA3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−101.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−104.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+53.8</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+139.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−96.0</td>
    </tr>
    <!-- dd-B -->
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">dd-B</td>
      <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">DNA</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DT5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+57.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+109.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+89.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−53.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−71.1</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DG</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−106.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−104.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+63.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+142.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+86.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−58.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−73.5</td>
    </tr>
    <tr>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DT3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−112.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−101.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+58.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+95.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−102.2</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DA5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+63.4</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+133.9</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−178.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−88.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−97.9</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DC</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−66.8</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+167.1</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+52.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+82.5</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−165.7</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−87.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−130.7</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td>
      <td style="border:1px solid #ccc; padding:4px 8px;">DA3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−67.3</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+163.2</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+57.0</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+89.6</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">—</td>
      <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−125.1</td>
    </tr>
  </tbody>
</table>
</div>

The most prominent backbone differences between HNA A-type and HNA B-type emerge from three torsions. The β angle (P–O6′–C6′–C5′) shifts from anti (≈ +167°) in hh-A to gauche− (≈ −108°) in hh-B. The δ angle (C6′–C5′–C4′–O4′) shifts from gauche+ (≈ +65°) in hh-A to positive anti (≈ +152°) in hh-B. The ε angle (C5′–C4′–O4′–P) shifts from negative trans (≈ −133°) in hh-A to gauche+ (≈ +105°) in hh-B. These three correlated changes in β, δ, and ε collectively report the flip of the hexitol ring between the $^{4′}C_{1′}$ and $^{1′}C_{4′}$ chairs. The α angle (O4′(n−1)–P–O6′–C6′) stays in the gauche− domain (≈ −60° to −70°) in hh-A and shifts to a broader range (≈ −58° to −103°) in hh-B, while the γ angle (O6′–C6′–C5′–C4′) remains gauche+ (≈ +42° to +81°) in all HNA systems and therefore does not alone discriminate between the two helical types. The glycosidic angle χ (C1′–C2′–N1/N9–C2/C4) is consistently anti in hh-A (≈ −147° to −154°) and shifts toward the high-anti to borderline syn range in hh-B (≈ −61° to −120°), consistent with the nucleobase moving from an axial to an equatorial orientation on the hexitol ring.

The hd-B HNA template strand shows δ values of +153° to +159° and γ values of +44° to +56°, consistent with ¹$^{1′}C_{4′}$ geometry, while β (≈ +136° to +143°) and ε (≈ −63° to −137°) lie between the hh-A and hh-B extremes. The different ε/ζ combinations indicate that multiple low-lying combinations are present on the PES for the B-type helical shape. The DNA χ values in hd-B and dd-B fall in the range −71° to −131°, which is consistent with canonical B-type DNA glycosidic geometry.

#### Sugar and ring puckering

For DNA, sugar conformation is described by the pseudorotation phase angle $P$: canonical B-type DNA adopts C2′-endo ($P \approx 162°$, south), while A-type DNA adopts C3′-endo ($P \approx 18°$, north). For HNA, the six-membered hexitol ring by a pseudorotational sphere (Q, θ, φ), where the polar angle θ distinguishes the two chair forms: θ ≈ 0° corresponds to $^{4′}C_{1′}$ (nucleobase axial) and θ ≈ 180° corresponds to $^{1′}C_{4′}$ (nucleobase equatorial).

Computed puckering parameters for all residues are given in Tables 4 and 5.

<div style="overflow-x: auto; margin: 1em 0;">
<table style="border-collapse: collapse; width: 100%; font-size: 0.82em;">
  <caption style="font-family:'Palatino linotype'; font-style:italic; font-size:0.95em; color:#555; padding-bottom:6px; text-align:left;">
    Table 4: HNA hexitol ring torsions (τ₀–τ₅, degrees) and Cremer–Pople puckering parameters. Ring atom order: O′–C1′–C2′–C3′–C4′–C5′.
  </caption>
  <thead>
    <tr style="background:#f2f2f2;">
      <th style="border:1px solid #ccc; padding:5px 8px;">System</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Res</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Name</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">τ₀</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">τ₁</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">τ₂</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">τ₃</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">τ₄</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">τ₅</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">Q (Å)</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">θ (°)</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Conf.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">hh-A</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td><td style="border:1px solid #ccc; padding:4px 8px;">HT5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−54.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+50.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−51.8</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+54.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−55.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+55.9</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.538</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">4.7</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>⁴′C₁′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td><td style="border:1px solid #ccc; padding:4px 8px;">HG</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−53.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+53.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−55.1</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+56.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−55.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+54.2</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.550</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">6.2</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>⁴′C₁′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td><td style="border:1px solid #ccc; padding:4px 8px;">HT3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−56.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+52.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−51.2</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+51.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−51.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+54.8</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.525</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">1.9</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>⁴′C₁′</b></td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td><td style="border:1px solid #ccc; padding:4px 8px;">HA5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−56.6</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+52.1</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−52.5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+55.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−57.2</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+58.2</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.555</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">4.3</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>⁴′C₁′</b></td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td><td style="border:1px solid #ccc; padding:4px 8px;">HC</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−50.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+52.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−55.9</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+56.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−52.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+49.4</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.535</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">9.7</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>⁴′C₁′</b></td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td><td style="border:1px solid #ccc; padding:4px 8px;">HA3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−58.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+53.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−51.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+51.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−54.2</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+58.1</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.544</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.4</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>⁴′C₁′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px;" rowspan="6">hh-B</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td><td style="border:1px solid #ccc; padding:4px 8px;">HT5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+61.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−61.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+55.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−48.6</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+45.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−52.5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.550</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">169.3</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td><td style="border:1px solid #ccc; padding:4px 8px;">HG</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+59.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−53.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+46.4</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−44.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+48.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−57.5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.510</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">173.3</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td><td style="border:1px solid #ccc; padding:4px 8px;">HT3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+58.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−52.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+46.8</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−46.6</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+50.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−57.4</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.513</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">176.1</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td><td style="border:1px solid #ccc; padding:4px 8px;">HA5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+61.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−61.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+54.7</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−46.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+44.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−52.3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.542</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">168.6</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td><td style="border:1px solid #ccc; padding:4px 8px;">HC</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+57.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−56.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+53.8</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−52.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+51.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−54.3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.541</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">175.9</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td><td style="border:1px solid #ccc; padding:4px 8px;">HA3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+61.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−57.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+50.3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−47.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+48.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−57.0</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.534</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">173.8</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px;" rowspan="3">hd-B<br/><small>(HNA)</small></td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td><td style="border:1px solid #ccc; padding:4px 8px;">HT5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+56.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−64.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+64.0</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−56.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+48.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−48.7</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.590</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">165.6</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td><td style="border:1px solid #ccc; padding:4px 8px;">HG</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+59.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−63.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+59.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−50.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+44.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−49.4</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.563</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">165.9</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td><td style="border:1px solid #ccc; padding:4px 8px;">HT3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+61.2</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−57.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+51.1</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−47.1</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+48.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−56.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">0.536</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">173.6</td><td style="border:1px solid #ccc; padding:4px 8px;"><b>¹′C₄′</b></td></tr>
  </tbody>
</table>
</div>

<div style="overflow-x: auto; margin: 1em 0;">
<table style="border-collapse: collapse; width: 100%; font-size: 0.82em;">
  <caption style="font-family:'Palatino linotype'; font-style:italic; font-size:0.95em; color:#555; padding-bottom:6px; text-align:left;">
    Table 5: DNA furanose ring torsions (ν₀–ν₄, degrees) and Altona–Sundaralingam pseudorotation parameters. Ring atom order: O4′–C1′–C2′–C3′–C4′.
  </caption>
  <thead>
    <tr style="background:#f2f2f2;">
      <th style="border:1px solid #ccc; padding:5px 8px;">System</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Res</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Name</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">ν₀</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">ν₁</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">ν₂</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">ν₃</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">ν₄</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">P (°)</th>
      <th style="border:1px solid #ccc; padding:5px 8px; text-align:right;">τmax (°)</th>
      <th style="border:1px solid #ccc; padding:5px 8px;">Pucker</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="border:1px solid #ccc; padding:4px 8px;" rowspan="3">hd-B<br/><small>(DNA)</small></td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td><td style="border:1px solid #ccc; padding:4px 8px;">DA5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−22.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+33.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−31.1</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+18.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+2.3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+157.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">33.7</td><td style="border:1px solid #ccc; padding:4px 8px;">C2′-endo</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td><td style="border:1px solid #ccc; padding:4px 8px;">DC</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−45.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+40.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−21.0</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−4.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+31.3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+117.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">45.0</td><td style="border:1px solid #ccc; padding:4px 8px;">O4′-endo</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td><td style="border:1px solid #ccc; padding:4px 8px;">DA3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+0.2</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+14.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−22.0</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+22.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−14.9</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−160.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">23.3</td><td style="border:1px solid #ccc; padding:4px 8px;">C2′-endo</td></tr>
    <tr style="background:#fafafa;">
        <td style="border:1px solid #ccc; padding:4px 8px;" rowspan="3">dd-B<br/><small>(S1)</small></td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">1</td><td style="border:1px solid #ccc; padding:4px 8px;">DT5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−43.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+38.1</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−19.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−4.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+29.8</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+117.6</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">42.4</td><td style="border:1px solid #ccc; padding:4px 8px;">O4′-endo</td></tr>
    <tr style="background:#fafafa;">
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">2</td><td style="border:1px solid #ccc; padding:4px 8px;">DG</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−4.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+21.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−28.9</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+27.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−14.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−169.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">29.3</td><td style="border:1px solid #ccc; padding:4px 8px;">C2′-endo</td></tr>
    <tr style="background:#fafafa;">
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">3</td><td style="border:1px solid #ccc; padding:4px 8px;">DT3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+0.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−13.8</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+20.7</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−21.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+13.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+18.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">21.8</td><td style="border:1px solid #ccc; padding:4px 8px;">C3′-endo</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px;" rowspan="3">dd-B<br/><small>(S2)</small></td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">4</td><td style="border:1px solid #ccc; padding:4px 8px;">DA5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−25.2</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+32.7</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−27.7</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+14.1</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+6.9</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+149.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">32.3</td><td style="border:1px solid #ccc; padding:4px 8px;">C2′-endo</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">5</td><td style="border:1px solid #ccc; padding:4px 8px;">DC</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−29.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+7.0</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+15.5</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−33.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+39.6</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+66.4</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">38.8</td><td style="border:1px solid #ccc; padding:4px 8px;">C4′-exo</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 8px; text-align:center;">6</td><td style="border:1px solid #ccc; padding:4px 8px;">DA3</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+5.5</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−22.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+28.9</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">−26.9</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+13.9</td>
        <td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">+8.3</td><td style="border:1px solid #ccc; padding:4px 8px; text-align:right;">29.2</td><td style="border:1px solid #ccc; padding:4px 8px;">C3′-endo</td></tr>
  </tbody>
</table>
</div>

The analysis cleanly separates the two HNA chair forms across all systems. In hh-A, all six hexitol rings give θ in the range 0.4°–9.7°, confirming exclusive $^{4′}C_{1′}$ character with a total puckering amplitude Q ≈ 0.53-0.55 Å. In hh-B, all six residues give θ = 169°–176°, confirming exclusive $^{1′}C_{4′}$ character with a comparable Q ≈ 0.51–0.55 Å. The near-identical Q values indicate that the ring is equally rigid in both chair forms; the conformational change is a pure inversion of the chair geometry rather than a flattening of the ring. In the hd-B HNA template strand, θ ranges from 165.6° to 173.6°, confirming retention of the $^{1′}C_{4′}$ chair despite the changed chemical environment of pairing with a DNA complement.

For the DNA residues, the picture is more nuanced. The range of puckering amplitudes (τmax ≈ 23–45°) is larger than the range of puckering amplitudes of the HNA rings, reflecting the greater conformational flexibility of the five-membered furanose. In hd-B, the DNA primer strand shows C2′-endo character for DA5 ($P$ = +157.4°) and O4′-endo for the internal DC ($P$ = +117.8°), with DA3 at $P$ = −160.7° (south, C2′-endo). C2′-endo is the canonical B-type sugar pucker, so the DNA complement of the HNA template does largely retain its expected B-type geometry. In dd-B, the puckering is more dispersed: the internal residues DG (strand 1, $P$ = −169.9°) and DA5 (strand 2, $P$ = +149.3°) are C2′-endo, while the terminal and internal pyrimidines adopt O4′-endo (DT5, $P$ = +117.6°; DC strand 2, $P$ = +66.4° → C4′-exo) or C3′-endo (DT3, $P$ = +18.0°; DA3 strand 2, $P$ = +8.3°) conformations. The dispersion across the pseudorotation wheel reflects the shallow furanose potential energy surface and the dominance of terminal effects in a short gas-phase-optimized trinucleotide, where the cooperative helical environment of a longer duplex is absent.

### Local energy decomposition analysis of base-pairing and stacking

Pairwise interaction energies between all six nucleotide fragments were decomposed using fragment-pair LED (fp-LED) at the DLPNO-CCSD level. Each nucleotide (base + sugar + phosphate) is treated as one fragment, numbered 1–6 (strand 1: T1–G2–T3 in the 5′→3′ direction; strand 2: A4–C5–A6 in the 5′→3′ direction). Watson–Crick-Franklin (WCF) base pairs form between complementary positions across strands: T1·A6 at pair (1,6), G2·C5 at (2,5), and T3·A4 at (3,4). 

#### Watson–Crick-Franklin hydrogen bonding

The LED components for all three Watson–Crick-Franklin pairs are tabulated below (kcal/mol). Electrostat and Exchange are the primary indicators of hydrogen bond strength; C-CCSD captures induction and higher-order correlation.

<div style="overflow-x: auto; margin: 1em 0;">
<table style="border-collapse: collapse; width: 100%; font-size: 0.85em;">
  <thead>
    <tr style="background:#f2f2f2;">
      <th style="border:1px solid #ccc; padding:5px 9px;">Pair</th>
      <th style="border:1px solid #ccc; padding:5px 9px;">System</th>
      <th style="border:1px solid #ccc; padding:5px 9px; text-align:right;">Electrostat</th>
      <th style="border:1px solid #ccc; padding:5px 9px; text-align:right;">Exchange</th>
      <th style="border:1px solid #ccc; padding:5px 9px; text-align:right;">Dispersion</th>
      <th style="border:1px solid #ccc; padding:5px 9px; text-align:right;">C-CCSD</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="border:1px solid #ccc; padding:4px 9px;" rowspan="4">T1·A6<br/><small>(1,6)</small></td>
        <td style="border:1px solid #ccc; padding:4px 9px;">hh-A</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−108.2</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−17.8</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−5.9</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−5.8</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 9px;">hh-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−107.0</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−17.8</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−6.0</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−4.3</td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 9px;">hd-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−115.5</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−19.3</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−6.3</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−4.5</td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 9px;">dd-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−111.8</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−18.6</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−6.0</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−1.1</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 9px;" rowspan="4"><b>G2·C5</b><br/><small>(2,5)</small></td>
        <td style="border:1px solid #ccc; padding:4px 9px;">hh-A</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;"><b>−153.4</b></td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;"><b>−24.1</b></td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−7.3</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−5.1</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 9px;">hh-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;"><b>−150.9</b></td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;"><b>−23.9</b></td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−7.3</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−4.5</td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 9px;">hd-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−140.3</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−21.6</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−6.8</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−5.1</td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 9px;">dd-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−141.4</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−22.0</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−6.9</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−1.8</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 9px;" rowspan="4">T3·A4<br/><small>(3,4)</small></td>
        <td style="border:1px solid #ccc; padding:4px 9px;">hh-A</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−116.6</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−18.8</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−6.0</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−1.5</td></tr>
    <tr><td style="border:1px solid #ccc; padding:4px 9px;">hh-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−113.1</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−18.6</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−5.9</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−2.6</td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 9px;">hd-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−118.0</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−19.1</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−6.0</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−3.1</td></tr>
    <tr style="background:#fafafa;"><td style="border:1px solid #ccc; padding:4px 9px;">dd-B</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−114.6</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−18.6</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−5.9</td>
        <td style="border:1px solid #ccc; padding:4px 9px; text-align:right;">−3.4</td></tr>
  </tbody>
</table>
</div>

The three base pairs show qualitatively distinct patterns that must be considered separately.

**G–C pair (2,5).** The HNA duplexes stand out clearly: electrostatics are ~12 kcal/mol more negative (hh-A: −153.4, hh-B: −150.9) than in the DNA-containing systems (hd-B: −140.3, dd-B: −141.4), and exchange follows the same trend. This enhancement is independent of helical type: both A-type and B-type HNA give near-identical values, identifying it as an intrinsic property of the hexitol scaffold. Dispersion is essentially constant across all four systems (≈ −7 kcal/mol).

**T–A pairs (1,6) and (3,4).** The T–A electrostatics show no systematic HNA advantage. For T1·A6 the order is hd-B (−115.5) < dd-B (−111.8) < hh-A (−108.2) < hh-B (−107.0); for T3·A4 it is hd-B (−118.0) < hh-A (−116.6) < dd-B (−114.6) < hh-B (−113.1). The total spread is only ~5–8 kcal/mol in both cases, compared to ~12 kcal/mol for G–C. The mixed hd-B duplex, where an HNA thymine faces a DNA adenine, is consistently the strongest T–A pair, suggesting a more optimal cross-scaffold H-bond geometry. Exchange and dispersion are effectively constant across systems for both T–A pairs, providing no additional discrimination.

The C-CCSD term (non-dispersive part; accounts for other correlated contributions) reveals an additional asymmetry. For T1·A6, it mirrors the G–C trend: strongest in hh-A (−5.8), weakest in dd-B (−1.1). For T3·A4 the ordering is **reversed**: dd-B (−3.4) < hd-B (−3.1) < hh-B (−2.6) < hh-A (−1.5). This positional reversal likely reflects the different flanking environments of the two terminal base pairs within the sequence: T1 is the 5′-terminal residue with the G–C pair immediately on its 3′ side, while T3 is the 3′-terminal residue with the G–C pair on its 5′ side, and sequence-dependent polarisation acts asymmetrically in the two directions.

Taken together, the data show that the HNA scaffold selectively strengthens G–C Watson–Crick hydrogen bonding while leaving T–A bonding essentially unchanged relative to DNA (at least as terminal base pairs). 

#### Nucleobase stacking

Nucleobase stacking interactions between adjacent base-pair steps are characterized by the dispersion and exchange components between nucleobases. The fp-LED dispersion heat maps for all four systems are shown in Figure 5; the colour scale runs from white (zero) through blue (stabilising dispersion), with deeper blue indicating stronger London interaction. The dominant stacking interaction in this sequence is between G2 and A6, which spans the T1·A6 / G2·C5 base-pair step.

<figure style="margin: 1.5em 0;">
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5em; width: 100%;">
    <div style="position: relative;">
      <img src="{{ '/assets/content/compchem/HNAgeometries/led_disp_hhA.png' | relative_url }}"
           alt="fp-LED dispersion hh-A" style="width:100%; height:auto; display:block;">
      <div style="position:absolute; top:6px; left:6px; background:rgba(0,0,0,0.55); color:#fff; padding:2px 8px; font-size:0.82em; border-radius:4px;">hh-A</div>
    </div>
    <div style="position: relative;">
      <img src="{{ '/assets/content/compchem/HNAgeometries/led_disp_hhB.png' | relative_url }}"
           alt="fp-LED dispersion hh-B" style="width:100%; height:auto; display:block;">
      <div style="position:absolute; top:6px; left:6px; background:rgba(0,0,0,0.55); color:#fff; padding:2px 8px; font-size:0.82em; border-radius:4px;">hh-B</div>
    </div>
    <div style="position: relative;">
      <img src="{{ '/assets/content/compchem/HNAgeometries/led_disp_hdB.png' | relative_url }}"
           alt="fp-LED dispersion hd-B" style="width:100%; height:auto; display:block;">
      <div style="position:absolute; top:6px; left:6px; background:rgba(0,0,0,0.55); color:#fff; padding:2px 8px; font-size:0.82em; border-radius:4px;">hd-B</div>
    </div>
    <div style="position: relative;">
      <img src="{{ '/assets/content/compchem/HNAgeometries/led_disp_ddB.png' | relative_url }}"
           alt="fp-LED dispersion dd-B" style="width:100%; height:auto; display:block;">
      <div style="position:absolute; top:6px; left:6px; background:rgba(0,0,0,0.55); color:#fff; padding:2px 8px; font-size:0.82em; border-radius:4px;">dd-B</div>
    </div>
  </div>
  <figcaption style="
    display: block;
    width: 100%;
    text-align: center;
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
    Figure 5: fp-LED CCSD dispersion interaction matrices (kcal/mol) for the four duplexes. Deeper blue indicates stronger (more negative) dispersion interactions. Row and column labels identify each nucleotide fragment; WC base pairs lie on the anti-diagonal (e.g. HG2·HC5, HT33·HA54, HT51·HA36). The strongly coloured cell at HG2·HA36 in hh-A reflects the dominant cross-strand G2·A6 stacking interaction characteristic of A-type helices.
  </figcaption>
</figure>

The most striking feature across the four maps is the progressive lightening of the G2·A6 (HG2·HA36) cell from deep blue in hh-A to near-white in dd-B, quantified in the table below alongside the opposing 5′–5′ face contacts:

| System | Disp (G2·A6) | Exch (G2·A6) | Disp (G2·A4) | Disp (T1·C5) | Disp (T3·C5) |
|--------|-------------:|-------------:|-------------:|-------------:|-------------:|
| hh-A   | −12.0        | −9.9         | −0.3         | −0.05        | −2.7         |
| hh-B   | −6.7         | −5.2         | −0.8         | −0.2         | −0.7         |
| hd-B   | −8.7         | −6.7         | −1.9         | −0.3         | −0.5         |
| dd-B   | −3.0         | −1.7         | −2.8         | −1.0         | −0.4         |

The G2·A6 cross-strand dispersion is **four-fold stronger in hh-A (−12.0 kcal/mol) than in dd-B (−3.0 kcal/mol)**. The exchange at this pair (hh-A: −9.9, dd-B: −1.7) confirms that G2 and A6 are in considerably closer van der Waals contact in the A-type helix. Conversely, the G2·A4 (2,4) and T1·C5 (1,5) cross-strand contacts — on the 5′–5′ face of the same step — are weakest in hh-A and increase monotonically toward dd-B. This is a direct geometric consequence of helical type: A-type helices have a large negative X-displacement that brings the 3′–3′ face into close contact, while B-type helices redistribute the stacking overlap to the 5′–5′ face. hh-B is consistently intermediate between hh-A and dd-B, as expected for an HNA duplex in B-type conformation.

Comparing hh-A to hh-B in isolation reveals the energetic cost of the $^{4′}C_{1′}$ → $^{1′}C_{4′}$ hexitol chair inversion at constant sequence and scaffold: G2·A6 dispersion weakens by ~5 kcal/mol, while the G–C electrostatics change by less than 2.5 kcal/mol. The **energetic cost of the A→B conformational switch in HNA is therefore primarily borne by nucleobase stacking, not by Watson–Crick-Franklin hydrogen bonding** (in addition to the energy cost for the flip in sugar pucker).

For the mixed hd-B system, the G2·A6 dispersion (−8.7 kcal/mol) is intermediate between hh-B (−6.7) and hh-A (−12.0), suggesting the HNA template partially preserves A-type cross-strand overlap even in a B-type helical context. The G–C electrostatics in hd-B (−140.3 kcal/mol) are markedly closer to dd-B (−141.4 kcal/mol) than to hh-B (−150.9 kcal/mol), indicating that the intrinsic HNA G–C H-bond strengthening is partly attenuated when the cytosine partner is DNA rather than HNA.

<!-- running scripts -->

<script>
(function() {
  var viewer = $3Dmol.createViewer("mol-9EMI", {
    backgroundColor: "white"
  });

  $3Dmol.download("pdb:9EMI", viewer, {}, function() {

    // Clear all styles first
    viewer.setStyle({}, {});

    // Protein: cartoon ribbon, tan color
    viewer.setStyle(
      { resn: ["ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS",
               "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
               "TYR","VAL"] },
      { cartoon: { color: "#d2b48c" } }
    );

    // Nucleic acids: stick with element color scheme
    // but carbon overridden to tan, everything else by element
    viewer.setStyle(
      { resn: ["A","U","G","C","DA","DT","DG","DC"] },
      { stick: {
          // radius: 0.2,
          colorscheme: {
            prop: "elem",
            map: {
              "C": "#d2b48c",
            //   "O": "#ff2200",
            //   "N": "#4444ff",
            //   "P": "#ff8800",
            //   "S": "#ffff00",
            //   "H": "#ffffff"
            }
          }
      }}
    );

    // Focus residues 4.T, 5.T, 6.T: same stick style but highlighted
    [4, 5, 6].forEach(function(resi) {
      viewer.setStyle(
        { resi: resi, chain: "T" },
        { stick: {
            radius: 0.35,
            colorscheme: {
              prop: "elem",
              map: {
                "C": "#ffcc00",   // yellow carbon to distinguish focus residues
              //   "O": "#ff2200",
              //   "N": "#4444ff",
              //   "P": "#ff8800",
              //   "S": "#ffff00",
              //   "H": "#ffffff"
              }
            }
        }}
      );
    });

    // Labels on focus residues
    viewer.addResLabels(
      { resi: [4, 5, 6], chain: "T" },
      { font: "Arial", fontSize: 12, fontColor: "#ffcc00",
        backgroundColor: "black", backgroundOpacity: 0.6 }
    );

    // Zoom to focus residues
    // Zoom to focus residues then rotate for better angle
    viewer.zoomTo({ resi: [4, 5, 6], chain: "T" });
    viewer.rotate(120, "y");   // rotate 90 degrees around Y axis
    viewer.rotate(-45, "z");
    viewer.render();
  });

})();
</script>

<script>
(function() {
  function parseAllFrames(raw) {
    var lines = raw.split('\n');
    var result = [];
    var i = 0;
    while (i < lines.length) {
      while (i < lines.length && lines[i].trim() === '') i++;
      if (i >= lines.length) break;
      var natoms = parseInt(lines[i].trim(), 10);
      if (isNaN(natoms)) break;
      result.push(lines[i]); i++;
      result.push(lines[i] || ''); i++;
      for (var j = 0; j < natoms && i < lines.length; j++, i++) {
        var parts = lines[i].trim().split(/\s+/);
        result.push(parts.slice(0, 4).join('  '));
      }
    }
    return result.join('\n');
  }

  function loadXYZViewer(elementId, xyzUrl) {
    var el = document.getElementById(elementId);
    var w = el.offsetWidth || el.parentElement.offsetWidth;
    var viewer = $3Dmol.createViewer(el, { backgroundColor: "white", width: w, height: 400 });
    var stickStyle = { stick: { radius: 0.15, colorscheme: { prop: "elem", map: { "C": "#d2b48c" }, defaultColor: "Jmol" } } };

    fetch(xyzUrl)
      .then(function(res) { return res.text(); })
      .then(function(data) {
        var models = viewer.addModels(parseAllFrames(data), "xyz");
        var nFrames = models.length;

        // Frame 0 is the equilibrium geometry — skip it, animate frames 1..N-1
        for (var k = 0; k < nFrames; k++) {
          viewer.setStyle({ model: k }, k === 1 ? stickStyle : {});
        }
        viewer.zoomTo();
        viewer.render();

        var frame = 1;
        setInterval(function() {
          viewer.setStyle({ model: frame }, {});
          frame = frame >= nFrames - 2 ? 1 : frame + 1;  // loop frames 1..18, skip equilibrium endpoints
          viewer.setStyle({ model: frame }, stickStyle);
          viewer.render();
        }, 80);
      });
  }

  // Delay until layout is fully computed
  window.addEventListener('load', function() {
    loadXYZViewer("mol-v006", "{{ '/assets/content/compchem/HNAgeometries/2020_BtypeDuplex.hess.v006.xyz' | relative_url }}");
    loadXYZViewer("mol-v007", "{{ '/assets/content/compchem/HNAgeometries/2020_BtypeDuplex.hess.v007.xyz' | relative_url }}");
  });
})();
</script>

<script>
(function() {
  var HNA_resn = ["HT5", "HG", "HT3", "HA5", "HC", "HA3"];
  var DNA_resn = ["DT5", "DG", "DT3", "DA5", "DC", "DA3"];

  function loadDuplexViewer(elementId, pdbUrl) {
    var el = document.getElementById(elementId);
    var viewer = $3Dmol.createViewer(el, { backgroundColor: "white" });

    fetch(pdbUrl)
      .then(function(res) { return res.text(); })
      .then(function(data) {
        viewer.addModel(data, "pdb");
        viewer.setStyle({}, {});
        viewer.setStyle(
          { resn: HNA_resn },
          { stick: { radius: 0.25, colorscheme: { prop: "elem", map: { "C": "#E07B39" }, defaultColor: "Jmol" } } }
        );
        viewer.setStyle(
          { resn: DNA_resn },
          { stick: { radius: 0.25, colorscheme: { prop: "elem", map: { "C": "#4A90D9" }, defaultColor: "Jmol" } } }
        );
        viewer.zoomTo();
        viewer.rotate(90, 'z');
        viewer.render();
      });
  }

  window.addEventListener('load', function() {
    loadDuplexViewer("mol-hhA", "{{ '/assets/content/compchem/HNAgeometries/hhA_opt_iter001.pdb' | relative_url }}");
    loadDuplexViewer("mol-hhB", "{{ '/assets/content/compchem/HNAgeometries/hhB_opt_iter001.pdb' | relative_url }}");
    loadDuplexViewer("mol-hdB", "{{ '/assets/content/compchem/HNAgeometries/hdB_opt_iter001.pdb' | relative_url }}");
    loadDuplexViewer("mol-ddB", "{{ '/assets/content/compchem/HNAgeometries/ddB_opt_iter001.pdb' | relative_url }}");
  });
})();
</script>
