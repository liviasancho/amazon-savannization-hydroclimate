#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hydroclimatic changes linked to atmospheric circulation
Revised analysis pipeline with Mann–Kendall trend maps
=======================================================

This script combines:
  1) SPEI-1, SPEI-3, SPEI-6 and SPEI-12 monthly NetCDF files;
  2) Daily atmospheric-blocking series;
  3) Optional hotspot polygons.

Main analyses
-------------
A. Spatial Mann–Kendall trends of SPEI:
   - monthly SPEI is aggregated to an ANNUAL metric at each grid cell;
   - Mann–Kendall is applied independently to each pixel;
   - the final map shows ONLY statistically significant trends;
   - map values are Kendall's tau:
       tau < 0 -> red  (negative trend)
       tau > 0 -> blue (positive trend)

B. Mann–Kendall trends of atmospheric blocking:
   - daily blocking is aggregated to annual blocked-day fraction;
   - Mann–Kendall is applied separately to each blocking region;
   - the figure shows Kendall's tau by region:
       significant positive -> blue
       significant negative -> red
       non-significant       -> gray

C. Blocking–SPEI relationships:
   - monthly blocking frequency vs regional/hotspot SPEI;
   - Pearson and Spearman associations;
   - lags of 0–3 months by default.

D. Spatial blocking–SPEI correlation maps.

E. SPEI composite maps for high- vs low-blocking months.

Statistical note
----------------
This script implements the CLASSICAL Mann–Kendall test with tie correction.
It does not apply pre-whitening or an autocorrelation-corrected modified
Mann–Kendall test. For this reason, the trend test is applied to annual
aggregates rather than directly to the monthly series.

Default SPEI trend metric
-------------------------
The default spatial trend uses the annual mean SPEI at each pixel.

Alternative metrics can be selected with:
    --spei-trend-metric annual_mean
    --spei-trend-metric annual_min
    --spei-trend-metric dry_months

