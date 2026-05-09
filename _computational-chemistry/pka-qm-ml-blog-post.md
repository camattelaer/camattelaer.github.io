---
layout: post
title: "Building a QM/ML pKa Calculator: Adventures in Protonation State Population"
date: 2026-04-25
categories: [computational-chemistry, machine-learning, python]
tags: [pKa, GFN2-xTB, ORCA, GPR, protonation, QM/ML]
math: true
---

# Building a QM/ML pKa Calculator: Adventures in Protonation State Population

A molecule's protonation state is rarely a settled question. Depending on the pH of its environment, a drug candidate might carry a positive charge, a negative one, or none at all — and the correct form matters enormously for binding, solubility, permeability, and toxicity. Getting this right computationally is harder than it sounds, and this post chronicles how we built a Python workflow to tackle it, combining quantum mechanical (QM) free energy calculations with a machine learning (ML) calibration layer.

The code is based on the theoretical framework proposed by Pesce, Farr, and de Fabritiis in their 2026 preprint ([arXiv:2604.00841](https://arxiv.org/abs/2604.00841)), part of the AcepKa/Uni-pKa family of methods.

---

## 1. What Is pKa and Why Should You Care?

The acid dissociation constant, $K_a$, quantifies the tendency of a molecule to donate a proton to water:

$$\mathrm{HA} \rightleftharpoons \mathrm{A}^- + \mathrm{H}^+$$

$$K_a = \frac{[\mathrm{A}^-][\mathrm{H}^+]}{[\mathrm{HA}]}$$

In practice, $K_a$ values span many orders of magnitude, so chemists work with $\mathrm{p}K_a = -\log_{10}(K_a)$. A low $\mathrm{p}K_a$ means a strong acid that readily gives up its proton; a high $\mathrm{p}K_a$ means the proton is tightly held.

For a molecule with multiple ionisable sites — think a drug with an amine, a carboxylic acid, and a phenol — there is not one $\mathrm{p}K_a$ but a ladder of them, one for each successive deprotonation step. At any given pH, the molecule exists as a mixture of **microstates** (distinct protonation forms), with each microstate carrying a population that follows a Boltzmann distribution over the accessible free energies. This distribution is what we set out to compute.

In medicinal chemistry, knowing the microstate populations at physiological pH (7.4) is essential for:
- Virtual screening (docking the *correct* ionisation state)
- ADMET prediction (ionised molecules permeate membranes poorly)
- Force field parameterisation (partial charges depend on protonation)
- Binding free energy calculations (incorrect protonation states corrupt $\Delta\Delta G$ estimates)

---

## 2. Why Is pKa So Difficult to Calculate?

You might expect that modern quantum chemistry, which can predict bond lengths to sub-ångström precision and reaction barriers to within a kcal/mol, should handle pKa without much trouble. In practice, pKa is one of the hardest molecular properties to calculate accurately from first principles, for several compounding reasons.

**The absolute free energy problem.** The $\mathrm{p}K_a$ of a molecule in aqueous solution depends on the absolute solvation free energy difference between the protonated and deprotonated forms, plus the free energy of the proton itself — a quantity that is notoriously difficult to pin down. The proton solvation free energy in water (around −265 kcal/mol, though consensus values vary by several kcal/mol depending on the thermodynamic cycle used) enters multiplicatively into the calculation, meaning even small errors in this reference propagate directly into your predicted $\mathrm{p}K_a$.

**Unit sensitivity.** Because $\mathrm{p}K_a = \Delta G / (RT \ln 10)$, a single kcal/mol error in $\Delta G$ translates to approximately 0.73 $\mathrm{p}K_a$ units. That does not sound dramatic until you realise that most QM methods operating on solvated systems have errors of several kcal/mol in absolute free energies. A calculation that is excellent by quantum chemistry standards might still miss the experimental $\mathrm{p}K_a$ by two or three units.

**Solvation model limitations.** Real aqueous protonation involves an intricate hydrogen-bond network around the ionisable site, cooperative solvent reorganisation, and sometimes explicit proton transfer to water. Implicit solvation models — which represent the solvent as a polarisable continuum — capture the electrostatic component reasonably well but miss specific solute-solvent interactions entirely. For highly polar or charged species, this approximation fails in a systematic but hard-to-correct manner.

**Conformational complexity and tautomerism.** The most stable geometry of the protonated form may differ substantially from that of the deprotonated form. A rigorous calculation requires finding the global minimum for each microstate — or, ideally, a properly weighted conformational ensemble. For flexible molecules with multiple ionisable groups and the possibility of intramolecular hydrogen bonds, the conformational space is vast. Tautomers (structural isomers that differ in proton placement without changing the net charge) add another layer of complexity: the nominal charge state of a molecule does not uniquely determine its structure.

**Systematic bias is the rule, not the exception.** Even well-validated QM methods produce raw $\mathrm{p}K_a$ values that are offset from experiment by a large, approximately constant systematic error. Our own GFN2-xTB/ALPB calculations, which are described below, produced effective free energies corresponding to nominal $\mathrm{p}K_a$ values in the range of 190–230 — obviously unphysical, but in a strangely predictable way that opens the door for machine learning calibration.

---

## 3. Development by Vibe Coding

The workflow was not designed top-down from a detailed specification. It grew iteratively through a series of working sessions with Claude, the kind of exploratory, back-and-forth development that has become known as *vibe coding* — writing a bit, running it, seeing what breaks, refining the theory, and iterating again. This approach turned out to be well-suited to the problem because the theoretical and practical challenges only became apparent as the code ran.

The starting point was the Uni-pKa/AcepKa framework from arXiv:2604.00841. The paper lays out a clean formalism: enumerate all microstates of a molecule, compute their free energies from QM, then fold in the pH dependence analytically via Boltzmann statistics. Implementing this required assembling several components.

**Phase 1: QM infrastructure.** The first step was writing the ORCA input generation machinery. Each microstate — defined by its proton count, net charge, and multiplicity — needed a geometry optimisation followed by a frequency calculation at the GFN2-xTB/ALPB(water) level. The frequency job provides the thermal corrections (zero-point energy, enthalpy, entropy) needed to assemble the Gibbs free energy from the electronic energy. We added robust retry logic for problematic charged species: looser SCF convergence thresholds, electronic temperature smearing (`etemp 3000`), and fallback strategies when the default settings stalled.

A non-trivial complication was the imaginary frequency problem. Geometry optimisations for flexible or multiply-charged species sometimes converge to first-order saddle points rather than true minima, betraying themselves with an imaginary vibrational mode. We wrote a loop that detects imaginary modes in ORCA output, uses `orca_pltvib` to generate an animation of the mode, extracts a displaced geometry at frame 10 of 20 along the mode trajectory, and restarts the optimisation from there — repeating until a true minimum is found or a maximum iteration count is reached.

**Phase 2: Charge descriptors.** A DFT single-point calculation at r2SCAN-3c/CPCM(water) level was added on top of the GFN2-xTB geometries. This served two purposes: a better estimate of the electronic energy, and the extraction of **Hirshfeld partial charges** as molecular descriptors for the ML model. Hirshfeld charges were chosen over the more commonly requested Mulliken charges because they are basis-set independent (Mulliken charges diverge unphysically when diffuse basis functions are used), more consistent across charge states (the $\Delta q$ between a carboxylate and its acid form is more physically meaningful), and better behaved for large or highly charged species. ORCA prints Hirshfeld charges when `Print[P_Hirshfeld] 1` is set in the `%output` block; we kept Mulliken charges as a fallback for older ORCA builds that predate the Hirshfeld implementation.

**Phase 3: The numerical crisis.** The first end-to-end run revealed the core problem described in section 2. The raw QM Gibbs free energies, when used directly in the Boltzmann expression, produced populations that were always 100% for one microstate and 0% for all others across the entire pH 0–14 range. Investigation showed that the effective free energy differences between microstates corresponded to nominal $\mathrm{p}K_a$ values around 200. The Boltzmann exponent $\Delta G / k_B T \approx 450$ causes `exp(-450) = 0` in standard floating-point arithmetic — complete numerical underflow, no matter how carefully you write the code.

The fix required abandoning the direct-Boltzmann route entirely. Instead, we converted the problem into the standard polyprotic species distribution formula, working in $\log_{10}$ space throughout and normalising with the log-sum-exp trick:

$$\log_{10}(\alpha_i) = \sum_{j < i} (\mathrm{p}K_{a,j} - \mathrm{pH})$$

$$\alpha_i = \frac{10^{\log_{10}(\alpha_i) - \max_k \log_{10}(\alpha_k)}}{\sum_k 10^{\log_{10}(\alpha_k) - \max_k \log_{10}(\alpha_k)}}$$

This formulation is numerically stable, gives smooth sigmoidal transitions at exactly the predicted $\mathrm{p}K_a$ values, and reproduces the microstate population diagrams shown in the AcepKa paper.

**Phase 4: ML calibration.** The final layer was a **Gaussian Process Regression (GPR)** model trained to map raw QM-derived features onto experimental $\mathrm{p}K_a$ values. The feature vector for each protonation step was constructed from the Hirshfeld charge differences between adjacent microstates, along with the raw QM free energy gap and molecular graph descriptors. GPR was chosen over simpler regression approaches because it provides calibrated uncertainty estimates alongside each prediction — useful for flagging molecules where the model is extrapolating outside its training distribution.

---

## 4. The Resulting ML Model

The final workflow operates as a pipeline with four stages.

**Stage 1 — Microstate enumeration.** Given a molecule (SMILES or 3D structure), all relevant protonation microstates are enumerated. For a monoprotic acid this gives two microstates; for a drug with three ionisable groups, up to eight. Each microstate is assigned a net charge, a proton count, and a starting 3D geometry (generated by RDKit or provided externally).

**Stage 2 — QM free energy calculation.** Each microstate is submitted to ORCA for a GFN2-xTB/ALPB(water) geometry optimisation and frequency calculation via Slurm array job. The Gibbs free energy $G_i(\mathrm{aq}) = E_\mathrm{elec} + G_\mathrm{RRHO} + \Delta G_\mathrm{solv}$ is extracted from the output. A subsequent DFT single-point at r2SCAN-3c/CPCM(water) provides Hirshfeld charges.

**Stage 3 — GPR calibration.** The raw inter-microstate free energy gaps and Hirshfeld charge descriptors are passed to the GPR model, which returns a predicted $\mathrm{p}K_a$ for each successive deprotonation step, along with a 95% confidence interval.

**Stage 4 — Population curves.** The predicted $\mathrm{p}K_a$ values are fed into the log-space species distribution formula, and microstate populations are computed as a function of pH over the range 0–14. The output is a set of smooth sigmoidal curves, one per microstate, showing how the molecular population redistributes as pH changes.

The GPR model was trained on a dataset of small organic molecules with experimentally measured $\mathrm{p}K_a$ values from the literature. The Hirshfeld $\Delta q$ descriptor proved more predictive than the raw energy gap alone, consistent with the interpretation that the charge redistribution upon protonation carries information that the scalar energy difference alone does not.

---

## 5. Current Shortcomings

The workflow is functional, but anyone wanting to use it should be aware of several important limitations.

**Computational cost is high.** Every microstate requires a full ORCA geometry optimisation with frequency calculation. For a molecule with four ionisable sites, that is 16 QM jobs, each potentially requiring tens of CPU-hours on an HPC cluster. The workflow is designed for HPC environments managed by Slurm and is not practical on a laptop or workstation for anything larger than a few atoms. Fast semiempirical methods (GFN2-xTB) keep this tractable, but the DFT single-point on top adds further cost.

**The GPR model needs retraining for new chemical space.** The calibration model was trained on a modest dataset of typical small organic molecules. It will extrapolate poorly to unusual chemical classes: highly strained systems, organometallic compounds, molecules with exotic heteroatoms, or species with extreme charges. Predictions for such systems should be treated with significant scepticism, and the GPR confidence intervals will correctly flag many (but not all) such cases.

**Tautomers are not handled.** The current workflow treats each protonation microstate as a single structure and does not enumerate tautomers within a charge state. For molecules where multiple tautomers are thermally accessible — keto/enol pairs, imidazole NH positions, and the like — this is a meaningful omission. The correct treatment would require tautomer enumeration and a Boltzmann-weighted free energy for each nominal charge state, which is technically straightforward but multiplies the computational cost.

**ORCA and Slurm are required.** The workflow is tightly coupled to ORCA for the QM calculations and Slurm for job management. There is no support for other QM codes (Gaussian, Q-Chem, NWChem) or other job schedulers (PBS, LSF, SGE). Porting to a different QM engine would require rewriting the input/output parsing modules.

**Conformational sampling is minimal.** Each microstate is represented by a single geometry — the nearest local minimum to the starting structure. For flexible molecules, the free energy of a microstate should be computed over a conformational ensemble, weighted by Boltzmann factors. The current implementation effectively assumes a rigid molecule, which is a reasonable approximation for rigid aromatic acids but breaks down for flexible peptides or macrocycles.

**The training dataset is private.** The GPR weights are distributed with the code, but the underlying training data is not, making it difficult to assess the applicability domain rigorously or to retrain the model on a different dataset without collecting new experimental data.

Despite these limitations, the workflow already produces qualitatively correct population curves for well-behaved small molecules and provides a principled, physics-grounded starting point for further development. The combination of a fast semiempirical QM method with a data-driven calibration layer strikes a reasonable balance between computational cost and accuracy, and the log-space population formulation means the numerical stability is solid once the calibrated $\mathrm{p}K_a$ values are in hand.

If you want to experiment with it, the code is available on this site and requires Python 3.9+, RDKit, scikit-learn, numpy, and a working ORCA 6 installation with GFN2-xTB support. Drop me a message if you run into issues — there are enough moving parts that a fresh installation on a new HPC environment almost certainly requires some path configuration.
