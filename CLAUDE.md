# EuroQol Population Norms — Project Context

## Scientific Background

The EuroQol group requires population reference estimates ("population norms") for its suite of
measures, in particular the **EQ-5D-5L** health-related quality of life instrument. The gold
standard for deriving such norms is random sampling, but in practice many datasets rely on
**online panel quota sampling**, which may introduce systematic biases.

This project conducts a **secondary data analysis** comparing datasets collected under different
sampling strategies for the UK/England population, to evaluate the representativeness of online
panel sampling and derive adjusted norms.

---

## Datasets

Six datasets have already been collected, cleaned, and **concatenated into a single dataframe**.
The two primary datasets are:

| Dataset | Sampling strategy |
|---|---|
| **HSE** — Health Survey for England | Stratified random sampling (gold standard / target) |
| **EQ-DAPHNIE** — EuroQol Data for Assessment of Population Health Needs and Instrument Evaluation | Online panel with quota sampling (source) |

HSE is treated as the **reference/target distribution** throughout the analysis.

### Sample sizes (Apr 2026 cleaned data)

Unresponsive participants (those who barely answered questions) have been dropped from the
dataset. Retention rates vary substantially across waves:

| Dataset | Retained (n) | Approx. retention |
|---|---|---|
| DAPHNIE 2024 | 5,237 | **~34%** |
| DAPHNIE 2023 | 1,657 | ~76% |
| HSE 2017 | 7,996 | ~80% |
| HSE 2018 | 8,177 | ~80% |
| HSE 2019 | 8,201 | ~80% |
| HSE 2022 | 7,727 | ~85% |
| **Total** | **38,995** | |

The low retention in DAPHNIE 2024 (~66% excluded) means the retained sample is the more
engaged subset of an already quota-sampled panel — an additional layer of selection bias on
top of the original sampling design. This should be acknowledged as a limitation when
reporting density ratio results for DAPHNIE 2024.

---

## Outcome Variables

Five main outcomes (confirmed by PI):

| Variable | Description | Notes |
|---|---|---|
| `srh` | Self-rated health (ordinal 1–5) | Separate measure |
| `EQvas` | EQ Visual Analogue Scale (0–100) | Separate measure |
| `FULLHEALTH` | Full health vs any EQ-5D-5L problem (binary) | Related to LSS_rs and EQ_index |
| `LSS_rs` | Leidelmeijer Severity Score (0–100) | Related to FULLHEALTH and EQ_index |
| `EQ_index` | EQ-5D-5L utility index (value set-scored) | Related to FULLHEALTH and LSS_rs |

`FULLHEALTH`, `LSS_rs`, and `EQ_index` are all derived from the same five EQ-5D-5L
dimensions and are therefore closely related. `EQvas` and `srh` are independent measures.

---

## Predictor Variables (Covariates for Density Ratio / Adjustment)

Confirmed predictor set (PI):

`Sex`, `age7cat`, `emp_cat`, `eth4cat`, `PA_vig`, `PA_mod`, `smoke_ever`, `smoke_ecig`,
`alcohol_yr`, `diabetes`, `obese`, `resp`, `skin`

Note: `PA_vig` and `PA_mod` are the physical activity variables in the Apr 2026 data (days
per week; replacing old `paVig`/`paMod` categorical columns). They have 95.8% missing and
are present only in DAPHNIE 2023 — same issue as before, cannot enter the density ratio model.

---

## Project Aims

### Aim 1 — Understand heterogeneity across datasets
Characterise differences in health and sociodemographic/SES distributions between datasets using:
- Traditional regression approaches
- Unsupervised clustering (k-means, UMAP, LCA)
- Community detection algorithms (Louvain and Leiden) to validate cluster structure

The goal is not to find identical clusters across datasets, but to identify whether certain health
and SES subgroups are systematically **under- or over-represented** in one dataset relative to
another.

### Aim 2 — Derive adjusted EQ-5D-5L norms and assess residual differences
Apply adjustment techniques informed by Aim 1 and assess whether adjusted norms still differ
across datasets.

---

## Methodological Framing

### Covariate Shift
The project is also framed as a **covariate shift** problem:

