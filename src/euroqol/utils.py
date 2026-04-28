import numpy as np
import pandas as pd

from venn_abers.venn_abers import VennAbersCV
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import brier_score_loss
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

def weighted_mean(series: pd.Series, weights: pd.Series) -> float:
    """Compute the weighted mean of a series, ignoring missing values.

    Parameters
    ----------
    series : pd.Series
        Values to average.
    weights : pd.Series
        Importance weights; observations with NaN or non-positive weights are excluded.

    Returns
    -------
    float
        Weighted mean, or np.nan if no valid observations remain.
    """
    mask = series.notna() & weights.notna() & (weights > 0)
    if mask.sum() == 0:
        return np.nan
    s, w = series[mask], weights[mask]
    return np.average(s, weights=w)


def weighted_var(series: pd.Series, weights: pd.Series) -> float:
    """Compute the weighted variance of a series, ignoring missing values.

    Parameters
    ----------
    series : pd.Series
        Values whose variance is computed.
    weights : pd.Series
        Importance weights; observations with NaN or non-positive weights are excluded.

    Returns
    -------
    float
        Weighted variance, or np.nan if fewer than two valid observations remain.
    """
    mask = series.notna() & weights.notna() & (weights > 0)
    if mask.sum() < 2:
        return np.nan
    s, w = series[mask], weights[mask]
    mu = np.average(s, weights=w)
    return np.average((s - mu) ** 2, weights=w)


def compute_smd(source_series: pd.Series, source_weights: pd.Series, target_series: pd.Series, target_weights: pd.Series) -> float:
    """Compute the standardised mean difference (SMD) between source and target distributions.

    SMD is defined as (mean_source − mean_target) / pooled_SD, where pooled_SD is the
    square root of the arithmetic mean of the two weighted variances.  A positive value
    indicates the source mean exceeds the target mean.

    Parameters
    ----------
    source_series : pd.Series
        Values from the source (online panel) dataset.
    source_weights : pd.Series
        Importance weights for the source observations.
    target_series : pd.Series
        Values from the target (HSE) dataset.
    target_weights : pd.Series
        Importance weights for the target observations.

    Returns
    -------
    float
        SMD, or np.nan if weighted means or variances cannot be computed, or if
        the pooled standard deviation is zero.
    """
    mu_s = weighted_mean(source_series, source_weights)
    mu_t = weighted_mean(target_series, target_weights)
    if np.isnan(mu_s) or np.isnan(mu_t):
        return np.nan
    var_s = weighted_var(source_series, source_weights)
    var_t = weighted_var(target_series, target_weights)
    if np.isnan(var_s) or np.isnan(var_t):
        return np.nan
    pooled_sd = np.sqrt((var_s + var_t) / 2)
    if pooled_sd == 0:
        return np.nan
    return (mu_s - mu_t) / pooled_sd

class VennAbersWrapper(VennAbersCV):
    """
    VennAbersCV with DataFrame-safe fit/predict_proba.
    VennAbersCV uses integer-positional indexing internally, which breaks on
    pandas DataFrames with named columns — this wrapper converts inputs to numpy.
    """
    def fit(self, X, y, **kwargs):
        return super().fit(np.asarray(X), np.asarray(y), **kwargs)

    def predict_proba(self, X, **kwargs):
        return super().predict_proba(np.asarray(X), **kwargs)


