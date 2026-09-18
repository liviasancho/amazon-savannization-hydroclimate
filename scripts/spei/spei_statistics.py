"""Statistical core for SPEI using the classical three-parameter log-logistic fit.

The implementation follows the parameterisation used by the R SPEI package:
climatic water balance -> rectangular accumulation -> calendar-month fit ->
Generalized Logistic (called log-Logistic by SPEI) fitted with unbiased PWMs ->
CDF -> standard normal variate.
"""

from __future__ import annotations

import numpy as np
import xarray as xr

try:
    import dask.array  # noqa: F401
    HAS_DASK = True
except ImportError:
    HAS_DASK = False
from scipy.special import expit, ndtri

PARAMETER_NAMES = ("xi", "alpha", "kappa")


def _fit_glo_ub_pwm_nd(values: np.ndarray) -> np.ndarray:
    """Fit GLO/log-logistic parameters along the last axis using unbiased PWMs.

    Parameters
    ----------
    values
        Array with the calibration sample on the last axis. The intended sample
        is one calendar month across all calibration years (30 values for
        1981-2010 in this project).

    Returns
    -------
    np.ndarray
        Same leading dimensions as ``values`` plus a final parameter dimension
        [xi, alpha, kappa]. Invalid fits are returned as NaN.
    """
    x = np.asarray(values, dtype=np.float64)
    n = x.shape[-1]
    out_shape = x.shape[:-1] + (3,)
    out = np.full(out_shape, np.nan, dtype=np.float64)

    if n < 4:
        return out

    complete = np.all(np.isfinite(x), axis=-1)
    if not np.any(complete):
        return out

    xs = np.sort(x, axis=-1)
    i = np.arange(n, dtype=np.float64)  # i = j-1 for ordered observation j=1..n

    # Unbiased probability-weighted moments beta_r, r=0,1,2.
    w1 = i / (n - 1)
    w2 = i * (i - 1) / ((n - 1) * (n - 2))

    b0 = np.mean(xs, axis=-1)
    b1 = np.sum(xs * w1, axis=-1) / n
    b2 = np.sum(xs * w2, axis=-1) / n

    # PWMs -> L-moments.
    l1 = b0
    l2 = 2.0 * b1 - b0
    l3 = 6.0 * b2 - 6.0 * b1 + b0

    with np.errstate(divide="ignore", invalid="ignore"):
        tau3 = l3 / l2
        kappa = -tau3

    valid = complete & np.isfinite(l1) & np.isfinite(l2) & np.isfinite(kappa)
    valid &= l2 > 0.0
    # For the GLO distribution with finite first L-moment, |kappa| < 1.
    valid &= np.abs(kappa) < 1.0

    small = np.abs(kappa) < 1e-7
    alpha = np.full_like(l1, np.nan, dtype=np.float64)
    xi = np.full_like(l1, np.nan, dtype=np.float64)

    # Limit at kappa -> 0 is the ordinary logistic distribution.
    alpha[small & valid] = l2[small & valid]
    xi[small & valid] = l1[small & valid]

    regular = (~small) & valid
    if np.any(regular):
        kr = kappa[regular]
        sinpk = np.sin(np.pi * kr)
        ar = l2[regular] * sinpk / (np.pi * kr)
        xir = l1[regular] - ar * (1.0 / kr - np.pi / sinpk)
        alpha[regular] = ar
        xi[regular] = xir

    valid &= np.isfinite(alpha) & (alpha > 0.0) & np.isfinite(xi)

    out[..., 0] = np.where(valid, xi, np.nan)
    out[..., 1] = np.where(valid, alpha, np.nan)
    out[..., 2] = np.where(valid, kappa, np.nan)
    return out


def fit_loglogistic_ub_pwm(calibration: xr.DataArray) -> xr.DataArray:
    """Fit [xi, alpha, kappa] independently at every grid cell.

    ``calibration`` must contain one calendar month's values with ``time`` as
    a dimension. Missing calibration values invalidate the fit for that cell.
    """
    if HAS_DASK:
        calibration = calibration.chunk({"time": -1})
    params = xr.apply_ufunc(
        _fit_glo_ub_pwm_nd,
        calibration,
        input_core_dims=[["time"]],
        output_core_dims=[["parameter"]],
        vectorize=False,
        dask="parallelized",
        output_dtypes=[np.float64],
        dask_gufunc_kwargs={"output_sizes": {"parameter": 3}},
    )
    return params.assign_coords(parameter=list(PARAMETER_NAMES))


