# HSE vs DAPHNIE as Covariate Shift

## Objective

Treat the distinction between HSE and DAPHNIE as a domain adaptation problem. The immediate task is to determine whether the two datasets differ in their background covariate distributions, and whether that difference can be handled as covariate shift for downstream prediction.

The downstream targets of interest are:

- `LSS_rs`
- `EQ_index`
- `EQvas`

## Working Assumption

The covariate-shift hypothesis is:

\[
p_{\text{HSE}}(x) \neq p_{\text{DAPHNIE}}(x), \qquad
p(y \mid x, \text{HSE}) \approx p(y \mid x, \text{DAPHNIE})
\]

where:

- `x` is a set of background covariates
- `y` is one of `LSS_rs`, `EQ_index`, or `EQvas`

This is a useful starting point, but it is still an assumption to be checked rather than accepted. The surveys differ by source and year, so concept shift remains possible even if covariate shift is present.

## Domain Label

Create a binary domain label:

- `HSE` for HSE 2017 and HSE 2018
- `DAPHNIE` for DAPHNIE 2023 and DAPHNIE 2024

This label is used only for the domain-classification stage.

## Covariates to Keep

Use only variables that are plausibly pre-outcome background characteristics for the domain classifier:

- `age7cat`
- `Sex`
- `eth4cat`
- `emp_cat`
- `edu_cat`
- `educ_pst`
- `smoke_ever`
- `smoke_ecig`
- `alcohol_yr`
- `diabetes`
- `obese`
- `resp`
- `bowel`
- `mus`
- `skin`

These variables support the interpretation that the classifier is learning differences in the source populations rather than differences in the outcomes themselves.

## Variables to Exclude

Exclude direct identifiers and target or near-target variables from the domain classifier:

- identifiers: `dataset`, `type`
- downstream targets: `LSS_rs`, `EQ_index`, `EQvas`
- EQ-5D dimensions: `MO5L`, `SC5L`, `UA5L`, `PD5L`, `AD5L`
- recoded EQ-5D dimensions: `mo2cat`, `sc2cat`, `ua2cat`, `pd2cat`, `ad2cat`
- summary variables derived from EQ-5D: `FULLHEALTH`, `anyprob`, `util_rowen`
- nearby subjective outcomes: `srh`, `sat`

The reason for excluding these variables is to avoid leakage. If the domain classifier uses health outcomes or variables that are close proxies for them, then high domain discrimination would no longer support a clean covariate-shift interpretation.

## Analytical Plan

1. Restrict the data to HSE 2017-2018 and DAPHNIE 2023-2024.
2. Build a feature matrix from the admissible background covariates.
3. Fit a domain classifier to predict `HSE` versus `DAPHNIE`.
4. Evaluate domain separability with cross-validated ROC AUC.
5. Inspect the fitted model to identify which covariates drive the separation.
6. Convert predicted domain probabilities into importance weights for transfer.
7. Use those weights in downstream models for `LSS_rs`, `EQ_index`, and `EQvas`.
8. Compare weighted versus unweighted transfer performance.

## Interpretation

- If the domain classifier is close to chance, the two datasets are not strongly separable on the selected covariates.
- If the classifier separates the domains well, there is evidence that the marginal covariate distributions differ.
- If reweighting improves transfer to the target domain, the covariate-shift framing is supported.
- If transfer remains poor after reweighting, then the discrepancy is likely not explained by covariate shift alone.

## Immediate Notebook Goal

The next notebook cells should do four things:

1. define the covariates used for domain classification
2. prepare a clean modeling table with missing-value handling delegated to the preprocessing pipeline
3. estimate how separable HSE and DAPHNIE are under those covariates
4. produce observation weights that can later be used for the downstream targets