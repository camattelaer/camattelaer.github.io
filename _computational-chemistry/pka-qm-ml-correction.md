---
title: 'Building an ML corrector for pK<sub>a</sub> calculations: My adventures in "vibe" coding'
date: 2026-05-16
layout: single
classes: wide
author_profile: false
math: true
header:
  teaser: /assets/content/compchem/pka-qm-ml-correction/meme.jpg
---

---
### Disclaimer
Files and code relevant for this post have been made available:
 - [Github](https://github.com/camattelaer/pKa-calc_LFER): code and model
 - [Zenodo](): code, model and raw data

---

## 1. Introduction (and obsession)

### What is pKa?

This post will assume that the reader is familiar with basic acid-base theory and terms as pKa, pH and the like. Simply put according to the Bromsted-Lowry theory, acids donate protons and bases accept protons. Here, pK<sub>a</sub> is known as a measure for the acidity of a compoundand thus the tendency of a molecule to lose a proton (in water, that is). This is a very important property of molecules. For example, the pH in cthe human body is 7.4 and is thightly regulated by both respiratory (O2/CO2(g)) balances as well as metabolic (HCO3-/CO2(aq)) balances. Even a tiny variation in pH, in the order of several 0.1 units, can already cause pathological symptoms.

The acid dissociation constant, $K_a$, quantifies the tendency of a molecule to donate a proton to water:

$$\mathrm{HA} + \mathrm{H_{2}O} \rightleftharpoons \mathrm{A}^- + \mathrm{H_{3}O}^+$$

$$K_a = K \cdot [\mathrm{H_{2}O}] = \frac{[\mathrm{A}^-][\mathrm{H_{3}O}^+]}{[\mathrm{HA}]}$$

In practice, $K_a$ values span many orders of magnitude, so chemists work with $\mathrm{p}K_a = -\log_{10}(K_a)$. A low $\mathrm{p}K_a$ means a strong acid that readily gives up its proton; a high $\mathrm{p}K_a$ means the proton is tightly held.

For a molecule with multiple ionisable sites — think a drug with an amine, a carboxylic acid, and a phenol — there is not one $\mathrm{p}K_a$ but a ladder of them, one for each successive deprotonation step. At any given pH, the molecule exists as a mixture of **microstates** (distinct protonation forms, e.g. different tautomers), with each microstate carrying a population that follows a Boltzmann distribution over the accessible free energies. Each distinct microstate corresponds to a particular **microscopic** pK<sub>a</sub> value. It is the population of different microstates and their respective pK<sub>a</sub> that will give rise to the **macroscopic** property we measure experimentally as pKa.

### Why is calculating pK<sub>a</sub> values so difficult?
In essence, the reaction above appears simple enough and calculating reaction energies is right there at the top of applications for QM calculations. However, ...

<div style="width: 75%; margin: 0 auto 1em auto; text-align: center;">
  <img src="{{ '/assets/content/compchem/pka-qm-ml-correction/meme.jpg' | relative_url }}" 
       style="width: 100%; height: auto;">
</div>

There are a lot of factors influencing calculations if you want to accurately calculate pK<sub>a</sub> values (list not exhaustive):
- **solvent effects**: pK<sub>a</sub> is defined in water and solvent effects are extremly important in stabilizing both the neutral forms as well as the ionic forms in the equation above. Implicit solvent models always have shortcomings to accurately describe the interactions between solute and solvent and including explicit solvent molecules in your calculations is computationally demanding.
- **molecular ensembles**: As previously mentioned, the acidic and basic form of a compound do not exist in isolation in solution. To accurately describe the reaction, molecular ensembles have to be considered (conformers, tautomers, ...) and exploring the potential energy surface of these molecular ensembles also requires a significant amount of compute time.
- **accuracy of the method**: You will already require some compute time and a lot of energy/gradient evaluations (this can easily reach order of magnitude 10 000 or higher) for the previously mentioned calculations. Doing this with a method that requires hours for a single evaluation would mean a calculation can take up months or even years. This is simply not feasible and worthwile. Hence you will typically apply a method with higher throughput but with a lower accuracy which is still relevant for capturing difficult effects such as solvent interactions.
- **thermodynamics of the proton**: In reality, the proton $\mathrm{H}^+$ does not simply exists as $\mathrm{H}^+$ in solution. Even the actual structure of $\mathrm{H_{3}O}^+$ is more involved and complex than an isolated molecule, see e.g. [this link](https://pubs.acs.org/doi/10.1021/ed1010213). Additionally QM calculations are based on (valence) electrons. The proton, as its name implies, does not contain any electrons and direct calculations on the proton itself are therefor not possible nor can we correlate direct measurements of thermodynamic parameters ($\Delta H$ or $-T\Delta S$) for the proton to calculations in a strathforward way.

Considering all these problems and probably others which I currently forgot about, make this simple concept of pK<sub>a</sub> based on reaction thermodynamics a very difficult problem to calculate and has evolved to somewhat of an obsessiopn for me. Trying to a attempt yet again when I think of a new approach which I have not yet considered before.

## 2. The "direct" approach 
 Obviously one of the first things I tried in the past was the "direct" approach, i.e. considering only the molecules in the chemical reaction above and it is safe to say that no meaningful result was obtained when looking at macroscopic reference values.

 Since a few months, I have warmed up to Claude (Code) in my work. This allows me to think about the required physics in a calculation and let Claude do the heavy lifting for setting up the calculations and more importantly the automatic transfer from one method to the subsequent method. This gave me the idea to explore a linear free energy relation (LFER) for pK<sub>a</sub> calculations which is typically implemented for approach such as the "direct" method because this linear correlation between calculated values and experimental pK<sub>a</sub> (references) can already correct for some of the above mentioned problems.

 Unfortunately, I do not have all raw data anymore. When I started doing the LFER correction for the direct approach, I noticed something peculiar: when separating the data according to functional groups, the linear correlation significantly improved. This gave my the idea that a machine learned (ML) model would probably be an interesting route as it would be ableto distinguish the molecules based on structure/functional group. So I set up for a "full vibe" experience since I have no ML experience and rely on Claude to provide the necessary code and implement an ML correction for our pK<sub>a</sub> calculations. I will let Claude themselves do the talking about the model and will provide a short discussion & conclusion myself at the end - and yes, this is **raw output** from Claude based on our conversation.

---

## 3. The QM workflow

The starting point for the ML correction is a set of raw quantum mechanical free energies, one per protonation microstate per molecule. The theoretical framework comes from Pesce, Farr, and de Fabritiis ([arXiv:2604.00841](https://arxiv.org/abs/2604.00841)): compute the Gibbs free energy of each microstate in implicit aqueous solvent, then assemble microstate populations as a function of pH via Boltzmann statistics.

Each molecule is defined in a `.msf` (microstate file) — a plain-text format that lists every protonation state with its charge, multiplicity, proton count, 3D coordinates, and optionally an experimental pK<sub>a</sub> for training. This file acts as both the input to the QM stage and the persistent record across the pipeline, so calculations that get preempted on the cluster can restart without losing progress.

### The two-step ORCA protocol

**Step 1** is a GFN2-xTB/ALPB(water) geometry optimisation and frequency calculation. GFN2-xTB is a tight-binding semiempirical method that is fast enough to handle the conformational sampling we need while still capturing the right qualitative electronic structure. The frequency calculation is required to extract the rigid-rotor harmonic-oscillator (RRHO) thermal corrections — zero-point energy, enthalpy, and entropy — that turn the electronic energy into a proper Gibbs free energy at 298 K:

$$G_i(\mathrm{aq}) = E_\mathrm{elec} + G_\mathrm{RRHO} + \Delta G_\mathrm{solv}$$

In practice, not all microstates converge cleanly. Highly charged or conjugated anions occasionally refuse to converge under default settings. For these cases a `robust` mode was added: SCF damping, electronic temperature smearing at 3000 K, extended iteration limits, and the `SlowConv` keyword. A further problem was **imaginary frequencies** — geometry optimisations that converge to a saddle point rather than a true minimum, betraying themselves with a negative vibrational frequency. The fix was an automated retry loop: detect the imaginary mode, use ORCA's `orca_pltvib` to generate a mode animation, extract the maximally displaced geometry at frame 10 of 20 along the mode trajectory, and restart the optimisation from there. This loop repeats until a clean minimum is found.

**Step 2** is a DFT single-point at r2SCAN-3c/CPCM(water) on the xTB geometry. This serves two purposes: a better electronic energy, and the extraction of **Hirshfeld partial charges** that become the primary descriptors for the ML model. Hirshfeld charges were chosen deliberately over the more commonly requested Mulliken charges — Mulliken charges diverge unphysically when diffuse basis functions are used, making them inconsistent across charge states and poorly behaved for large or highly charged species. Hirshfeld charges are basis-set independent and physically better defined. Both are extracted from every calculation, with Mulliken retained as a fallback for older ORCA builds.

### The numerical crisis

The first end-to-end run of the population workflow produced a rather alarming result: every microstate had a population of either exactly 100% or exactly 0% across the entire pH 0–14 range, for every molecule tested. This was not a bug in the population formula — it was a floating-point underflow problem.

The raw GFN2-xTB free energy differences between microstates correspond to inter-microstate $\Delta G$ values equivalent to nominal pK<sub>a</sub> values in the range of **190 to 230**. These are not wrong — they are a consistent consequence of the thermodynamic cycle — but they mean the Boltzmann exponent is approximately $\Delta G / k_BT \approx 450$, and `exp(-450)` is identically zero in standard 64-bit floating point. No amount of careful coding fixes this; the information is genuinely lost in the floating-point representation.

The solution was to abandon the direct Boltzmann route entirely and reformulate the population calculation in $\log_{10}$ space using the log-sum-exp trick:

$$\log_{10}(\alpha_i) = \sum_{j < i} \left(\mathrm{p}K_{a,j} - \mathrm{pH}\right)$$

$$\alpha_i = \frac{10^{\log_{10}(\alpha_i) - \max_k \log_{10}(\alpha_k)}}{\sum_k 10^{\log_{10}(\alpha_k) - \max_k \log_{10}(\alpha_k)}}$$

This formulation is numerically stable for any physically meaningful pK<sub>a</sub> range and produces the smooth sigmoidal population curves one would expect. The key insight is that the raw GFN2 pK<sub>a</sub> values of ~200 only need to be *relatively* correct to each other — the ML calibration layer then maps them onto the experimentally observed range. The 190–230 values contain real chemical information about relative acidity; they just need rescaling and recentring before they are useful.

## 4. The ML model

### What we were trying to do

The ML model (`pka_gpr_calibrate.py`) sits between the raw QM numbers and the final population curves. Its job is to take the raw pK<sub>a</sub> estimate for each protonation step — somewhere in the 190–230 range — together with a set of quantum chemical descriptors, and predict the experimental pKa. This is fundamentally a regression problem with a small training set (ultimately around 200 MSF files) and a heterogeneous input space covering many different functional group types.

### The benchmark

Before settling on an architecture, a systematic benchmark was run on 59 training steps with real ORCA-computed descriptors, evaluating every model by leave-one-out (LOO) cross-validation. The results were:

| Model | LOO RMSE (pKa units) |
|---|---|
| Ridge Regression | 2.701 |
| Kernel Ridge Regression (RBF) | 2.465 |
| Random Forest (500 trees) | 1.968 |
| Gradient Boosting | 1.865 |
| GPR with RBF kernel (sklearn) | 1.833 |
| GPR with Matérn ν=3/2 kernel | ~1.71 |
| GPR with Matérn ν=5/2 kernel | ~1.71 |
| **SVR with RBF kernel** | **1.614** |

The linear models (Ridge, KRR) were cleanly the worst, which confirmed that the relationship between QM descriptors and experimental pK<sub>a</sub> is genuinely nonlinear across different functional group classes — something we already suspected from the LFER analysis. The tree methods (Random Forest, Gradient Boosting) were competitive but not the best. The clear winner on accuracy was **Support Vector Regression (SVR)** with an RBF kernel, at LOO RMSE = 1.614.

### Why we did not use SVR

SVR is the most accurate model in the benchmark, and yet it is not what was ultimately implemented as the primary model. The reason is simple: **SVR makes a single point prediction with no indication of confidence**. For a tool that is applied to novel molecules — often ones the model has never seen anything like — knowing *when not to trust the answer* is as important as knowing the answer itself. A prediction of pK<sub>a</sub> = 8.3 ± 0.4 and a prediction of pK<sub>a</sub> = 8.3 ± 3.1 should be treated very differently by anyone using the output.

The Gaussian Process Regression (GPR) model returns a posterior standard deviation $\sigma$ alongside every prediction. This $\sigma$ grows naturally when the query compound sits far from any training data in feature space — exactly the signal we need to flag unreliable predictions. SVR cannot do this. So despite being slightly less accurate on the benchmark, GPR was chosen as the primary model for this reason.

SVR is available as a `--model svr` flag for cases where raw point accuracy matters more than uncertainty quantification.

### Why Matérn ν=5/2 and not the RBF kernel

The initial implementation used an RBF (squared-exponential) kernel, which is the default choice in most GPR tutorials. The RBF kernel assumes that the target function is infinitely smooth — every derivative exists everywhere. That assumption is physically wrong for pK<sub>a</sub> prediction. Within a functional group family (say, aliphatic carboxylates), pK<sub>a</sub> does vary smoothly with electronic structure. But across different functional group families — carboxylate versus phenol, ammonium versus guanidinium — the behaviour is effectively discontinuous from the kernel's perspective. Forcing the RBF kernel to cover both regimes simultaneously means it has to use a large length scale that washes out within-group structure.

The **Matérn ν=5/2 kernel** is twice-differentiable but not infinitely smooth, and decays faster at large inter-point distances. This means it assigns appropriately low similarity to chemically dissimilar compounds, which is exactly what is needed here. On the benchmark at N=59, switching from RBF to Matérn ν=5/2 gave approximately 10% RMSE improvement. The Matérn kernel was implemented from scratch with analytical gradients (verified against finite differences) rather than using the sklearn implementation, in order to keep full control over the per-feature Automatic Relevance Determination (ARD) length scales and the hyperparameter optimisation.

The kernel is:

$$k(\mathbf{x}_1, \mathbf{x}_2) = a^2 \left(1 + \sqrt{5}\,r + \tfrac{5}{3}r^2\right) e^{-\sqrt{5}\,r}, \quad r = \sqrt{\sum_d \frac{(x_{1,d} - x_{2,d})^2}{\ell_d^2}}$$

where $a$ is the amplitude, $\ell_d$ is the per-feature length scale, and $r$ is the scaled Euclidean distance. Hyperparameters are optimised by maximising the log-marginal likelihood using L-BFGS-B with 27 random restarts.

### Other architectures that were considered and rejected

**A two-stage LFER + GPR architecture.** The first idea for improving on a pure GPR was to pre-correct the raw pK<sub>a</sub> values with a linear free energy relationship per functional group before the GPR saw the data — essentially doing a per-group linear regression first, then having the GPR correct the residual. The appeal was that the large systematic offset between chemical families (guanidinium sits at pKa_calc ≈ 187, carboxylates around 205, phenols around 215) would be absorbed analytically. The problem: at the time of implementation, most functional group categories had only one or two training compounds. A per-group LFER fitted on two data points has essentially no generalisation ability and would have made things worse. This idea was reverted.

**Heteroscedastic noise.** The standard GPR uses a single noise parameter $\sigma_n$ for all training points, assuming every observation has the same measurement uncertainty. In reality, predictions for simple well-characterised functional groups (aliphatic carboxylates, aliphatic amines) are far more reliable than predictions for rare scaffolds. Heteroscedastic noise weights were implemented to reflect this, assigning lower noise to well-represented groups and higher noise to singletons. The noise parameter did improve: it dropped from 0.727 to 0.657. However, the LOO RMSE barely changed (and in one run slightly increased). The diagnosis: the LOO error for isolated compounds is dominated by kernel support density, not by the noise model. A compound with no similar training neighbours reverts to the prior regardless of how its noise weight is set. This modification was reverted.

**Physics-informed neural network (à la Starling/Rowan).** This was raised as a question during development: would it not be better to build something like Rowan's Starling tool, which combines a neural network potential (AIMNet2) with a graph neural network trained on millions of pK<sub>a</sub> measurements from ChEMBL? The honest answer is no — not for this dataset. Starling's accuracy comes primarily from having millions of experimental training points, made accessible by the ~1000× speed advantage of AIMNet2 over DFT for energy evaluation. A graph neural network trained on ~200 compounds would simply overfit. The statistical literature suggests N ≥ 500 before message-passing networks start outperforming GPR/SVR on tabular data. The GPR is appropriate for the dataset size we have.

## 5. The feature vector: what we use and why

The final feature vector is nine-dimensional. Here is what each feature is, why it was chosen, and what was tried and dropped along the way.

### Features in the final model

**δpKa_calc** — the raw QM-derived pK<sub>a</sub> for the protonation step, centred by subtracting the mean pKa_calc of all training steps at the same net acid charge state. The centering matters enormously: without it, the raw values of 187–263 cause the length-scale optimiser to find scales so large that the feature carries no information. Subtracting the charge-state mean (computed from the training set at fit time) compresses the feature to deviations of roughly ±15 units that are genuinely informative about relative acidity within a charge class.

**q_acid** — the Hirshfeld partial charge on the ionisable heavy atom of the acid-form microstate, from the r2SCAN-3c/CPCM single-point. This encodes the Born solvation contribution: more charged atoms experience stronger differential solvation, which systematically shifts the pKa.

**Δq_O, Δq_N, Δq_C** — element-resolved Hirshfeld charge differences between the base and acid microstates. These are the change in total charge sitting on all oxygen atoms, all nitrogen atoms, and all carbon atoms respectively, upon deprotonation. A large negative Δq_O signals a carboxylate or phenolate forming. A large negative Δq_N signals an ammonium or guanidinium losing its proton. Δq_C captures resonance delocalisation into the carbon skeleton.

**Σ\|Δq\|** — the sum of absolute Hirshfeld charge changes across all atoms. This measures how delocalised the proton's departure is across the whole molecule. A thiol losing a proton concentrates the charge on one sulfur atom (small Σ\|Δq\|); an aromatic carboxylate spreads it through the ring system (large Σ\|Δq\|).

**is_O_dom, is_N_dom, is_S_dom** — binary indicators for which element experiences the dominant charge shift. These three features were the result of a specific diagnosis: without them, the kernel conflates carboxylates with phenolates (both have large \|Δq_O\|) and confuses ammonium with guanidinium (both large \|Δq_N\|), which forces the ARD length scales for those dimensions to become very large — effectively disabling those features. The indicators partition the training data into chemically coherent neighbourhoods so the kernel can function correctly within each group. In the converged model they behave more like hard separators than graded similarity measures, which is physically appropriate.

### Features that were tried and dropped

This is where the development got genuinely interesting — and where the length-scale diagnostics from the ARD optimisation were invaluable. A feature is considered "inactive" when its optimised length scale hits the upper bound of the allowed range (set to 5.0 in the final implementation). An inactive feature means the optimiser is saying: this feature adds no independent information given what the other features already tell me.

**Δq_S** (Hirshfeld charge change on sulfur atoms). This went wall-bound in every training run. With only a handful of thiol and sulfonate training compounds, there simply is not enough training density for the kernel to learn a sulfur-specific pattern. Replaced by the `is_S_dom` indicator.

**ΔE_LUMO** (change in LUMO energy between base and acid microstates). This had the highest raw Pearson correlation with the DFT correction of any descriptor tested — r = +0.505. Despite this, it consistently went wall-bound in the GPR. The reason: ΔE_LUMO is strongly correlated with δpKa_calc itself. Once the centred QM pK<sub>a</sub> value is in the kernel, ΔE_LUMO carries no additional independent signal. It was adding two extra hyperparameters to optimise while contributing nothing to accuracy.

**ΔE_HOMO and ΔE_gap** (HOMO energy change and HOMO–LUMO gap change on deprotonation). These were added after an earlier SVR benchmark at N=59 showed they reduced SVR RMSE from 1.664 to 1.444 — a 13% improvement. The physical reasoning was compelling: large ΔE_HOMO corresponds to extensive π-delocalisation upon deprotonation (as in ammonium and guanidinium species), while ΔE_gap encodes aromaticity changes (imidazolium→imidazole gives Δgap ≈ +11 eV, while a simple carboxylate gives +1–3 eV). Both features were implemented and carefully validated. Both went wall-bound in the GPR at N=82 and beyond. The explanation for this apparent contradiction: SVR with an RBF kernel and tuned C/ε hyperparameters can exploit many moderately correlated features simultaneously; GPR with ARD length scales needs each feature to be independently informative relative to everything else already in the kernel. With the functional group indicators and bond-order features present, the orbital energies were redundant.

**Δ\|μ\|** (change in dipole moment magnitude). Tested alongside the orbital features. Wall-bound in all GPR fits.

**ΔBO_XC and ΔBO_ring** (Mayer bond order changes). These were motivated by a specific failure mode: 4-nitrophenolate and phenolate can have very similar Δq_O values because both form a phenolate, but the nitro group relay means the charge redistribution is qualitatively different. Mayer bond orders — extractable from ORCA without any external software via `Print[P_BondOrders] 1` — capture how the bond between the ionisable heteroatom and its directly bonded carbon changes on deprotonation, encoding whether resonance into the ring occurs. ΔBO_ring similarly captures aromatic charge relay. Both features were implemented, extracted, and added to the feature vector. Both went wall-bound. With the current training set size and the functional group indicators already separating the major classes, the additional resolution from bond orders cannot be learned. They remain candidates for when the training set is substantially larger.

**NBO E(2) donor-acceptor energies and QTAIM bond critical point properties** were discussed and dismissed early. Both would require external post-processing software — NBO7 or Multiwfn respectively — and a deliberate design choice was made to keep the pipeline dependent only on ORCA and standard Python libraries. This constraint ruled out both.

### What the length scales tell us in the final model

When trained on the full dataset (~200 training steps), the three most informative features are consistently **Δq_O** (shortest length scale, ≈ 0.97), **q_acid** (≈ 1.76), and **δpKa_calc** (≈ 1.86–3.13 across runs). These three features alone carry most of the predictive signal. Δq_N, Δq_C, and Σ\|Δq\| are active at intermediate scales. The functional group indicators approach the upper bound, acting as structural separators rather than smooth similarity features.

## 6. Results and shortcomings

### How well does it work?

The LOO RMSE on the full training set is approximately **2.1–2.4 pK<sub>a</sub> units**. This number deserves careful interpretation. LOO RMSE measures how well the model can predict each training compound when it is left out of the fit — and for a heterogeneous training set covering many different functional group types, many compounds have no close structural neighbours in feature space. Their LOO predictions revert to the GPR prior with large errors, inflating the overall figure. A more informative metric is the within-class RMSE for well-covered functional groups (aliphatic carboxylates, aliphatic amines, simple phenols), which is approximately **0.8–1.0 pK<sub>a</sub> units** — already competitive with published implicit-solvent pK<sub>a</sub> methods.

To stress-test the model on scaffolds not represented in training, a 20-compound medchem test set was assembled covering 10 structural families that were absent or thinly covered: sulfonamide antibiotics, diaminopyrimidines, nitroimidazoles, imizolines, SNRI antidepressants, AChE inhibitors, cyclic N-H acids (hydantoin, thiazolidinedione, benzothiazine enolate), β-amino acids, and nucleoside analogues. Of 23 ionisation steps tested, **15 were predicted within the LOO RMSE** of the training set (test RMSE ≈ 0.96 on these steps). The remaining 8 were failures on genuinely novel scaffolds.

Two failures were severe enough to be instructive. Metformin's second ionisation step (guanidinium, q+2→+1) had an initial error of +13 pK<sub>a</sub> units. Aspirin's carboxylate step had an error of −7 units. Both were driven by the same root cause: the model's training set had no compounds with similar DFT descriptor signatures, so the prediction reverted to the prior. Both improved dramatically after targeted training additions — adding a compound covering the q+1→0 guanidinium class and adding salicylic acid to represent ortho-activated aryl carboxylates. This confirmed that the LOO RMSE bottleneck is **training set coverage**, not the model architecture.

### The extrapolation problem

The deeper issue revealed by the test set is that the GPR kernel computes similarity in a 9-dimensional space of quantum chemical descriptors that does not encode molecular structure. Two compounds can have very similar Hirshfeld charge descriptors but very different molecular graphs — and the model cannot distinguish them. Cetirizine (a piperazine with a carboxylate on the same nitrogen chain) is a good example: its DFT descriptors look superficially like other ammonium-near-EWG compounds, but the specific connectivity — three bonds from the ionisable nitrogen to a pendant carboxylate — is unique in the training set. The kernel assigns high similarity to structurally dissimilar compounds and the prediction fails.

The proposed fix is a **product kernel** combining the Matérn kernel on DFT descriptors with a Tanimoto kernel on ECFP4 molecular fingerprints:

$$k_\mathrm{total}(\mathbf{x}_i, \mathbf{x}_j) = k_\mathrm{Matérn}(\mathbf{x}_i, \mathbf{x}_j) \times k_\mathrm{Tanimoto}(\mathrm{fp}_i, \mathrm{fp}_j)$$

A product kernel requires both structural similarity *and* DFT descriptor similarity to be high before two compounds influence each other's prediction. This is far more selective than either kernel alone. SMILES strings are already embedded in each MSF file, so the fingerprints are computable via RDKit at zero additional QM cost. This has been identified as the next implementation step.

### Other known shortcomings

- **Tautomers within a charge state are not handled** by the main pipeline. Each charge state is represented by a single optimised structure. For compounds with accessible tautomers (imidazole NH position, keto-enol pairs), this is a meaningful simplification.
- **Conformational sampling is single-structure.** Each microstate is relaxed from its starting geometry to the nearest local minimum. For flexible molecules the free energy should properly be Boltzmann-averaged over a conformational ensemble.
- **ORCA and Slurm are hard dependencies.** Every piece of output parsing is tightly coupled to ORCA's specific output format. Porting to another QM code would require rewriting the I/O layer.
- **The training set remains modest.** The fundamental bottleneck identified throughout development is not the kernel, not the features, but the number of training compounds in underrepresented chemical classes. Adding 40–50 more compounds targeted at sparse functional group classes (guanidinium q+1→0, sulfonates, dihydropyridinium, phosphates) would, by the kernel density argument, reduce the LOO RMSE more than any further architectural change.

---

## 7. Personal discussion and conclusion

I feel very unsecure publishing this. I did not have the time to double check what Claude actually cooked up and I am providing all raw data at the user's discretion. If this wasn't for a hobby project, I would most definitely have spent more time going through Claude's code to make sure it actually makes sense.

In addition, I feel the need to add that Claude apparently forgot the fact that that the code actually runs a conformational and tautomeric search, but limits the number of evaluated compounds to reduce the following computational wall time. It does not rely on a single geometry per protonations state. However, I do *believe* that the code does not average charges over the geometries, perhaps another point of improvement that could be made.

Next, does it work? Yes, but not ideally. Comparing the first test set from which I saved the results, with the last one, we do see some improvement:

<div style="width: 75%; margin: 0 auto 1em auto; text-align: center;">
  <img src="{{ '/assets/content/compchem/pka-qm-ml-correction/gpr_predictions_test-initial.png' | relative_url }}"
       alt="Figure 1"
       style="width: 100%; height: auto;">
  <div style="
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
  Figure 1: GPR predictions on the first recorded test set. Some large deviations from experimental pK<sub>a</sub> values are observed along with some very large errors for multiple compounds.
  </div>
</div>

<div style="width: 75%; margin: 0 auto 1em auto; text-align: center;">
  <img src="{{ '/assets/content/compchem/pka-qm-ml-correction/gpr_predictions_test-final.png' | relative_url }}"
       alt="Figure 2"
       style="width: 100%; height: auto;">
  <div style="
    font-family: 'Palatino linotype';
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
  ">
  Figure 2: GPR predictions on the final test set. Overall agreement with experimental pK<sub>a</sub> is rather OK, and MAE/RMSE has also decreased.
  </div>
</div>

This is a positive result. However, I would have liked a minimal ML model that would be able to correct the calculated pK<sub>a</sub> value to within 1 pK<sub>a</sub> unit. My feeling currently is that this kind of accuracy might be attainable with this approach, but only with even more training data. The presence of similar compounds in the training data seems to be critical to obtain accurate results. In that sense, my approach here failed because I wanted to **not** rely on similar compounds for accurate results. Something I will discuss in a next post related to the "isodesmic" approach.

This was already a very long post so I will end this here and if you have any questions, please feel free to contact me.

CA