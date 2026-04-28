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

Nine outcomes in total:

| Variable | Description | Abstract scope | Missingness HSE 2017–18 | Missingness DAPHNIE 2024 |
|---|---|---|---|---|
| `MO5L` | Mobility dimension (1–5) | **Yes** | ~9.3% | ~0.3% |
| `SC5L` | Self-care dimension (1–5) | **Yes** | ~9.4% | ~0.5% |
| `UA5L` | Usual activities dimension (1–5) | **Yes** | ~9.2% | ~0.8% |
| `PD5L` | Pain/discomfort dimension (1–5) | **Yes** | ~9.8% | ~0.6% |
| `AD5L` | Anxiety/depression dimension (1–5) | **Yes** | ~10.0% | ~0.6% |
| `EQ_index` | EQ-5D-5L utility index (value set-scored) | **Yes** | ~10.9% | ~1.8% |
| `LSS_rs` | Leidelmeijer Severity Score (0–100) | **Yes** | ~10.9% | ~1.8% |
| `srh` | Self-rated health (ordinal 1–5) | Deferred to paper | ~0% | ~6.1% |
| `EQvas` | EQ Visual Analogue Scale (0–100) | Deferred to paper | ~11.5% | ~7.3% |

`FULLHEALTH` (full health vs any EQ-5D-5L problem, binary) is **not in `wrangled_data.csv`**
but is derivable in notebook 04 as `(MO5L==1) & (SC5L==1) & (UA5L==1) & (PD5L==1) & (AD5L==1)`.

**Abstract scope decision (Apr 2026):** `srh` and `EQvas` are dropped from the abstract
analysis due to time constraints and data quality concerns:
- `EQvas` has the worst completion in both datasets (worst of all outcomes) and requires
  placing oneself on a 0–100 scale — consistently the hardest item to answer
- `srh` has a reversed missingness pattern (0% in HSE, 6.1% in DAPHNIE 2024) that would
  need additional explanation; deferred to the full paper
Both variables remain in the dataset for the full paper analysis.

**EQ-5D missingness in HSE 2017–18 is not MCAR.** The ~10% block missing (1,492 respondents
missing all five dimensions) is systematically related to observed covariates: worse SRH
(SMD = −0.227, strongest predictor), lower education (SMD = −0.189), less employed
(SMD = −0.149), more Non-White (SMD = +0.129), more medications (SMD = +0.131), and a
U-shaped age pattern (youngest and oldest overrepresented). The missing group is
systematically less healthy, raising the possibility of MNAR. **Complete-case norms from
HSE 2017–18 may therefore overestimate population health.** Accepted for the abstract as
a stated limitation; missingness weighting deferred to the full paper.

---

## Predictor Variables (Covariates for Density Ratio / Adjustment)

Confirmed predictor set (PI):

`Sex`, `age7cat`, `emp_cat`, `eth4cat`, `PA_vig`, `PA_mod`, `smoke_ever`, `smoke_ecig`,
`diabetes`, `edu_cat_2`, `eth2cat`, `meds_num`, `ill_dis`

**Notebook 03 predictor set (13 variables, DAPHNIE vs pre-2020 HSE):**
`Sex`, `age7cat`, `eth2cat`, `emp_cat_Employed`, `emp_cat_Other (Sick/Home/etc)`,
`emp_cat_Retired`, `emp_cat_Student`, `emp_cat_Unemployed`, `edu_cat_2`, `smoke_ecig`,
`diabetes`, `meds_num`, `ill_dis`

**Notebook 04 predictor set (15 variables, DAPHNIE 2024 vs HSE 2017–2018):**
Same 13 variables above + `resp` + `skin`. Both are 0% missing in HSE 2017–18 and
DAPHNIE 2024. They were excluded from notebook 03 because HSE 2019 (part of the pre-2020
target) was missing them entirely; restricting the target to HSE 2017–2018 removes that
constraint.