- The marginal covariate distribution $P(X)$ differs across datasets (sampling bias)
- The conditional $P(Y|X)$ is assumed stable across datasets (same underlying health given same
  person type) — this is a testable scientific assumption; violations would suggest **mode
  effects or panel conditioning**
- Correction proceeds by estimating the **density ratio** $w(x) = P_\text{target}(x) /
  P_\text{source}(x)$ and using it as importance weights

### Density Ratio Estimation
Preferred approach: **classifier-based estimation**
- Train a binary classifier to distinguish source (online panel) from target (HSE) samples
- The predicted probability odds approximate $w(x)$
- Analogous to propensity score weighting in observational studies — interpretable and familiar
  to health economists
- Alternatives to keep in mind: Kernel Mean Matching (KMM), KLIEP, RuLSIF

### Multi-source Structure
With six datasets, the covariate shift is a **multi-source problem**. Two key questions:
1. Is each non-HSE dataset shifted relative to HSE? (pairwise, HSE as fixed target)
2. Do datasets cluster among themselves in terms of distributional similarity?

The second question is where clustering/community detection from Aim 1 becomes directly
informative for Aim 2.

---

## Notebooks

| Notebook | Description | Status |
|---|---|---|
| `data_wrangling/02-csv_wrangling.ipynb` | Cleans and concatenates all six raw datasets into `data/wrangled_data.csv`; harmonises variable names, coding, and survey weights | Done |
| `covariate_shift/01-covariate_comparison.ipynb` | Within-HSE consistency check: weighted SMD comparing pre-2020 (2017–2019) vs post-2020 (HSE 2022); Love plot | Done — re-run Apr 2026 |
| `covariate_shift/02-daphnie_vs_hse.ipynb` | 2×2 SMD comparison: each DAPHNIE wave (2023, 2024) vs each HSE target (2022, pre-2020); Love plot | Done — re-run Apr 2026 |
| `covariate_shift/03-density_ratio.ipynb` | Classifier-based density ratio estimation (logistic regression + gradient boosting) for each DAPHNIE wave vs pre-2020 HSE; weight diagnostics; before/after balance check | In progress |

---

## Key Findings from Covariate Comparison

### HSE 2022 lacks EQ-5D-5L data
HSE 2022 has no observations for the five EQ-5D-5L dimensions. This means **the
pre-2020 HSE waves (2017–2019) are the only valid HSE reference for EQ-5D norm
derivation**. HSE 2022 may still be used for sensitivity checks on variables it does
contain (e.g. employment, BMI, SRH).

### Within-HSE drift is small and largely explainable (Apr 2026 re-run)
Only 4 of 27 variables exceed |SMD| > 0.1 (pre-2020 vs HSE 2022):

| Variable | SMD (post − pre) | Explanation |
|---|---|---|
| `obese` | −0.244 | Measurement shift (nurse-measured pre-2020 vs self-reported 2022) |
| `smoke_ever` | −0.176 | Plausible secular decline in smoking prevalence (54.8% → 54.5% → 52.6% → 50.8% across waves) |
| `edu_cat` | +0.166 | Plausible secular trend |
| `sat` | −0.156 | Possible COVID effect on life satisfaction |

Notably, **employment is now stable within HSE** — the large SMDs seen previously
(emp_cat SMD up to 0.41) were entirely the all-zero coding artefact. EQ-5D dimensions
and health outcomes are stable across the split. Pre-2020 HSE is a valid, stable
reference pool for norm derivation.

### DAPHNIE vs HSE: main imbalanced covariates (Apr 2026 re-run)

SMDs below are DAPHNIE 2024 vs pre-2020 HSE (primary density ratio comparison) unless noted.
23 variables show |SMD| > 0.1 in at least one of the four comparisons.

**Variables with large imbalance — currently outside the density ratio feature set:**
- **`alcohol_yr`** (SMD = −0.87): largest imbalance; skip-logic artefact, not includable as-is
- **`srh`** (SMD = −0.82): DAPHNIE reports consistently worse self-rated health across all 4 comparisons; an outcome, not a predictor
- **`edu_cat`** (SMD = +0.47): DAPHNIE 2024 massively overrepresents degree holders (41.4% vs ~28–29% pre-2020 HSE) and nearly eliminates no-qualification respondents (2.3% vs ~21%); not in confirmed predictor set but the largest structural imbalance with no construct issue; **DAPHNIE 2023 is 100% missing** — inclusion only viable for the 2024 comparison
- **`AD5L`** (SMD = +0.43, vs pre-2020 only): anxiety/depression most imbalanced EQ-5D dimension; outcome variable
- **`obese`** (SMD = −0.30): measurement artefact dominates; pending PI decision
- **`EQ-5D dimensions`** (SMD +0.10 to +0.43 vs pre-2020): DAPHNIE reports more health problems consistently; outcomes

