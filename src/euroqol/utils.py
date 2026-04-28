import numpy as np
import pandas as pd

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