Variables dropped from all pipelines: `obese` (measurement shift: nurse-measured in
pre-2020 HSE vs self-reported in DAPHNIE; also 18.2% missing in HSE 2017–18),
`PA_vig`/`PA_mod` (DAPHNIE 2023 only, 95.8% missing overall), `smoke_ever` (10.3%
missing in DAPHNIE 2024 — deferred), `alcohol_yr` (skip-logic artefact — kept in
dataset for future harmonisation work).

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
| `covariate_shift/011-covariate_comparison_hse.ipynb` | HSE 2017 vs HSE 2018 pairwise consistency check on the 15-variable notebook 04 predictor set (incl. `resp` and `skin`); validates pooling the two waves as the norm derivation reference | Done — Apr 2026 |
| `covariate_shift/02-daphnie_vs_hse.ipynb` | 2×2 SMD comparison: each DAPHNIE wave (2023, 2024) vs each HSE target (2022, pre-2020); Love plot | Done — re-run Apr 2026 |
| `covariate_shift/021-daphnie_vs_hse.ipynb` | Restricted SMD comparison for the norm derivation pipeline: DAPHNIE 2024 vs HSE 2017–2018 pooled, 16-variable predictor set (incl. `alcohol_yr` for characterisation); weighted means table and Love plot | Done — Apr 2026 |
| `covariate_shift/03-density_ratio.ipynb` | Classifier-based density ratio estimation — six model variants (LR, LR+Platt, LR+Venn-Abers, HGB, HGB+Isotonic, HGB+Venn-Abers) for each DAPHNIE wave vs pre-2020 HSE; calibration diagnostics (reliability diagrams, Brier, ECE); ESS and before/after balance check | Done — Apr 2026 |
| `covariate_shift/031-density_ratio.ipynb` | Restricted pipeline: same six-model architecture for DAPHNIE 2024 vs HSE 2017–2018 only; 15-variable predictor set (adds `resp` + `skin`); `alcohol_yr` included as diagnostic in balance check only; produces the weights used in notebook 04 | Done — Apr 2026 |
| `covariate_shift/04-norm_derivation.ipynb` | Restricted pipeline: density ratio re-estimated from scratch (plain LR, 15-variable predictor set, self-contained); importance-weighted population norms for 7 EQ-5D outcomes + FULLHEALTH; three-way comparison (HSE 2017–18 with `wt_int`, DAPHNIE unadjusted with `svy_wt`, DAPHNIE adjusted with `svy_wt × w_LR`) via Horvitz–Thompson weighted means with sandwich SEs; level frequency tables; dimension profile plots; weighted KDE for continuous outcomes; subgroup norms by Sex × age7cat | In progress — Apr 2026 |

---

## Key Findings from Covariate Comparison

### HSE 2022 lacks EQ-5D-5L data
HSE 2022 has no observations for the five EQ-5D-5L dimensions. This means **the
pre-2020 HSE waves (2017–2019) are the only valid HSE reference for EQ-5D norm
derivation**. HSE 2022 may still be used for sensitivity checks on variables it does
contain (e.g. employment, BMI, SRH).

### Within-HSE drift is small and largely explainable (Apr 2026 re-run)
`edu_cat` (original ordinal) dropped from the analytic set as redundant with `edu_cat_2` (binary recoding, strictly preferred). 3 of 35 variables exceed |SMD| > 0.1 (pre-2020 vs HSE 2022):

| Variable | SMD (post − pre) | Explanation |
|---|---|---|
| `alcohol_yr` | −0.418 | Skip-logic artefact also affects within-HSE comparison — further confirms exclusion from density ratio model |
| `edu_cat_2` | +0.162 | Plausible secular trend (degree holders: ~28–29% pre-2020 → 34% HSE 2022) |
| `sat` | −0.156 | Possible COVID effect on life satisfaction |

Notable changes from previous documentation: `obese` is now stable within HSE (SMD = +0.016); the measurement shift concern is specific to the DAPHNIE comparison (addressed in notebook 02). `smoke_ever` improved to SMD = −0.089 (below threshold); the secular decline is plausible and confirmed. Notably, **employment is now stable within HSE** — the large SMDs seen previously (emp_cat SMD up to 0.41) were entirely the all-zero coding artefact. EQ-5D dimensions and health outcomes are stable across the split. Pre-2020 HSE is a valid, stable reference pool for norm derivation.