**Variables in the current density ratio feature set:**
- **`eth4cat_Black`** (SMD = +0.245): DAPHNIE 2024 overrepresents Black respondents
- **`emp_cat_Unemployed`** (SMD = +0.237): DAPHNIE 2024 overrepresents unemployed
- **`eth4cat_White`** (SMD = −0.166): DAPHNIE 2024 underrepresents White respondents
- **`emp_cat_Employed`** (SMD = −0.086), **`smoke_ecig`** (SMD = +0.060), **`diabetes`** (SMD = −0.022), **`Sex`** (+0.043), **`age7cat`** (+0.013): all small

**Key implication:** the current 6-predictor clean feature set captures only modest distributional
shift. The largest imbalances live in variables not yet in the model (`srh`, EQ-5D, `obese`,
`alcohol_yr`, `edu_cat`). The density ratio model will likely achieve a **lower AUC than before**
and weights that do not fully align outcome distributions. `edu_cat` (+0.47) is the strongest
case for PI review — it has no known construct issue and only 0.5% missing in DAPHNIE 2024, but is **100% missing in DAPHNIE 2023** so can only enter the 2024 comparison.

**DAPHNIE 2023 pilot anomalies confirmed:**
- `emp_cat_Retired` SMD = −0.52, `emp_cat_Employed` = +0.42 (vs HSE): working-age skew
- `bmi_calc` / `bmi_cat` SMD ≈ −2.1 to −2.7 vs HSE: measurement artefact (self-reported vs nurse-measured BMI)

### Variables excluded from the density ratio model
| Variable | Reason |
|---|---|
| `edu_cat` | **Not in confirmed predictor set but analytically urgent for DAPHNIE 2024.** Within-HSE is consistent (secular trend: ~28–29% degree pre-2020 → 34% in 2022). DAPHNIE 2024 imbalance is the largest in the data: degree holders 41.4% vs ~28–29% HSE; no-qualification 2.3% vs ~21% HSE (SMD = +0.47). Only 0.5% missing in DAPHNIE 2024. **DAPHNIE 2023: 100% missing** — cannot enter that comparison at all. **PI decision needed: add to confirmed predictor set for the DAPHNIE 2024 model.** |
| `smoke_ever` | Previously excluded (three incompatible coding schemes, massive missingness). **Fixed in updated Apr 2026 data**: within-HSE inconsistency resolved — HSE waves show a gradual, plausible secular decline (54.8% → 54.5% → 52.6% → 50.8% across 2017–2022); the old anomaly was a data artefact. **Remaining concern for DAPHNIE 2024**: 10.3% missing (vs ~0.7% in HSE) — listwise deletion would drop ~540 rows (~10% of DAPHNIE 2024). DAPHNIE 2023 still anomalous at 17.6% yes (likely pilot quota artefact). **Includable for DAPHNIE 2024 vs pre-2020 HSE** pending a decision on missingness handling; the PI decision is now simpler — the within-HSE barrier is gone. |
| `smoke_ecig` | **Fixed in Apr 2026 data**: no missing values, consistent binary yes/no. **Included in current density ratio model.** DAPHNIE 2024 has higher use (22.4%) than HSE (~18%), likely a demographic composition effect. |
| `eth4cat_*` dummies | Previously miscoded ("Others" absorbed all DAPHNIE rows). **Fixed in Apr 2026 data**: proper ethnicity distribution. **Included in current density ratio model** (4 dummies). DAPHNIE overrepresents Black respondents (~9% vs ~3% HSE). |
| `age3cat` | Redundant with `age7cat` (finer granularity, strictly more informative) |
| `bmi_calc` / `bmi_cat` | Missing in DAPHNIE 2024; `obese` was the intended common proxy, but see `obese` finding above |
| `obese` | Construct shift between pre-2020 HSE (nurse-measured, ~16%) and HSE 2022 / DAPHNIE (self-reported, 7.7% / 5.7%). Most of the DAPHNIE vs pre-2020 HSE gap is measurement artefact. **PI decision needed: exclude or include with caveat.** |
| `diabetes` | Previously miscoded (HSE coded nurse-screening completion ~99% = 1). **Fixed in Apr 2026 data**: no missing values, consistent self-reported prevalence 6.9–9.2% across all waves. **Included in current density ratio model.** The SMD ≈ −5 from prior analysis was entirely an artefact. |
| `emp_cat_*` dummies | Previously all-zero for DAPHNIE 2023 and HSE 2019. **Fixed in Apr 2026 data**: <0.5% missing. **Included in current density ratio model** (5 dummies). Key imbalances in DAPHNIE 2024 vs pre-2020 HSE: unemployed overrepresented (7.8% vs ~2%), retired underrepresented (20.9% vs ~27%). DAPHNIE 2023 anomalous (76.9% employed, 4.8% retired) — narrow pilot quota. |
| `skin` | **Not collected in DAPHNIE 2023 or HSE 2019**. Including it in the density ratio model would drop all HSE 2019 rows (~8,200, ~34% of the pre-2020 target) via listwise deletion. For the DAPHNIE 2023 comparison, both source and target wave are missing it. **PI decision needed: exclude, or restrict pre-2020 target to HSE 2017–2018 only.** |
| `resp` | **Not collected in HSE 2019** (100% missing); consistent and well-harmonised everywhere else (7.8–9.1%). Same structural consequence as `skin`: including it drops ~8,200 HSE 2019 rows. Note: both `resp` and `skin` are missing in HSE 2019 — likely a deliberate instrument omission in that wave. If the PI wants to keep both, the cleanest solution is to drop HSE 2019 from the pre-2020 target entirely and use only HSE 2017–2018. **PI decision needed: exclude both, or restrict pre-2020 target to HSE 2017–2018.** |