def _glo_to_standard_normal(
    x: np.ndarray, xi: np.ndarray, alpha: np.ndarray, kappa: np.ndarray
) -> np.ndarray:
    """Transform GLO/log-logistic variates to standard-normal SPEI."""
    x = np.asarray(x, dtype=np.float64)
    xi = np.asarray(xi, dtype=np.float64)
    alpha = np.asarray(alpha, dtype=np.float64)
    kappa = np.asarray(kappa, dtype=np.float64)

    z = (x - xi) / alpha
    small = np.abs(kappa) < 1e-7

    y = np.full(np.broadcast_shapes(x.shape, xi.shape, alpha.shape, kappa.shape), np.nan)
    xb, xib, ab, kb, zb, sb = np.broadcast_arrays(x, xi, alpha, kappa, z, small)
    valid_params = np.isfinite(xib) & np.isfinite(ab) & (ab > 0) & np.isfinite(kb)
    valid_x = np.isfinite(xb)

    logistic_mask = valid_params & valid_x & sb
    y[logistic_mask] = zb[logistic_mask]

    reg = valid_params & valid_x & (~sb)
    arg = 1.0 - kb * zb
    inside = reg & (arg > 0.0)
    y[inside] = -np.log(arg[inside]) / kb[inside]

    p = np.full_like(y, np.nan, dtype=np.float64)
    p[np.isfinite(y)] = expit(y[np.isfinite(y)])

    # Outside the finite support of the GLO distribution.
    above = reg & (arg <= 0.0) & (kb > 0.0)
    below = reg & (arg <= 0.0) & (kb < 0.0)
    p[above] = 1.0
    p[below] = 0.0

    # Avoid +/- infinity in NetCDF while staying at machine precision.
    eps = np.finfo(np.float64).eps
    finite_p = np.isfinite(p)
    p[finite_p] = np.clip(p[finite_p], eps, 1.0 - eps)

    result = np.full_like(p, np.nan, dtype=np.float64)
    result[finite_p] = ndtri(p[finite_p])
    return result


def transform_with_params(data: xr.DataArray, params: xr.DataArray) -> xr.DataArray:
    """Transform accumulated climatic water balance to SPEI."""
    xi = params.sel(parameter="xi", drop=True)
    alpha = params.sel(parameter="alpha", drop=True)
    kappa = params.sel(parameter="kappa", drop=True)
    return xr.apply_ufunc(
        _glo_to_standard_normal,
        data,
        xi,
        alpha,
        kappa,
        input_core_dims=[[], [], [], []],
        output_core_dims=[[]],
        vectorize=False,
        dask="parallelized",
        output_dtypes=[np.float64],
    )


def calculate_spei(
    monthly_balance: xr.DataArray,
    *,
    scale: int,
    calibration_start: str = "1981-01-01",
    calibration_end: str = "2010-12-31",
) -> tuple[xr.DataArray, xr.DataArray]:
    """Calculate SPEI for a monthly climatic water balance.

    Returns both SPEI and the 12 sets of fitted parameters.
    """
    if scale < 1:
        raise ValueError("scale must be >= 1")

    accumulated = monthly_balance.rolling(time=scale, min_periods=scale).sum()
    calibration = accumulated.sel(time=slice(calibration_start, calibration_end))

    month_results: list[xr.DataArray] = []
    month_params: list[xr.DataArray] = []

    for month in range(1, 13):
        cal_month = calibration.where(calibration.time.dt.month == month, drop=True)
        if cal_month.sizes.get("time", 0) == 0:
            raise ValueError(f"No calibration values found for calendar month {month}")

        params = fit_loglogistic_ub_pwm(cal_month).expand_dims(month=[month])
        month_params.append(params)

        data_month = accumulated.where(accumulated.time.dt.month == month, drop=True)
        transformed = transform_with_params(data_month, params.squeeze("month", drop=True))
        month_results.append(transformed)

    spei = xr.concat(month_results, dim="time").sortby("time").rename(f"spei_{scale}")
    params = xr.concat(month_params, dim="month").rename(f"spei_{scale}_parameters")
    return spei, params