**Pooling conclusion:** HSE 2017, 2018, and 2019 can be pooled as the pre-2020 reference for the predictor variables. Strictly, the notebook tests the *pooled* pre-2020 against HSE 2022 — it does not formally test wave-by-wave consistency within the pre-2020 period. However, pooling is well-supported: the three waves share the same survey design and sampling frame, and the `smoke_ever` secular trend (54.8% → 54.5% → 52.6%) confirms any within-pre-2020 drift is smooth and small. A rigorous pairwise check (2017 vs 2018 vs 2019) on the confirmed predictor set is reserved for a later stage.

### HSE 2017 vs HSE 2018 pairwise consistency (Apr 2026, notebook 011)

All 16 variables (15-variable notebook 04 predictor set + `alcohol_yr` for characterisation)
have |SMD| < 0.1 between the two waves. Maximum SMD is 0.037 (`eth2cat`); all others ≤ 0.030.
`alcohol_yr` SMD = −0.015 — well-balanced within HSE, confirming any artefact is specific to
the DAPHNIE vs HSE comparison. **Pooling HSE 2017 and HSE 2018 as the norm derivation
reference is fully supported.**

Notable missingness: `meds_num` 35.1%/41.0% missing in HSE 2017/2018 (handled by median
imputation in the density ratio classifier); `alcohol_yr` 17.1%/16.8% missing (consistent
within HSE, skip-logic artefact with DAPHNIE confirmed separately in notebook 021).

### DAPHNIE 2024 vs HSE 2017–2018: definitive covariate comparison (Apr 2026, notebook 021)

**Feature set:** 16 variables — 15-variable notebook 04 predictor set + `alcohol_yr`
(included for characterisation; excluded from the density ratio model due to skip-logic artefact).

**5 variables with |SMD| > 0.1:**

| Variable | DAPHNIE 2024 | HSE 2017–18 | SMD | Interpretation |
|---|---|---|---|---|
| `alcohol_yr` | 1.60 | 2.60 | −0.878 | Skip-logic artefact — excluded from density ratio model |
| `edu_cat_2` | 41.7% degree | 29.2% degree | +0.264 | DAPHNIE overrepresents degree holders |
| `emp_cat_Unemployed` | 7.8% | 2.8% | +0.225 | DAPHNIE overrepresents unemployed |
| `eth2cat` | 21.6% Non-White | 14.6% Non-White | +0.181 | DAPHNIE overrepresents Non-White |
| `ill_dis` | 35.1% ill/disabled | 42.5% ill/disabled | −0.152 | DAPHNIE underrepresents ill/disabled |

`skin` is just below threshold (SMD = +0.097; DAPHNIE 3.1% vs HSE 1.6%). All other
variables |SMD| < 0.08. `meds_num` near-zero (SMD = +0.034) despite being a key predictor
in notebook 03 — the main DAPHNIE 2024 bias is driven by education, unemployment,
ethnicity, and health status.

Results are consistent with notebook 02 (DAPHNIE 2024 vs pre-2020 HSE): restricting the
target to HSE 2017–2018 only does not materially change the imbalance picture.

### DAPHNIE vs HSE: main imbalanced covariates (Apr 2026 re-run)

SMDs below are DAPHNIE 2024 vs pre-2020 HSE (primary density ratio comparison) unless noted.
23 variables show |SMD| > 0.1 in at least one of the four comparisons.

**Variables excluded from covariate comparison notebooks (01 and 02) and density ratio model:**
- **`alcohol_yr`** (SMD = −0.87 D2024 vs pre-2020): skip-logic artefact, not includable as-is
- **`srh`** (SMD = −0.82): outcome, not a predictor
- **`obese`** (SMD = −0.30 vs pre-2020, ~0 vs HSE 2022): measurement artefact (nurse-measured pre-2020 vs self-reported); drop confirmed by PI
- **`EQ-5D dimensions`** (SMD +0.10 to +0.43 vs pre-2020): outcomes; NaN vs HSE 2022 (no EQ-5D in HSE 2022)
- **`eth4cat_*` dummies** (`eth4cat_Asian`, `eth4cat_Black`, `eth4cat_Others`, `eth4cat_White`): replaced by binary `eth2cat` in all notebooks; dropping them loses subgroup granularity (DAPHNIE 2024 specifically overrepresents Black respondents, SMD ≈ +0.24) but gives a cleaner, non-collinear predictor
- **`edu_cat`** (original ordinal): replaced by binary `edu_cat_2` in all notebooks; NaN for all DAPHNIE 2023 comparisons confirming the original coding had massive missingness in the pilot wave