### Wrangling audit finding (Apr 2026 — largely resolved)
The Apr 2026 data delivery fixed most harmonisation issues. Remaining open items requiring
PI decisions before they can enter the density ratio model: `alcohol_yr`, `obese`,
`resp`, `skin` (see excluded variables table above). `smoke_ever` within-HSE issue resolved —
see table for remaining missingness consideration. `PA_vig`/`PA_mod` are
DAPHNIE 2023-only and cannot enter. `edu_cat` audited (Apr 2026): large imbalance confirmed (SMD +0.47), within-HSE consistent, 0.5% missing in DAPHNIE 2024 but **100% missing in DAPHNIE 2023** — includable only for the 2024 comparison; PI decision needed to add to predictor set. `sat` not yet audited.

`wrangled_data.csv` regenerated Apr 2026: **38,995 rows × 44 columns**. Zero rows dropped
for invalid `age7cat` (pre-filtered in source). All dummy columns for `eth4cat` and
`emp_cat` confirmed present.

### Density ratio estimation (notebook 03 — Apr 2026 re-run)

**Feature set (13 variables):** `Sex`, `age7cat`, `eth4cat_Asian`, `eth4cat_Black`,
`eth4cat_Others`, `eth4cat_White`, `emp_cat_Employed`, `emp_cat_Other (Sick/Home/etc)`,
`emp_cat_Retired`, `emp_cat_Student`, `emp_cat_Unemployed`, `diabetes`, `smoke_ecig`

**Architecture:** logistic regression (primary), gradient boosting (robustness check);
`class_weight='balanced'`; 5-fold CV AUC; weights clipped at 99th percentile and
normalised to mean 1.

**AUC results:**

| Wave | LR AUC | HGB AUC |
|---|---|---|
| DAPHNIE 2023 vs pre-2020 HSE | 0.719 (±0.009) | 0.796 (±0.014) |
| DAPHNIE 2024 vs pre-2020 HSE | 0.586 (±0.004) | 0.638 (±0.008) |

DAPHNIE 2024 AUC barely above chance — confirms the current feature set captures only modest
distributional shift. HGB is now well-behaved (no longer saturates at 1.0; the old AUC = 1.0
was driven entirely by miscoded variables).