For dry_months, the number of months per year with SPEI <= --spei-threshold
is used.
"""

from __future__ import annotations

import argparse
import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from matplotlib.colors import TwoSlopeNorm
from scipy.stats import norm, pearsonr, spearmanr

try:
    from shapely import contains_xy
except ImportError as exc:
    raise ImportError(
        "This script requires Shapely >= 2.0 because it uses shapely.contains_xy."
    ) from exc


# =============================================================================
# USER CONFIGURATION
# =============================================================================

SPEI_VARIABLES = {
    1: "spei_1",
    3: "spei_3",
    6: "spei_6",
    12: "spei_12",
}

BLOCKING_REGIONS = [
    "total",
    "north",
    "north_h1",
    "north_h2",
    "south",
    "south_h1",
    "south_h2",
]

SPEI_EVENT_THRESHOLD = -1.0
DEFAULT_ALPHA = 0.05

LOW_BLOCKING_QUANTILE = 0.25
HIGH_BLOCKING_QUANTILE = 0.75

BLOCKING_TO_SPEI_LAGS = [0, 1, 2, 3]


# =============================================================================
# GENERAL UTILITIES
# =============================================================================

def ensure_output_dirs(base_dir: Path) -> dict[str, Path]:
    """Create output folders."""
    dirs = {
        "tables": base_dir / "tables",
        "figures": base_dir / "figures",
        "netcdf": base_dir / "netcdf",
        "diagnostics": base_dir / "diagnostics",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def find_coord_name(da: xr.DataArray, candidates: list[str]) -> str:
    """Return the first existing coordinate name from candidates."""
    for name in candidates:
        if name in da.coords:
            return name
    raise KeyError(f"None of these coordinate names were found: {candidates}")


# =============================================================================
# CLASSICAL MANN–KENDALL TEST
# =============================================================================

def mann_kendall_test_1d(values: np.ndarray, alpha: float = 0.05) -> tuple:
    """
    Classical Mann–Kendall test for a one-dimensional time series.

    Returns
    -------
    tau : float
        Kendall's tau calculated as S / [n(n-1)/2].
    p_value : float
        Two-sided p-value based on the asymptotic normal distribution of S,
        including tie correction.
    significant : bool
        True if p_value < alpha.
    n : int
        Number of valid observations.

    Method
    ------
    S = sum(sign(x_j - x_i)) for all j > i

    Var(S) includes correction for tied groups:
        Var(S) = [n(n-1)(2n+5) - sum(t(t-1)(2t+5))] / 18

    Z uses continuity correction:
        if S > 0: Z = (S - 1) / sqrt(Var(S))
        if S = 0: Z = 0
        if S < 0: Z = (S + 1) / sqrt(Var(S))

    IMPORTANT
    ---------
    This is the classical Mann–Kendall test. It does not correct for serial
    autocorrelation.
    """
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size

    if n < 5:
        return np.nan, np.nan, False, n

    # Mann–Kendall S statistic.
    s = 0
    for i in range(n - 1):
        s += np.sign(x[i + 1:] - x[i]).sum()

    # Tie correction.
    _, counts = np.unique(x, return_counts=True)
    tie_counts = counts[counts > 1]

    var_s = (
        n * (n - 1) * (2 * n + 5)
        - np.sum(tie_counts * (tie_counts - 1) * (2 * tie_counts + 5))
    ) / 18.0

    if var_s <= 0:
        return np.nan, np.nan, False, n

    if s > 0:
        z = (s - 1.0) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1.0) / np.sqrt(var_s)
    else:
        z = 0.0

    p_value = 2.0 * (1.0 - norm.cdf(abs(z)))

    denominator = n * (n - 1) / 2.0
    tau = s / denominator

    significant = bool(p_value < alpha)

    return float(tau), float(p_value), significant, int(n)


def _mk_tau(values: np.ndarray, alpha: float) -> float:
    return mann_kendall_test_1d(values, alpha)[0]


def _mk_p(values: np.ndarray, alpha: float) -> float:
    return mann_kendall_test_1d(values, alpha)[1]


def _mk_sig(values: np.ndarray, alpha: float) -> bool:
    return mann_kendall_test_1d(values, alpha)[2]


def mann_kendall_grid(
    annual_da: xr.DataArray,
    alpha: float = 0.05,
) -> xr.Dataset:
    """
    Apply the classical Mann–Kendall test independently to every grid cell.

    Parameters
    ----------
    annual_da
        DataArray with dimensions year x latitude x longitude.
    alpha
        Significance level.

    Returns
    -------
    Dataset containing:
      tau
      p_value
      significant
      tau_significant

    tau_significant contains NaN for non-significant pixels and is therefore
    directly suitable for the requested trend map.
    """
    if "year" not in annual_da.dims:
        raise ValueError("annual_da must contain a 'year' dimension.")

    # IMPORTANT:
    # 'year' is the core dimension passed to apply_ufunc.
    # Dask requires the entire time series of each pixel to be contained
    # in a single chunk along this dimension.
    annual_da = annual_da.chunk({"year": -1})

    tau = xr.apply_ufunc(
        _mk_tau,
        annual_da,
        input_core_dims=[["year"]],
        output_core_dims=[[]],
        vectorize=True,
        dask="parallelized",
        kwargs={"alpha": alpha},
        output_dtypes=[float],
    )

    p_value = xr.apply_ufunc(
        _mk_p,
        annual_da,
        input_core_dims=[["year"]],
        output_core_dims=[[]],
        vectorize=True,
        dask="parallelized",
        kwargs={"alpha": alpha},
        output_dtypes=[float],
    )

    significant = xr.apply_ufunc(
        _mk_sig,
        annual_da,
        input_core_dims=[["year"]],
        output_core_dims=[[]],
        vectorize=True,
        dask="parallelized",
        kwargs={"alpha": alpha},
        output_dtypes=[bool],
    )

    tau_sig = tau.where(significant)

    ds = xr.Dataset(
        {
            "tau": tau,
            "p_value": p_value,
            "significant": significant,
            "tau_significant": tau_sig,
        }
    )

    ds.attrs.update(
        {
            "trend_test": "Classical Mann-Kendall with tie correction",
            "significance_level": alpha,
            "trend_metric": "Kendall tau",
            "note": (
                "tau_significant contains only pixels with p < alpha. "
                "No serial-autocorrelation correction was applied."
            ),
        }
    )

    return ds.compute()


# =============================================================================
# BLOCKING DATA
# =============================================================================

def read_daily_blocking(path: Path) -> pd.DataFrame:
    """Read and validate the daily blocking CSV."""
    df = pd.read_csv(path, parse_dates=["time"])

    expected = {"time", *BLOCKING_REGIONS}
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"Missing blocking columns: {sorted(missing)}")

    df = df.sort_values("time").reset_index(drop=True)

    if df["time"].duplicated().any():
        raise ValueError("Duplicated dates found in daily blocking series.")

    expected_dates = pd.date_range(df["time"].min(), df["time"].max(), freq="D")
    if (
        len(expected_dates) != len(df)
        or not np.array_equal(expected_dates.values, df["time"].values)
    ):
        raise ValueError("Missing dates found in daily blocking series.")

    for region in BLOCKING_REGIONS:
        unique_values = set(df[region].dropna().unique())
        if not unique_values.issubset({0, 1}):
            raise ValueError(
                f"Blocking region '{region}' contains values other than 0/1."
            )

    return df


def blocking_monthly_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily blocking to monthly blocked-day frequency."""
    output = []

    for region in BLOCKING_REGIONS:
        tmp = (
            daily.set_index("time")[region]
            .resample("MS")
            .agg(["sum", "count"])
            .rename(columns={"sum": "blocked_days", "count": "days_in_record"})
            .reset_index()
        )
        tmp["blocked_fraction"] = tmp["blocked_days"] / tmp["days_in_record"]
        tmp["region"] = region
        output.append(tmp)

    return pd.concat(output, ignore_index=True)