**Confirmed density ratio predictor set (13 variables):** `Sex`, `age7cat`, `eth2cat`, `emp_cat_Employed`, `emp_cat_Other (Sick/Home/etc)`, `emp_cat_Retired`, `emp_cat_Student`, `emp_cat_Unemployed`, `edu_cat_2`, `smoke_ecig`, `diabetes`, `meds_num`, `ill_dis`

**Key imbalances in DAPHNIE 2024 vs pre-2020 HSE (primary comparison):**
- `edu_cat_2` (SMD ≈ +0.28): overrepresents degree holders (41.7% vs ~28–29% HSE)
- `eth2cat` (SMD ≈ +0.23): overrepresents Non-White respondents (21.5% vs ~13% HSE)
- `emp_cat_Unemployed` (SMD = +0.237): overrepresents unemployed (7.8% vs ~2% HSE)
- `ill_dis` (SMD = −0.153): underrepresents ill/disabled
- All other confirmed predictors: |SMD| < 0.1

**Key implication:** the confirmed 13-variable feature set captures the main distributional differences in DAPHNIE 2024. The largest remaining imbalances (`srh`, EQ-5D outcomes, `alcohol_yr`) are excluded for methodological reasons. Covariate notebooks need re-run to confirm SMDs for `edu_cat_2`, `eth2cat`, `meds_num`, and `ill_dis` with the updated analytic column set.

**DAPHNIE 2023 pilot anomalies confirmed:**
- `emp_cat_Retired` SMD = −0.52, `emp_cat_Employed` = +0.42 (vs HSE): working-age skew
- `bmi_calc` / `bmi_cat` SMD ≈ −2.1 to −2.7 vs HSE: measurement artefact (self-reported vs nurse-measured BMI)

