---
title: "The geometry of HNA duplexes"
date: 2027-01-01
layout: single
classes: single
author_profile: false
math: true
molecule: true
sidebar:
  - title: "Disclaimer"
    text: "All files used for visualization or discussion are made available under the respective folder in `/assets/content/compchem` "
published: false
---

## Quicklinks
{:.no_toc}
* TOC
{:toc}

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

**TO DO**

- sequence
- computational methods & software

## Results 

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