def fit_classifiers(daphnie_df, hse_df, features):
    """
    Pool DAPHNIE (label=0) and HSE (label=1), fit six classifier variants
    (raw + two calibrated methods for both LR and HGB).

    All models use class_weight='balanced', equalising the prior on both classes.
    The density ratio is therefore w(x) = p_hat/(1-p_hat) for all variants,
    including calibrated ones — no sample-size correction needed.

    Returns a dict of fitted models, 5-fold CV AUC for the two base classifiers,
    and the pooled feature matrix X and labels y.
    """
    src = daphnie_df[features].copy().assign(_label=0)
    tgt = hse_df[features].copy().assign(_label=1)
    pooled = pd.concat([src, tgt], ignore_index=True)

    X, y = pooled[features], pooled["_label"]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    lr_proto = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("clf",     LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42
        )),
    ])
    hgb_proto = HistGradientBoostingClassifier(
        max_iter=300, class_weight="balanced", random_state=42
    )

    auc_lr  = cross_val_score(lr_proto,  X, y, cv=cv, scoring="roc_auc")
    auc_hgb = cross_val_score(hgb_proto, X, y, cv=cv, scoring="roc_auc")

    models = {
        "LR":               clone(lr_proto),
        "LR + Platt":       CalibratedClassifierCV(clone(lr_proto),  method="sigmoid",  cv=5),
        "LR + Venn-Abers":  VennAbersWrapper(clone(lr_proto),  inductive=False, n_splits=5, shuffle=True, random_state=42),
        "HGB":              clone(hgb_proto),
        "HGB + Isotonic":   CalibratedClassifierCV(clone(hgb_proto), method="isotonic", cv=5),
        "HGB + Venn-Abers": VennAbersWrapper(clone(hgb_proto), inductive=False, n_splits=5, shuffle=True, random_state=42),
    }

    for clf in models.values():
        clf.fit(X, y)

    return models, auc_lr, auc_hgb, X, y


def compute_weights(clf, daphnie_X, clip_percentile=99):
    """
    Density ratio weights for DAPHNIE observations.
    w(x) = p_hat / (1 - p_hat), normalised to mean 1, clipped at clip_percentile.
    Works with any sklearn-compatible classifier.
    """
    p_hat = clf.predict_proba(daphnie_X)[:, 1]
    eps = 1e-8
    w = p_hat / (1 - p_hat + eps)
    w = w / w.mean()

    clip_val = np.percentile(w, clip_percentile)
    n_clipped = (w > clip_val).sum()
    w = np.clip(w, 0, clip_val)
    w = w / w.mean()

    n_eff = w.sum() ** 2 / (w ** 2).sum()
    return w, clip_val, n_clipped, n_eff

def ece_score(y_true, y_prob, n_bins=10):
    """Expected Calibration Error — binning-based."""
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() == 0:
            continue
        ece += mask.sum() / n * abs(y_true[mask].mean() - y_prob[mask].mean())
    return ece


def run_calibration_diagnostics(daphnie_df, hse_df, features):
    """
    Calibration assessment via a stratified 80/20 hold-out split on pooled data.
    Fits all six model variants on the 80% training split; evaluates reliability,
    Brier score, and ECE on the held-out 20%. Diagnostics only — not used for weights.
    """
    src = daphnie_df[features].copy().assign(_label=0)
    tgt = hse_df[features].copy().assign(_label=1)
    pooled = pd.concat([src, tgt], ignore_index=True)
    X_all, y_all = pooled[features], pooled["_label"]

    X_tr, X_cal, y_tr, y_cal = train_test_split(
        X_all, y_all, test_size=0.2, stratify=y_all, random_state=42
    )

    lr_proto = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("clf",     LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ])
    hgb_proto = HistGradientBoostingClassifier(
        max_iter=300, class_weight="balanced", random_state=42
    )

    diag_models = {
        "LR":               clone(lr_proto),
        "LR + Platt":       CalibratedClassifierCV(clone(lr_proto),  method="sigmoid",  cv=5),
        "LR + Venn-Abers":  VennAbersWrapper(clone(lr_proto),  inductive=False, n_splits=5, shuffle=True, random_state=42),
        "HGB":              clone(hgb_proto),
        "HGB + Isotonic":   CalibratedClassifierCV(clone(hgb_proto), method="isotonic", cv=5),
        "HGB + Venn-Abers": VennAbersWrapper(clone(hgb_proto), inductive=False, n_splits=5, shuffle=True, random_state=42),
    }

    for clf in diag_models.values():
        clf.fit(X_tr, y_tr)

    probs, rows = {}, []
    for name, clf in diag_models.items():
        p = clf.predict_proba(X_cal)[:, 1]
        probs[name] = p
        rows.append({
            "Model":       name,
            "Brier score": brier_score_loss(y_cal, p),
            "ECE":         ece_score(y_cal.values, p),
        })

    return probs, y_cal.values, pd.DataFrame(rows).set_index("Model")