### Variables excluded from the density ratio model
| Variable | Reason |
|---|---|
| `edu_cat_2` | **Added to confirmed predictor set (PI, Apr 2026).** Binary recoding of original `edu_cat`: Degree or equivalent vs below degree (absorbing No qualification). Within-HSE consistent (secular trend: ~28–29% degree pre-2020 → 34% HSE 2022). DAPHNIE 2024: 41.7% degree; DAPHNIE 2023: 44.5% degree; both vs ~28–29% pre-2020 HSE (SMD ≈ +0.28 binary). Missingness negligible across all waves (<0.5%). DAPHNIE 2023 missingness resolved by recoding — **includable for both wave comparisons**. |
| `meds_num` | **Added to confirmed predictor set (PI, Apr 2026).** Number of medications. Already present and audited in dataset. Distribution details to be documented after covariate comparison re-run. |
| `ill_dis` | **Added to confirmed predictor set (PI, Apr 2026).** Illness/disability indicator. Already present and audited in dataset. Distribution details to be documented after covariate comparison re-run. |
| `smoke_ever` | Previously excluded (three incompatible coding schemes, massive missingness). **Fixed in updated Apr 2026 data**: within-HSE inconsistency resolved — HSE waves show a gradual, plausible secular decline (54.8% → 54.5% → 52.6% → 50.8% across 2017–2022); the old anomaly was a data artefact. **Remaining concern for DAPHNIE 2024**: 10.3% missing (vs ~0.7% in HSE) — listwise deletion would drop ~540 rows (~10% of DAPHNIE 2024). DAPHNIE 2023 still anomalous at 17.6% yes (likely pilot quota artefact). **Includable for DAPHNIE 2024 vs pre-2020 HSE** pending a decision on missingness handling; the PI decision is now simpler — the within-HSE barrier is gone. |
| `smoke_ecig` | **Fixed in Apr 2026 data**: no missing values, consistent binary yes/no. **Included in current density ratio model.** DAPHNIE 2024 has higher use (22.4%) than HSE (~18%), likely a demographic composition effect. |
| `eth2cat` | **Added to confirmed predictor set (PI, Apr 2026).** Binary recoding of `eth4cat`: White (0) vs Non-White (1). DAPHNIE 2024: 21.5% Non-White; DAPHNIE 2023: 20.1% Non-White; pre-2020 HSE: ~13% Non-White (SMD ≈ +0.23). Within-HSE consistent (11.7–14.1%). Missingness: 0.6% DAPHNIE 2024, 8.4% DAPHNIE 2023 (~139 rows, inherited from `eth4cat`). **Includable for both wave comparisons.** Replaces the 4 `eth4cat_*` dummies from the prior model. |
| `age3cat` | Redundant with `age7cat` (finer granularity, strictly more informative) |
| `bmi_calc` / `bmi_cat` | Missing in DAPHNIE 2024; `obese` was the intended common proxy, but see `obese` finding above |
| `obese` | **Dropped from predictor set (PI decision, Apr 2026).** Differences driven by question type: nurse-measured in pre-2020 HSE (~24% obese) vs self-reported in DAPHNIE and HSE 2022 (~5.7% and ~18.1%). The DAPHNIE vs pre-2020 HSE gap is a measurement artefact, not a true population difference. Variable remains in the dataset for potential sensitivity analyses. |
| `diabetes` | Previously miscoded (HSE coded nurse-screening completion ~99% = 1). **Fixed in Apr 2026 data**: no missing values, consistent self-reported prevalence 6.9–9.2% across all waves. **Included in current density ratio model.** The SMD ≈ −5 from prior analysis was entirely an artefact. |
| `emp_cat_*` dummies | Previously all-zero for DAPHNIE 2023 and HSE 2019. **Fixed in Apr 2026 data**: <0.5% missing. **Included in current density ratio model** (5 dummies). Key imbalances in DAPHNIE 2024 vs pre-2020 HSE: unemployed overrepresented (7.8% vs ~2%), retired underrepresented (20.9% vs ~27%). DAPHNIE 2023 anomalous (76.9% employed, 4.8% retired) — narrow pilot quota. |
| `skin` | **Dropped from current pipeline (PI decision, Apr 2026).** Not collected in DAPHNIE 2023 or HSE 2019. **Reserved for a separate pipeline** restricting the pre-2020 HSE target to 2017–2018 only, which eliminates the HSE 2019 missingness constraint. |
| `resp` | **Dropped from current pipeline (PI decision, Apr 2026).** Not collected in HSE 2019 (100% missing); consistent elsewhere (7.8–9.1%). Same structural constraint as `skin`. **Reserved for the same separate pipeline** using HSE 2017–2018 as target only. |
| `alcohol_yr` | **Dropped from current pipeline (PI decision, Apr 2026).** Largest covariate imbalance (SMD = −0.87) but driven by skip-logic artefact across datasets — not includable as-is. Variable remains in the dataset for future consideration if harmonisation is possible. |

### Wrangling audit finding (Apr 2026 — largely resolved)
The Apr 2026 data delivery fixed most harmonisation issues. Remaining open items requiring
All PI decisions resolved (Apr 2026). Dropped from current pipeline: `obese` (question-type
artefact), `alcohol_yr` (skip-logic artefact), `resp` and `skin` (missing in HSE 2019 — reserved
for a separate pipeline using HSE 2017–2018 as target only). `smoke_ever` within-HSE issue
resolved — see table for remaining missingness consideration. `edu_cat_2`, `eth2cat`, `meds_num`,
and `ill_dis` audited and added to predictor set. `PA_vig`/`PA_mod` DAPHNIE 2023-only, excluded.
`sat` not yet audited.

`wrangled_data.csv` regenerated Apr 2026: **38,995 rows × 58 columns** (44 was a stale cached figure from notebook 02). Zero rows dropped for invalid `age7cat` (pre-filtered in source). `eth4cat_*` dummies and `emp_cat_*` dummies confirmed present in data but `eth4cat_*` are now excluded from all analytic notebooks in favour of binary `eth2cat`.