def blocking_annual_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily blocking to annual blocked-day frequency.

    The primary trend variable is blocked_fraction:
        number of blocked days / number of available days in the year.
    """
    output = []

    for region in BLOCKING_REGIONS:
        tmp = daily[["time", region]].copy()
        tmp["year"] = tmp["time"].dt.year

        annual = (
            tmp.groupby("year")[region]
            .agg(["sum", "count"])
            .rename(columns={"sum": "blocked_days", "count": "days_in_record"})
            .reset_index()
        )
        annual["blocked_fraction"] = (
            annual["blocked_days"] / annual["days_in_record"]
        )
        annual["region"] = region

        output.append(annual)

    return pd.concat(output, ignore_index=True)


def blocking_mk_trends(
    annual: pd.DataFrame,
    alpha: float,
) -> pd.DataFrame:
    """Mann–Kendall trend of annual blocked-day fraction for each region."""
    rows = []

    for region in BLOCKING_REGIONS:
        subset = annual.loc[annual["region"] == region].sort_values("year")

        tau, p_value, significant, n = mann_kendall_test_1d(
            subset["blocked_fraction"].values,
            alpha=alpha,
        )

        rows.append(
            {
                "region": region,
                "n_years": n,
                "tau": tau,
                "p_value": p_value,
                "significant": significant,
                "trend_direction": (
                    "positive" if significant and tau > 0
                    else "negative" if significant and tau < 0
                    else "not significant"
                ),
            }
        )

    return pd.DataFrame(rows)


# =============================================================================
# SPEI DATA
# =============================================================================

def open_spei(path: Path, scale: int) -> xr.DataArray:
    """Open one SPEI NetCDF lazily."""
    ds = xr.open_dataset(path, chunks={"time": -1})

    variable = SPEI_VARIABLES[scale]
    if variable not in ds:
        raise KeyError(
            f"Variable '{variable}' not found in {path}. "
            f"Available variables: {list(ds.data_vars)}"
        )

    da = ds[variable]

    lat_name = find_coord_name(da, ["latitude", "lat"])
    lon_name = find_coord_name(da, ["longitude", "lon"])

    rename = {}
    if lat_name != "latitude":
        rename[lat_name] = "latitude"
    if lon_name != "longitude":
        rename[lon_name] = "longitude"

    if rename:
        da = da.rename(rename)

    return da


def aggregate_spei_annual(
    da: xr.DataArray,
    metric: str,
    threshold: float,
) -> xr.DataArray:
    """
    Convert monthly SPEI to an annual metric for pixel-wise trend analysis.

    Options
    -------
    annual_mean:
        Mean SPEI of all available months in each year.

    annual_min:
        Minimum SPEI in each year.

    dry_months:
        Number of months per year with SPEI <= threshold.

    Why aggregate annually?
    -----------------------
    The Mann–Kendall test is intended for monotonic trends. Applying it directly
    to a monthly sequence can mix trend, seasonality and serial persistence.
    Annual aggregation provides a clearer long-term trend diagnostic.
    """
    grouped = da.groupby("time.year")

    if metric == "annual_mean":
        annual = grouped.mean("time", skipna=True)
        annual.name = "annual_mean_spei"
        annual.attrs["long_name"] = "Annual mean SPEI"

    elif metric == "annual_min":
        annual = grouped.min("time", skipna=True)
        annual.name = "annual_minimum_spei"
        annual.attrs["long_name"] = "Annual minimum SPEI"

    elif metric == "dry_months":
        annual = (da <= threshold).groupby("time.year").sum("time")
        annual.name = "annual_number_of_low_spei_months"
        annual.attrs["long_name"] = (
            f"Annual number of months with SPEI <= {threshold}"
        )

    else:
        raise ValueError(
            "metric must be one of: annual_mean, annual_min, dry_months"
        )

    return annual


# =============================================================================
# OPTIONAL HOTSPOTS
# =============================================================================

def read_hotspots(shapefile: Path, hotspot_id_field: str) -> gpd.GeoDataFrame:
    """
    Read optional hotspot polygons and convert them to WGS84.

    NOTE:
    This optional feature still uses GeoPandas/pyproj because hotspot files may
    use arbitrary CRSs and may require reprojection. If --hotspots-shapefile is
    not supplied, the Legal Amazon cartography does not depend on pyproj.
    """
    gdf = gpd.read_file(shapefile)

    if gdf.crs is None:
        raise ValueError("Hotspot shapefile has no CRS.")

    gdf = gdf.to_crs("EPSG:4326")

    if hotspot_id_field not in gdf.columns:
        raise KeyError(
            f"Field '{hotspot_id_field}' not found. "
            f"Available fields: {list(gdf.columns)}"
        )

    return gdf


def make_polygon_mask(da: xr.DataArray, geometry) -> xr.DataArray:
    """Create a boolean mask using grid-cell centers."""
    lon2d, lat2d = np.meshgrid(
        da["longitude"].values,
        da["latitude"].values,
    )
    mask_np = contains_xy(geometry, lon2d, lat2d)

    return xr.DataArray(
        mask_np,
        coords={
            "latitude": da["latitude"],
            "longitude": da["longitude"],
        },
        dims=("latitude", "longitude"),
    )


def extract_spatial_mean_series(
    da: xr.DataArray,
    hotspots: gpd.GeoDataFrame | None,
    hotspot_id_field: str | None,
) -> pd.DataFrame:
    """
    Extract spatial-mean monthly SPEI.

    If no hotspots are supplied, uses the full valid SPEI domain.
    """
    rows = []

    if hotspots is None:
        s = da.mean(["latitude", "longitude"], skipna=True).compute().to_series()
        out = s.rename("spei").reset_index()
        out["spatial_unit"] = "Amazon_Legal_domain"
        return out

    for _, row in hotspots.iterrows():
        unit = str(row[hotspot_id_field])
        mask = make_polygon_mask(da, row.geometry)

        s = (
            da.where(mask)
            .mean(["latitude", "longitude"], skipna=True)
            .compute()
            .to_series()
        )

        out = s.rename("spei").reset_index()
        out["spatial_unit"] = unit
        rows.append(out)

    return pd.concat(rows, ignore_index=True)


# =============================================================================
# BLOCKING–SPEI RELATIONSHIPS
# =============================================================================

def lagged_blocking_spei_relationships(
    spei_monthly: pd.DataFrame,
    monthly_blocking: pd.DataFrame,
    lags: list[int],
) -> pd.DataFrame:
    """
    Pearson and Spearman relationships between monthly blocking frequency and SPEI.

    lag = 0 -> blocking(t) vs SPEI(t)
    lag = 1 -> blocking(t) vs SPEI(t+1)
    ...
    """
    blocking_wide = monthly_blocking.pivot(
        index="time",
        columns="region",
        values="blocked_fraction",
    )

    rows = []

    for (unit, scale), group in spei_monthly.groupby(
        ["spatial_unit", "scale"]
    ):
        s = group[["time", "spei"]].copy()
        s["time"] = pd.to_datetime(s["time"])
        s = s.set_index("time").sort_index()

        for region in BLOCKING_REGIONS:
            b = blocking_wide[[region]].rename(
                columns={region: "blocking_fraction"}
            )

            joined = b.join(s[["spei"]], how="inner")

            for lag in lags:
                pair = pd.DataFrame(
                    {
                        "blocking": joined["blocking_fraction"],
                        "spei_future": joined["spei"].shift(-lag),
                    }
                ).dropna()

                if len(pair) < 10:
                    continue

                if pair["blocking"].std() == 0 or pair["spei_future"].std() == 0:
                    pr = pp = sr = sp = np.nan
                else:
                    pr, pp = pearsonr(
                        pair["blocking"],
                        pair["spei_future"],
                    )
                    sr, sp = spearmanr(
                        pair["blocking"],
                        pair["spei_future"],
                    )

                rows.append(
                    {
                        "spatial_unit": unit,
                        "scale": scale,
                        "blocking_region": region,
                        "lag_months": lag,
                        "n": len(pair),
                        "pearson_r": pr,
                        "pearson_p": pp,
                        "spearman_r": sr,
                        "spearman_p": sp,
                    }
                )

    return pd.DataFrame(rows)


def align_monthly_blocking_to_spei(
    da: xr.DataArray,
    monthly_blocking: pd.DataFrame,
    region: str,
) -> tuple[xr.DataArray, xr.DataArray]:
    """Align one monthly blocking-frequency series with gridded SPEI."""
    b = (
        monthly_blocking.loc[
            monthly_blocking["region"] == region,
            ["time", "blocked_fraction"],
        ]
        .sort_values("time")
        .set_index("time")["blocked_fraction"]
    )

    b_da = xr.DataArray(
        b.values,
        coords={"time": b.index.values},
        dims="time",
        name="blocked_fraction",
    )

    return xr.align(da, b_da, join="inner")


def spatial_blocking_spei_correlation(
    da: xr.DataArray,
    monthly_blocking: pd.DataFrame,
    region: str,
    lag: int,
) -> xr.DataArray:
    """
    Spatial Pearson correlation between blocking frequency and SPEI.

    lag = 1 means blocking(t) is paired with SPEI(t+1).
    """
    spei, blocking = align_monthly_blocking_to_spei(
        da,
        monthly_blocking,
        region,
    )

    if lag > 0:
        spei = spei.shift(time=-lag)

    # corr = xr.corr(spei, blocking, dim="time")
    valid = np.isfinite(spei) & np.isfinite(blocking)

    n_valid = valid.sum("time")

    spei_std = spei.where(valid).std("time")
    blocking_std = blocking.where(valid).std("time")

    corr = xr.corr(
        spei.where(valid),
        blocking.where(valid),
        dim="time",
    )

    corr = corr.where(
        (n_valid >= 10)
        & (spei_std > 0)
        & (blocking_std > 0)
    )
    corr.name = "pearson_r"
    corr.attrs.update(
        {
            "blocking_region": region,
            "lag_months": lag,
            "description": (
                "Spatial Pearson correlation between monthly blocked-day "
                "fraction and SPEI."
            ),
        }
    )
    return corr.compute()


def blocking_composite_difference(
    da: xr.DataArray,
    monthly_blocking: pd.DataFrame,
    region: str,
    low_q: float,
    high_q: float,
) -> xr.Dataset:
    """Calculate high-blocking minus low-blocking SPEI composites."""
    spei, blocking = align_monthly_blocking_to_spei(
        da,
        monthly_blocking,
        region,
    )

    low_threshold = float(np.nanquantile(blocking.values, low_q))
    high_threshold = float(np.nanquantile(blocking.values, high_q))

    low = spei.where(blocking <= low_threshold).mean("time", skipna=True)
    high = spei.where(blocking >= high_threshold).mean("time", skipna=True)

    ds = xr.Dataset(
        {
            "mean_spei_low_blocking": low,
            "mean_spei_high_blocking": high,
            "high_minus_low": high - low,
        }
    )

    ds.attrs.update(
        {
            "blocking_region": region,
            "low_quantile": low_q,
            "high_quantile": high_q,
            "low_blocking_threshold": low_threshold,
            "high_blocking_threshold": high_threshold,
        }
    )

    return ds.compute()



# =============================================================================
# CARTOGRAPHIC UTILITIES
# =============================================================================

def read_amazon_legal_boundary(shapefile: Path) -> dict:
    """
    Read the Legal Amazon shapefile directly with Cartopy's shapereader.

    This intentionally avoids GeoPandas/pyproj for the Legal Amazon boundary,
    because the HPC environment showed a PROJ database-context error.

    The supplied Legal Amazon shapefile is geographic (SIRGAS 2000 / EPSG:4674),
    so its coordinates are already longitude/latitude values in degrees.
    For plotting only, they can be drawn on a PlateCarree map without
    reprojection.

    Returns
    -------
    dict with:
      geometries : list of shapely geometries
      bounds     : (minx, miny, maxx, maxy)
    """
    shapefile = Path(shapefile)

    if not shapefile.exists():
        raise FileNotFoundError(
            f"Legal Amazon shapefile not found: {shapefile}"
        )

    reader = shapereader.Reader(str(shapefile))
    geometries = list(reader.geometries())

    if not geometries:
        raise ValueError("Legal Amazon shapefile contains no geometries.")

    # Compute total bounds without using GeoPandas/pyproj.
    bounds = np.asarray([geom.bounds for geom in geometries], dtype=float)

    minx = float(np.nanmin(bounds[:, 0]))
    miny = float(np.nanmin(bounds[:, 1]))
    maxx = float(np.nanmax(bounds[:, 2]))
    maxy = float(np.nanmax(bounds[:, 3]))

    return {
        "geometries": geometries,
        "bounds": (minx, miny, maxx, maxy),
    }

def configure_cartopy_map(
    ax,
    da: xr.DataArray,
    amazon_boundary: dict,
    tick_interval: float = 5.0,
):
    """
    Add Cartopy geographic context to a latitude/longitude map.

    Adds:
      - coastlines;
      - international borders;
      - first-order administrative boundaries (states/provinces);
      - Legal Amazon outline;
      - geographic longitude/latitude labels;
      - dashed graticule.

    Note
    ----
    Natural Earth features may be downloaded automatically by Cartopy the first
    time they are used if they are not already cached locally.
    """
    data_crs = ccrs.PlateCarree()

    lon_min = float(np.nanmin(da["longitude"].values))
    lon_max = float(np.nanmax(da["longitude"].values))
    lat_min = float(np.nanmin(da["latitude"].values))
    lat_max = float(np.nanmax(da["latitude"].values))

    minx, miny, maxx, maxy = amazon_boundary["bounds"]
    lon_min = min(lon_min, float(minx))
    lon_max = max(lon_max, float(maxx))
    lat_min = min(lat_min, float(miny))
    lat_max = max(lat_max, float(maxy))

    margin = 0.5
    ax.set_extent(
        [lon_min - margin, lon_max + margin, lat_min - margin, lat_max + margin],
        crs=data_crs,
    )

    ax.coastlines(
        resolution="50m",
        linewidth=0.7,
        color="black",
        zorder=5,
    )

    ax.add_feature(
        cfeature.BORDERS.with_scale("50m"),
        edgecolor="black",
        linewidth=0.7,
        facecolor="none",
        zorder=5,
    )

    admin1 = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none",
    )
    ax.add_feature(
        admin1,
        edgecolor="0.45",
        linewidth=0.5,
        zorder=5,
    )

    ax.add_geometries(
        amazon_boundary["geometries"],
        crs=data_crs,
        facecolor="none",
        edgecolor="black",
        linewidth=1.5,
        zorder=7,
    )

    x_start = np.floor((lon_min - margin) / tick_interval) * tick_interval
    x_end = np.ceil((lon_max + margin) / tick_interval) * tick_interval
    y_start = np.floor((lat_min - margin) / tick_interval) * tick_interval
    y_end = np.ceil((lat_max + margin) / tick_interval) * tick_interval

    xticks = np.arange(x_start, x_end + 0.5 * tick_interval, tick_interval)
    yticks = np.arange(y_start, y_end + 0.5 * tick_interval, tick_interval)

    ax.set_xticks(xticks, crs=data_crs)
    ax.set_yticks(yticks, crs=data_crs)

    ax.xaxis.set_major_formatter(
        LongitudeFormatter(
            degree_symbol="°",
            number_format=".0f",
            dateline_direction_label=True,
        )
    )
    ax.yaxis.set_major_formatter(
        LatitudeFormatter(
            degree_symbol="°",
            number_format=".0f",
        )
    )

    ax.gridlines(
        crs=data_crs,
        draw_labels=False,
        linewidth=0.45,
        linestyle="--",
        color="0.55",
        alpha=0.45,
        zorder=2,
    )

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")


# =============================================================================
# FIGURES
# =============================================================================

def plot_spei_mk_map(
    mk_ds: xr.Dataset,
    scale: int,
    metric: str,
    alpha: float,
    output: Path,
    amazon_boundary=None,
    geographic_boundary=None,
    tick_interval: float = 5.0,
):
    """
    Plot significant spatial SPEI trends using Kendall's tau.

    Requested scheme:
      negative significant trend -> red
      positive significant trend -> blue
      non-significant pixels     -> not plotted / white
    """
    tau_sig = mk_ds["tau_significant"]

    finite = np.isfinite(tau_sig.values)
    if finite.any():
        vmax = float(np.nanmax(np.abs(tau_sig.values)))
        if vmax == 0:
            vmax = 1.0
    else:
        vmax = 1.0

    fig, ax = plt.subplots(
        figsize=(9, 7),
        subplot_kw={"projection": ccrs.PlateCarree()},
    )

    # RdBu is red for negative values and blue for positive values.
    # Center the colormap on zero.
    norm_plot = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    im = tau_sig.plot(
        ax=ax,
        x="longitude",
        y="latitude",
        transform=ccrs.PlateCarree(),
        cmap="RdBu",
        norm=norm_plot,
        add_colorbar=False,
    )

    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Kendall's tau")

    metric_titles = {
        "annual_mean": "annual mean",
        "annual_min": "annual minimum",
        "dry_months": "annual number of low-SPEI months",
    }

    ax.set_title(
        f"Spatial Mann–Kendall trend in SPEI-{scale} {metric_titles[metric]}\n"
        f"Amazon Legal, 1961–2025 — only significant trends (p < {alpha})"
    )
    configure_cartopy_map(
        ax,
        tau_sig,
        amazon_boundary=amazon_boundary,
        tick_interval=tick_interval,
    )

    fig.tight_layout()
    fig.savefig(output, dpi=250, bbox_inches="tight")
    plt.close(fig)


def plot_blocking_mk_tau(
    trends: pd.DataFrame,
    alpha: float,
    output: Path,
):
    """
    Plot Mann–Kendall tau for each atmospheric-blocking region.

    Visual convention:
      - significant positive trend: blue filled circle;
      - significant negative trend: red filled circle;
      - non-significant trend: gray x;
      - dashed red horizontal line at tau = 0.

    Tau values are placed below significant circles.
    """
    labels = trends["region"].tolist()
    x = np.arange(len(labels))
    y = trends["tau"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(11, 6))

    for xi, (_, row) in zip(x, trends.iterrows()):
        tau = float(row["tau"])

        if not np.isfinite(tau):
            continue

        if bool(row["significant"]) and tau > 0:
            ax.scatter(
                xi, tau, s=85, marker="o", color="blue", zorder=3
            )
            ax.annotate(
                f"{tau:.2f}",
                xy=(xi, tau),
                xytext=(0, -12),
                textcoords="offset points",
                ha="center",
                va="top",
                fontsize=9,
            )

        elif bool(row["significant"]) and tau < 0:
            ax.scatter(
                xi, tau, s=85, marker="o", color="red", zorder=3
            )
            ax.annotate(
                f"{tau:.2f}",
                xy=(xi, tau),
                xytext=(0, -12),
                textcoords="offset points",
                ha="center",
                va="top",
                fontsize=9,
            )

        else:
            ax.scatter(
                xi,
                tau,
                s=85,
                marker="x",
                color="gray",
                linewidths=1.6,
                zorder=3,
            )

    ax.axhline(
        0,
        color="red",
        linestyle="--",
        linewidth=1.3,
        alpha=0.9,
        zorder=1,
    )

    legend_handles = [
        Line2D(
            [0], [0],
            marker="o",
            linestyle="None",
            markerfacecolor="blue",
            markeredgecolor="blue",
            markersize=8,
            label="Increasing",
        ),
        Line2D(
            [0], [0],
            marker="o",
            linestyle="None",
            markerfacecolor="red",
            markeredgecolor="red",
            markersize=8,
            label="Decreasing",
        ),
        Line2D(
            [0], [0],
            marker="x",
            linestyle="None",
            color="gray",
            markersize=8,
            label="No trend",
        ),
    ]

    ax.legend(
        handles=legend_handles,
        title="Trend",
        loc="best",
        frameon=True,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right")
    ax.set_ylabel("Kendall's Tau")
    ax.set_xlabel("Atmospheric-blocking region")

    ax.set_title(
        "Trend Analysis - Atmospheric Blocking Indices\n"
        f"Annual blocked-day frequency, ERA5, 1961–2025 "
        f"(Mann–Kendall, p < {alpha})"
    )

    ax.grid(
        which="major",
        axis="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.3,
    )

    finite_y = y[np.isfinite(y)]
    if finite_y.size:
        ymin = min(-0.05, float(np.nanmin(finite_y)) - 0.10)
        ymax = max(0.05, float(np.nanmax(finite_y)) + 0.10)
        ax.set_ylim(ymin, ymax)

    fig.tight_layout()
    fig.savefig(output, dpi=250, bbox_inches="tight")
    plt.close(fig)


def plot_spatial_correlation_map(
    da: xr.DataArray,
    scale: int,
    region: str,
    lag: int,
    output: Path,
    amazon_boundary=None,
    geographic_boundary=None,
    tick_interval: float = 5.0,
):
    """Plot spatial blocking–SPEI Pearson correlation."""
    fig, ax = plt.subplots(
        figsize=(9, 7),
        subplot_kw={"projection": ccrs.PlateCarree()},
    )

    im = da.plot(
        ax=ax,
        x="longitude",
        y="latitude",
        transform=ccrs.PlateCarree(),
        cmap="RdBu",
        vmin=-1,
        vmax=1,
        add_colorbar=False,
    )

    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Pearson correlation coefficient (r)")

    lag_text = (
        "same month"
        if lag == 0
        else f"blocking leading SPEI by {lag} month(s)"
    )

    ax.set_title(
        f"Spatial association between atmospheric blocking and SPEI-{scale}\n"
        f"Blocking region: {region}; {lag_text}; 1961–2025"
    )
    configure_cartopy_map(
        ax,
        da,
        amazon_boundary=amazon_boundary,
        tick_interval=tick_interval,
    )

    fig.tight_layout()
    fig.savefig(output, dpi=250, bbox_inches="tight")
    plt.close(fig)


def plot_composite_map(
    da: xr.DataArray,
    scale: int,
    region: str,
    low_q: float,
    high_q: float,
    output: Path,
    amazon_boundary=None,
    geographic_boundary=None,
    tick_interval: float = 5.0,
):
    """Plot high-blocking minus low-blocking SPEI composite."""
    finite = np.isfinite(da.values)

    if finite.any():
        vmax = float(np.nanmax(np.abs(da.values)))
        if vmax == 0:
            vmax = 1.0
    else:
        vmax = 1.0

    fig, ax = plt.subplots(
        figsize=(9, 7),
        subplot_kw={"projection": ccrs.PlateCarree()},
    )

    im = da.plot(
        ax=ax,
        x="longitude",
        y="latitude",
        transform=ccrs.PlateCarree(),
        cmap="RdBu",
        vmin=-vmax,
        vmax=vmax,
        add_colorbar=False,
    )

    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label(f"Difference in SPEI-{scale}")

    ax.set_title(
        f"SPEI-{scale} response during months with high versus low blocking activity\n"
        f"Blocking region: {region}; high ≥ P{int(high_q*100)}, "
        f"low ≤ P{int(low_q*100)}; 1961–2025"
    )
    configure_cartopy_map(
        ax,
        da,
        amazon_boundary=amazon_boundary,
        tick_interval=tick_interval,
    )

    fig.tight_layout()
    fig.savefig(output, dpi=250, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run(args):
    output_dir = Path(args.output_dir)
    dirs = ensure_output_dirs(output_dir)

    # Cartographic context used in all spatial figures.
    print("[0/5] Reading cartographic boundaries...")
    amazon_boundary = read_amazon_legal_boundary(
        Path(args.amazon_shapefile)
    )

    # -------------------------------------------------------------------------
    # 1. Atmospheric blocking
    # -------------------------------------------------------------------------
    print("[1/5] Reading atmospheric-blocking data...")

    daily_blocking = read_daily_blocking(Path(args.blocking_csv))
    monthly_blocking = blocking_monthly_metrics(daily_blocking)
    annual_blocking = blocking_annual_metrics(daily_blocking)

    blocking_trends = blocking_mk_trends(
        annual_blocking,
        alpha=args.alpha,
    )

    monthly_blocking.to_csv(
        dirs["tables"] / "blocking_monthly_frequency.csv",
        index=False,
    )
    annual_blocking.to_csv(
        dirs["tables"] / "blocking_annual_frequency.csv",
        index=False,
    )
    blocking_trends.to_csv(
        dirs["tables"] / "blocking_mann_kendall_trends.csv",
        index=False,
    )

    plot_blocking_mk_tau(
        blocking_trends,
        alpha=args.alpha,
        output=dirs["figures"]
        / "mann_kendall_atmospheric_blocking_trends_1961_2025.png",
    )

    # -------------------------------------------------------------------------
    # 2. Optional hotspots
    # -------------------------------------------------------------------------
    hotspots = None

    if args.hotspots_shapefile:
        print("[2/5] Reading hotspot polygons...")
        hotspots = read_hotspots(
            Path(args.hotspots_shapefile),
            args.hotspot_id_field,
        )
    else:
        print("[2/5] No hotspot shapefile supplied.")

    # -------------------------------------------------------------------------
    # 3. SPEI spatial Mann–Kendall trends
    # -------------------------------------------------------------------------
    print("[3/5] Calculating pixel-wise Mann–Kendall trends for SPEI...")

    spei_paths = {
        1: Path(args.spei1),
        3: Path(args.spei3),
        6: Path(args.spei6),
        12: Path(args.spei12),
    }

    spei_arrays = {}
    regional_spei_frames = []

    for scale, path in spei_paths.items():
        print(f"      SPEI-{scale}...")

        da = open_spei(path, scale)
        spei_arrays[scale] = da

        annual = aggregate_spei_annual(
            da,
            metric=args.spei_trend_metric,
            threshold=args.spei_threshold,
        ).chunk({"year": -1})

        mk_ds = mann_kendall_grid(
            annual,
            alpha=args.alpha,
        )

        # Save the full statistical result, not just the significant map.
        mk_path = (
            dirs["netcdf"]
            / f"spei{scale}_{args.spei_trend_metric}_mann_kendall_1961_2025.nc"
        )
        mk_ds.to_netcdf(mk_path)

        plot_spei_mk_map(
            mk_ds,
            scale=scale,
            metric=args.spei_trend_metric,
            alpha=args.alpha,
            output=dirs["figures"]
            / f"spei{scale}_{args.spei_trend_metric}_mann_kendall_significant_tau.png",
            amazon_boundary=amazon_boundary,
            tick_interval=args.map_tick_interval,
        )

        # Regional/hotspot monthly mean series for blocking–SPEI analysis.
        extracted = extract_spatial_mean_series(
            da,
            hotspots,
            args.hotspot_id_field if hotspots is not None else None,
        )
        extracted["scale"] = scale
        regional_spei_frames.append(extracted)

    regional_spei = pd.concat(
        regional_spei_frames,
        ignore_index=True,
    )
    regional_spei["time"] = pd.to_datetime(regional_spei["time"])

    regional_spei.to_csv(
        dirs["tables"] / "spei_monthly_spatial_mean_series.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # 4. Blocking–SPEI time-series relationships
    # -------------------------------------------------------------------------
    print("[4/5] Calculating monthly blocking–SPEI relationships...")

    lagged = lagged_blocking_spei_relationships(
        regional_spei,
        monthly_blocking,
        lags=args.lags,
    )

    lagged.to_csv(
        dirs["tables"] / "blocking_spei_lagged_relationships.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # 5. Spatial correlations and composites
    # -------------------------------------------------------------------------
    print("[5/5] Calculating spatial blocking–SPEI associations...")

    for scale, da in spei_arrays.items():
        for region in args.spatial_blocking_regions:

            for lag in args.spatial_lags:
                corr = spatial_blocking_spei_correlation(
                    da,
                    monthly_blocking,
                    region=region,
                    lag=lag,
                )

                corr.to_netcdf(
                    dirs["netcdf"]
                    / f"blocking_{region}_spei{scale}_lag{lag}_spatial_correlation.nc"
                )

                plot_spatial_correlation_map(
                    corr,
                    scale=scale,
                    region=region,
                    lag=lag,
                    output=dirs["figures"]
                    / f"blocking_{region}_spei{scale}_lag{lag}_spatial_correlation.png",
                    amazon_boundary=amazon_boundary,
                            tick_interval=args.map_tick_interval,
                )

            comp = blocking_composite_difference(
                da,
                monthly_blocking,
                region=region,
                low_q=args.low_blocking_quantile,
                high_q=args.high_blocking_quantile,
            )

            comp.to_netcdf(
                dirs["netcdf"]
                / f"blocking_{region}_spei{scale}_high_low_composite.nc"
            )

            plot_composite_map(
                comp["high_minus_low"],
                scale=scale,
                region=region,
                low_q=args.low_blocking_quantile,
                high_q=args.high_blocking_quantile,
                output=dirs["figures"]
                / f"blocking_{region}_spei{scale}_high_minus_low_composite.png",
                amazon_boundary=amazon_boundary,
                    tick_interval=args.map_tick_interval,
            )

    # -------------------------------------------------------------------------
    # Save analysis settings for reproducibility.
    # -------------------------------------------------------------------------
    settings = {
        "study_period": "1961-2025",
        "amazon_shapefile": args.amazon_shapefile,
        "map_tick_interval_degrees": args.map_tick_interval,
        "mann_kendall_test": "classical with tie correction",
        "alpha": args.alpha,
        "spei_spatial_trend_metric": args.spei_trend_metric,
        "spei_threshold": args.spei_threshold,
        "blocking_trend_metric": "annual blocked-day fraction",
        "blocking_to_spei_lags": args.lags,
        "spatial_blocking_regions": args.spatial_blocking_regions,
        "spatial_lags": args.spatial_lags,
        "low_blocking_quantile": args.low_blocking_quantile,
        "high_blocking_quantile": args.high_blocking_quantile,
        "notes": [
            "Legal Amazon boundary is read with cartopy.io.shapereader, avoiding GeoPandas/pyproj for that layer.",
            "SPEI spatial trends are calculated independently at every pixel.",
            "Only significant SPEI tau values are displayed on trend maps.",
            "Blocking trend colors: blue=significant positive, red=significant negative, gray=non-significant.",
            "Classical Mann-Kendall does not correct for serial autocorrelation.",
            "Annual aggregation is used for trend analyses.",
        ],
    }

    with open(
        output_dir / "analysis_settings.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print("\nAnalysis completed.")
    print(f"Results saved in: {output_dir.resolve()}")


# =============================================================================
# COMMAND-LINE ARGUMENTS
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Hydroclimatic analysis of SPEI and ERA5 atmospheric blocking "
            "with pixel-wise Mann-Kendall trends."
        )
    )

    parser.add_argument(
        "--blocking-csv",
        required=True,
        help="Path to daily_blocking_series.csv",
    )

    parser.add_argument("--spei1", required=True)
    parser.add_argument("--spei3", required=True)
    parser.add_argument("--spei6", required=True)
    parser.add_argument("--spei12", required=True)

    parser.add_argument(
        "--output-dir",
        required=True,
    )

    parser.add_argument(
        "--amazon-shapefile",
        required=True,
        help=(
            "Shapefile containing the Legal Amazon boundary. "
            "Read directly with Cartopy shapereader and used to draw the "
            "Legal Amazon outline on all spatial maps."
        ),
    )

    parser.add_argument(
        "--map-tick-interval",
        type=float,
        default=5.0,
        help="Latitude/longitude tick interval in degrees. Default: 5.",
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=DEFAULT_ALPHA,
        help="Significance level for Mann-Kendall tests. Default: 0.05",
    )

    parser.add_argument(
        "--spei-trend-metric",
        choices=["annual_mean", "annual_min", "dry_months"],
        default="annual_mean",
        help=(
            "Annual SPEI metric used for pixel-wise Mann-Kendall trend. "
            "Default: annual_mean"
        ),
    )

    parser.add_argument(
        "--spei-threshold",
        type=float,
        default=SPEI_EVENT_THRESHOLD,
        help=(
            "Threshold used only when --spei-trend-metric dry_months. "
            "Default: -1.0"
        ),
    )

    parser.add_argument(
        "--lags",
        type=int,
        nargs="+",
        default=BLOCKING_TO_SPEI_LAGS,
        help="Blocking(t) -> SPEI(t+lag) lags.",
    )

    parser.add_argument(
        "--spatial-blocking-regions",
        nargs="+",
        choices=BLOCKING_REGIONS,
        default=["total", "north", "south"],
        help="Blocking regions used in spatial blocking-SPEI maps.",
    )

    parser.add_argument(
        "--spatial-lags",
        type=int,
        nargs="+",
        default=[0, 1],
        help="Lags for gridded blocking-SPEI correlation maps.",
    )

    parser.add_argument(
        "--low-blocking-quantile",
        type=float,
        default=LOW_BLOCKING_QUANTILE,
    )

    parser.add_argument(
        "--high-blocking-quantile",
        type=float,
        default=HIGH_BLOCKING_QUANTILE,
    )

    parser.add_argument(
        "--hotspots-shapefile",
        default=None,
        help="Optional hotspot shapefile.",
    )

    parser.add_argument(
        "--hotspot-id-field",
        default="id",
        help="Unique hotspot identifier field.",
    )

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run(args)