**Effective sample sizes (LR):**
- DAPHNIE 2023: 672 / 1,657 (40.6%) — driven by anomalous employment composition in the pilot
- DAPHNIE 2024: 4,691 / 5,237 (89.6%) — very high, reflecting modest detected shift

**Dominant LR coefficients:**
- DAPHNIE 2023: employment dummies dominate (|coef| up to 3.0), reflecting the working-age
  pilot skew; ethnicity coefficients large but secondary
- DAPHNIE 2024: all coefficients small (|coef| < 0.25); `emp_cat_Unemployed` and
  `eth4cat_White` are largest

**Balance after reweighting (LR):**
- DAPHNIE 2023: 4 variables remain |SMD| > 0.1 after reweighting. `Sex` worsens from
  +0.012 before to +0.262 after — extreme employment coefficients create unintended sex
  imbalance as a side effect.
- DAPHNIE 2024: 3 variables imbalanced both before and after (no net improvement). Main
  targets (`eth4cat_Black`, `emp_cat_Unemployed`) collapse to near-zero, but `age7cat`
  increases from +0.041 to +0.198 and `emp_cat_Retired` from −0.028 to +0.128 — model
  trades age/retirement balance to correct ethnicity and unemployment.

**Overall conclusion:** the current feature set is insufficient, particularly for DAPHNIE 2024.
The largest distributional differences (in `edu_cat`, `obese`, `alcohol_yr`, EQ-5D outcomes)
are outside the model. PI decisions on expanding the predictor set — especially `edu_cat`
(SMD = +0.47, no known construct issue) — are now analytically urgent before norm derivation
can proceed.

---

## Current Status

- [x] Exploratory analysis completed
- [x] Data wrangling and concatenation (`data_wrangling/02-csv_wrangling.ipynb`) — re-run Apr 2026 with cleaned source data
- [x] Within-HSE consistency check (`covariate_shift/01-covariate_comparison.ipynb`) — re-run Apr 2026; 4/27 variables imbalanced, employment now stable
- [x] DAPHNIE vs HSE 2×2 covariate comparison (`covariate_shift/02-daphnie_vs_hse.ipynb`) — re-run Apr 2026; 23 variables imbalanced in at least one comparison
- [x] Wrangling audit (Apr 2026 data delivery resolved most issues):
  - [x] `eth4cat`: fixed — proper distribution across all waves
  - [x] `emp_cat`: fixed — real categories, <0.5% missing
  - [x] `diabetes`: fixed — consistent self-reported prevalence, no missing
  - [x] `smoke_ecig`: fixed — no missing, consistent
  - [ ] `alcohol_yr`: PI decision needed (skip logic / HSE 2022 missing)
  - [ ] `obese`: PI decision needed (measurement shift nurse vs self-reported)
  - [x] `smoke_ever`: within-HSE inconsistency resolved (secular trend, not artefact); includable for DAPHNIE 2024 pending missingness handling (10.3% missing in DAPHNIE 2024)
  - [ ] `resp` + `skin`: PI decision needed (missing in HSE 2019 — drop HSE 2019 or exclude variables)
  - [ ] `PA_vig` / `PA_mod`: DAPHNIE 2023 only — exclude from density ratio
- [x] Density ratio / propensity score estimation — run Apr 2026 (13-variable clean feature set). **Results indicate feature set is insufficient** — DAPHNIE 2024 AUC = 0.586, balance not fully achieved. PI decisions on predictor expansion needed before norm derivation.
- [ ] Importance weighting and norm derivation
- [ ] Cluster analysis and community detection
- [ ] Adjusted norm comparison across datasets

---

## Technical Preferences

- **Language:** Python
- **Style:** Thoughtful, well-explained code — understanding the method matters as much as
  the implementation
- Before writing any non-trivial analysis, explain the statistical rationale first

---

## Key References / Concepts to Keep in Mind

- Covariate shift and importance weighting (Sugiyama et al.)
- Propensity score methods in survey methodology
- Louvain and Leiden community detection algorithms
- Latent Class Analysis (LCA) for probabilistic subgroup identification
- EQ-5D-5L value sets and utility scoring for the UK