### Density ratio estimation (notebook 03 — Apr 2026, final results)

**Feature set (13 variables):** `Sex`, `age7cat`, `eth2cat`, `emp_cat_Employed`,
`emp_cat_Other (Sick/Home/etc)`, `emp_cat_Retired`, `emp_cat_Student`, `emp_cat_Unemployed`,
`edu_cat_2`, `smoke_ecig`, `diabetes`, `meds_num`, `ill_dis`

**Architecture:** six classifier variants fitted per wave, all using `class_weight='balanced'`
(equalises prior, so $w(x) = \hat{p}/(1-\hat{p})$ is the density ratio for every variant
without sample-size correction). 5-fold CV AUC reported for the two base models only; weights
clipped at 99th percentile and normalised to mean 1. Calibration diagnostics (reliability
diagrams, Brier score, ECE) evaluated on a stratified 80/20 hold-out of the pooled data.

| Model | Calibration method |
|---|---|
| LR | None (base) |
| LR + Platt | Sigmoid (Platt scaling) |
| LR + Venn-Abers | Cross Venn-Abers (5-fold) |
| HGB | None (base) |
| HGB + Isotonic | Isotonic regression |
| HGB + Venn-Abers | Cross Venn-Abers (5-fold) |

**AUC results (5-fold CV, base models):**

| Wave | LR AUC | HGB AUC |
|---|---|---|
| DAPHNIE 2023 vs pre-2020 HSE | 0.725 (±0.009) | 0.881 (±0.010) |
| DAPHNIE 2024 vs pre-2020 HSE | 0.648 (±0.007) | 0.819 (±0.009) |

The updated feature set substantially increased HGB AUC (DAPHNIE 2024: 0.638 → 0.819),
confirming that `edu_cat_2`, `meds_num`, and `ill_dis` contain real non-linear discriminative
signal. The LR–HGB gap is now large, especially for DAPHNIE 2024 (0.648 vs 0.819), indicating
meaningful non-linearity in the density ratio that LR cannot capture.

**Dominant LR coefficients (standardised):**
- DAPHNIE 2023: employment dummies still dominate (|coef| up to 1.57, reflecting working-age
  pilot skew); `ill_dis` (+0.427), `meds_num` (−0.337), `edu_cat_2` (−0.208) are major
  secondary drivers
- DAPHNIE 2024: `ill_dis` (+0.361), `edu_cat_2` (−0.264), `meds_num` (−0.231) now rank 1–3;
  all coefficients moderate (|coef| < 0.4) — DAPHNIE 2024 overrepresents degree holders,
  unemployed, and non-White respondents, while underrepresenting ill/disabled people

**ESS after reweighting (LR / LR+VA / HGB+VA):**
- DAPHNIE 2023 LR: ~42% — driven by extreme employment corrections
- DAPHNIE 2024 LR: ~77% — modest shift, weights remain usable
- HGB-based variants: lower ESS (~33–36%) reflecting more extreme weight distributions; Venn-Abers
  caps probabilities away from 0/1 (preventing the worst ESS collapse) but high AUC still
  implies concentrated weights

**Balance after reweighting — variables with |SMD| > 0.1:**

| Wave | Before | After LR | After LR+VA | After HGB+VA |
|---|---|---|---|---|
| DAPHNIE 2023 | 7 | 4 | **3** | 5 |
| DAPHNIE 2024 | 4 | **3** | 4 | 6 |

**AUC–balance disconnect:** HGB+VA has the highest AUC yet produces the worst balance in both
waves. This is a known phenomenon: better discrimination does not imply better balance. HGB
learns a complex non-linear decision surface that concentrates extreme weights on a small subset
of observations, correcting targeted variables while inducing new imbalances on correlated
features. High AUC is a ceiling on detectable shift, not a quality measure for the resulting
weights.

**Recommended weighting scheme:**
- DAPHNIE 2023: **LR + Venn-Abers** (3 imbalanced variables — best overall; calibration
  improves on raw LR)
- DAPHNIE 2024: **LR** plain (3 imbalanced variables — calibration adds no benefit; HGB
  degrades balance)

**Persistent imbalance in DAPHNIE 2024 (3 variables after best scheme):** this is not a
modelling failure. It reflects genuine limitations of the 13-variable feature set — some
selection mechanisms driving the 66% non-retention and online panel recruitment are either
unmeasured or excluded for methodological reasons (`alcohol_yr`, `obese`). No weighting
scheme can correct for unobserved confounders. This residual imbalance must be reported as a
limitation when deriving adjusted norms from DAPHNIE 2024.

---

### Density ratio estimation — restricted pipeline (notebook 031 — Apr 2026, final results)

**Feature set (15 variables):** notebook 03 set + `resp` + `skin`. `alcohol_yr` excluded
from model (skip-logic artefact confirmed); included in balance check as diagnostic only.

**AUC results (5-fold CV, base models):**

| Model | AUC |
|---|---|
| LR | 0.651 (±0.008) |
| HGB | 0.822 (±0.008) |

Consistent with notebook 03 (DAPHNIE 2024 vs pre-2020 HSE, 13 variables): AUC barely
changed (+0.003 LR, +0.003 HGB), confirming `resp` and `skin` add no discriminative signal.
The LR–HGB gap (0.651 vs 0.822) indicates real non-linearity in the density ratio.

**Dominant LR coefficients (standardised):** `ill_dis` (+0.391), `edu_cat_2` (−0.266),
`emp_cat_Retired` (+0.221), `meds_num` (−0.219), `emp_cat_Unemployed` (−0.177) — same
pattern as notebook 03; `resp` and `skin` are minor contributors (|coef| < 0.11).

**Calibration (80/20 hold-out, ECE):**

| Model | Brier | ECE |
|---|---|---|
| LR | 0.232 | 0.241 |
| LR + Platt | 0.172 | **0.010** |
| LR + Venn-Abers | 0.172 | **0.009** |
| HGB | 0.173 | 0.170 |
| HGB + Isotonic | 0.134 | **0.008** |
| HGB + Venn-Abers | 0.135 | 0.013 |

Raw LR ECE (0.241) is notably poor — calibration methods are important here.
LR + Platt and LR + Venn-Abers achieve near-perfect calibration (ECE < 0.01).

**ESS after reweighting (99th-pct clip):**
- LR: 3,902/5,237 (74.5%) — usable
- LR + Platt: 4,198/5,237 (80.2%) — best ESS
- LR + Venn-Abers: 3,777/5,237 (72.1%); 0 observations clipped (Venn-Abers caps probabilities naturally)
- HGB variants: 28–41% — too low for reliable norm estimation

**Balance after reweighting — variables with |SMD| > 0.1:**

| Before | After LR | After LR+VA | After HGB+VA |
|---|---|---|---|
| 4 | **3** | 4 | 7 |

**Recommended weighting scheme: plain LR** (3 residual imbalanced variables — best balance;
calibrated variants do not improve balance despite better ECE; HGB degrades balance severely).

**Residual imbalances after LR (3 variables):**
- `ill_dis`: −0.152 → +0.127 (overcorrects)
- `age7cat`: +0.046 → +0.161 (worsens — same trade-off as notebook 03)
- `emp_cat_Student`: −0.062 → −0.111 (marginal)

**`alcohol_yr` diagnostic (not in model):** SMD barely moves under any weighting scheme
(−0.878 before → −0.844 after LR). The skip-logic artefact is not corrected or worsened
by the density ratio weights — confirming exclusion from the model is safe.

**`alcohol_yr` confirmed harmful when included in model (tested, reverted):** including it
as a predictor raised LR AUC to 0.757 (artefactually), collapsed ESS to 41%, worsened
balance to 5 variables after LR, and overcorrected `alcohol_yr` to SMD +0.229. Excluding
it is the correct methodological decision.

---

### Norm Derivation Pipeline (notebook 04 — in progress Apr 2026)

**Design decisions (Apr 2026):**

- **Source:** DAPHNIE 2024 only. DAPHNIE 2023 excluded — pilot quota anomalies (76.9%
  employed, 4.8% retired), 42% ESS after reweighting, missing `skin`, 8.4% missing
  `eth2cat`. It can be characterised as a pilot in the paper but does not enter norm
  derivation.
- **Target:** HSE 2017–2018 only (n ≈ 16,173). HSE 2019 excluded because it has no
  EQ-5D outcome data.
- **Predictor set:** 15 variables (13 from notebook 03 + `resp` + `skin`; both 0% missing
  in both datasets once HSE 2019 is excluded).
- **Outcomes in scope for abstract (7):** `MO5L`, `SC5L`, `UA5L`, `PD5L`, `AD5L`,
  `EQ_index`, `LSS_rs`. `FULLHEALTH` derivable from dimensions as
  `(MO5L==1)&(SC5L==1)&(UA5L==1)&(PD5L==1)&(AD5L==1)`. `srh` and `EQvas` deferred
  to full paper.
- **Density ratio:** re-estimated from scratch within notebook 04 (self-contained — no
  dependency on notebook 031 session state). Same plain LR architecture; results should
  reproduce notebook 031 exactly (same data, same random seed).
- **Three comparison conditions:**
  - HSE 2017–18 weighted with `wt_int` (official survey weights)
  - DAPHNIE 2024 unadjusted, weighted with `svy_wt` (quota-sample design weights)
  - DAPHNIE 2024 adjusted, weighted with `svy_wt × w_LR`
- **Estimator:** Horvitz–Thompson weighted mean with sandwich SE:
  $\widehat{SE} = \sqrt{\sum_i w_i^2 (y_i - \bar{y}_w)^2 / (\sum_i w_i)^2}$
  — same formula for both means and proportions (FULLHEALTH, % any problem).
- **Outputs:**
  - Overall norms table: mean + SE for all 8 outcomes under all 3 conditions
  - % any problem (level ≥ 2) for each dimension
  - Weighted % at each level (1–5) for each dimension
  - Dimension profile plot (grouped bar per level, five panels)
  - Weighted KDE comparison for `EQ_index` and `LSS_rs`
  - Subgroup norms by Sex × age7cat (EuroQoL standard breakdown)
- **No wrangling changes needed:** all required variables already present in
  `wrangled_data.csv`. `FULLHEALTH` computed in notebook 04 from dimensions.
- **Missingness limitation:** ~10% block missing on EQ-5D in HSE 2017–18 is not MCAR
  (systematically less healthy; see Outcome Variables section). Complete-case analysis
  per outcome accepted for abstract as stated limitation.

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
  - [x] `alcohol_yr`: kept in dataset, excluded from model (skip-logic artefact; future harmonisation possible)
  - [x] `obese`: dropped from all pipelines (measurement shift nurse vs self-reported; 18.2% missing in HSE 2017–18)
  - [x] `smoke_ever`: within-HSE inconsistency resolved; excluded from notebook 04 (10.3% missing in DAPHNIE 2024)
  - [x] `resp` + `skin`: added to notebook 04 predictor set (0% missing once HSE 2019 excluded from target)
  - [x] `PA_vig` / `PA_mod`: excluded (DAPHNIE 2023 only)
- [x] Density ratio / propensity score estimation — complete Apr 2026. Six model variants (LR, LR+Platt, LR+VA, HGB, HGB+Isotonic, HGB+VA) with calibration diagnostics. **Recommended schemes:** LR+Venn-Abers for DAPHNIE 2023 (3 residual imbalanced vars), plain LR for DAPHNIE 2024 (3 residual). Persistent imbalance in DAPHNIE 2024 reflects unmeasured selection — report as limitation.
- [x] Restricted density ratio estimation (`covariate_shift/031-density_ratio.ipynb`) — DAPHNIE 2024 vs HSE 2017–2018; 15-variable predictor set. **Recommended scheme: plain LR** (3 residual imbalanced vars). Weights ready for notebook 04.
- [ ] Norm derivation (`covariate_shift/04-norm_derivation.ipynb`) — notebook written Apr 2026; three-way comparison (HSE reference, DAPHNIE unadjusted, DAPHNIE adjusted) for 7 EQ-5D outcomes + FULLHEALTH; subgroup norms by Sex × age7cat; **needs first run and results review**
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
