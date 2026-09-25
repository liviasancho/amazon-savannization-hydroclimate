"""Calculate six annual climate-extreme indices and Pettitt change points.

Inputs are supplied explicitly on the command line:

- three original BR-DWGD precipitation NetCDF files;
- three original BR-DWGD daily maximum temperature (Tmax) NetCDF files;
- the Arc of Deforestation shapefile;
- an output directory.

Expected BR-DWGD filename pattern
---------------------------------
Precipitation:
    pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
    pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
    pr_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc

Daily maximum temperature:
    Tmax_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
    Tmax_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
    Tmax_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc

The three files for each variable are concatenated along the time dimension,
sorted chronologically, and checked for duplicated timestamps. No intermediate
pre-concatenated BR-DWGD files are required.

Outputs
-------
<output-dir>/indices/<INDEX>_annual.nc
<output-dir>/indices/pettitt_breakpoints_arc_deforestation.xlsx
<output-dir>/figures/<INDEX>_annual_arc_deforestation_pettitt.png
<output-dir>/figures/annual_extremes_arc_deforestation_pettitt.png

The script uses the 1961–1990 reference period for WSDI. The calendar-day
90th percentile is calculated with a centred 5-day window, and a warm spell
must contain at least six consecutive days above that threshold.

The configured variables are ``pr`` for precipitation and ``Tmax`` for daily
maximum air temperature. BR-DWGD precipitation is stored as daily accumulated
millimetres; the script represents these values as the numerically equivalent
daily rate ``mm d-1`` required by xclim precipitation indices.

The script renames common latitude/longitude aliases internally and uses
regionmask plus cosine-latitude weighting to calculate Arc-wide annual means.
"""

from __future__ import annotations

import argparse
import logging
import inspect
import sys
import warnings
from pathlib import Path
from typing import Any

import dask
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import regionmask
import xarray as xr
import xclim.indices as xci
from xclim.core.calendar import percentile_doy
from xclim.core.units import convert_units_to
from scipy.stats import rankdata


# =============================================================================
# USER CONFIGURATION
# =============================================================================

SCRIPT_VERSION = "repository-cli-1"

# Populated from command-line arguments in main().
PRECIPITATION_FILES: list[Path] = []
TASMAX_FILES: list[Path] = []
SHAPEFILE: Path | None = None
INDICES_DIR: Path | None = None
FIGURES_DIR: Path | None = None

# Xavier 1961–2025 files: ``pr-xavier_2025.nc`` contains ``pr`` and
# ``tas-xavier_2025.nc`` contains ``Tmax``. Keeping these explicit makes the
# calculation unambiguous and prevents a mean-temperature field being used.
PRECIPITATION_VARIABLE: str | None = "pr"
TASMAX_VARIABLE: str | None = "Tmax"

# Xavier data are normally supplied as daily precipitation and temperature.
# These values are applied only when a NetCDF variable lacks a units attribute.
PRECIPITATION_UNITS_IF_MISSING = "mm d-1"
TEMPERATURE_UNITS_IF_MISSING = "degC"

# The Xavier Tmax NetCDF used here is in degrees Celsius, but its metadata may
# use the invalid spelling ``Celcius``. Apply this correct unit before *any*
# xclim operation. Set to None only for another product with reliable metadata.
TASMAX_UNITS_OVERRIDE: str | None = "degC"

START_DATE = "1961-01-01"
END_DATE = "2025-12-31"
WSDI_REFERENCE_START = "1961-01-01"
WSDI_REFERENCE_END = "1990-12-31"
WSDI_PERCENTILE = 90
WSDI_PERCENTILE_WINDOW = 5
WSDI_SPELL_LENGTH = 6

# Conservative chunks keep WSDI feasible on a ~10-km national grid. Increase
# only after checking available memory. With a larger machine, 48 or 64 may be
# faster; with memory pressure, reduce to 24 or reduce workers to one.
SPATIAL_CHUNK_SIZE = 32
DASK_NUM_WORKERS = 2

PETTITT_ALPHA = 0.05

NETCDF_ENGINE = "h5netcdf"
NETCDF_ENCODING = {"zlib": True, "complevel": 4, "dtype": "float32"}


# =============================================================================
# FIGURE STYLE
# =============================================================================

LINE_COLOUR = "#344E5C"       # restrained blue-grey
POINT_COLOUR = "#71808A"
BREAK_COLOUR = "#B23A48"      # muted red
GRID_COLOUR = "#D9DEE2"
TEXT_COLOUR = "#20282D"

mpl.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 10.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "axes.labelcolor": TEXT_COLOUR,
        "xtick.color": TEXT_COLOUR,
        "ytick.color": TEXT_COLOUR,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    }
)

INDEX_METADATA: dict[str, dict[str, str]] = {
    "WSDI": {
        "long_name": "Warm spell duration index",
        "definition": (
            "Annual number of days in spells of at least six consecutive days "
            "with daily maximum temperature above the calendar-day 90th "
            "percentile, calculated from a centred 5-day window over 1961–1990."
        ),
        "y_label": "Days",
    },
    "SU35": {
        "long_name": "Days with daily maximum temperature above 35 °C",
        "definition": "Annual number of days with daily maximum temperature above 35 °C.",
        "y_label": "Days",
    },
    "TXx": {
        "long_name": "Maximum of daily maximum temperature",
        "definition": "Annual maximum of daily maximum temperature.",
        "y_label": "Temperature (°C)",
    },
    "CDD": {
        "long_name": "Maximum consecutive dry days",
        "definition": "Annual maximum number of consecutive days with precipitation below 1 mm day−1.",
        "y_label": "Days",
    },
    "R1mm": {
        "long_name": "Wet days",
        "definition": "Annual number of days with precipitation at or above 1 mm day−1.",
        "y_label": "Days",
    },
    "PRCPTOT": {
        "long_name": "Annual total wet-day precipitation",
        "definition": "Annual accumulated precipitation from days with precipitation at or above 1 mm day−1.",
        "y_label": "Precipitation (mm)",
    },
}


def configure_logging() -> None:
    """Send concise, time-stamped progress information to the terminal."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def require_file(path: Path, label: str) -> None:
    """Fail early with the exact expected location when a required input is absent."""
    if not path.is_file():
        raise FileNotFoundError(f"{label} was not found: {path}")


def coordinate_name(ds: xr.Dataset, candidates: tuple[str, ...], label: str) -> str:
    """Find a coordinate/dimension name case-insensitively."""
    available = list(ds.coords) + [name for name in ds.dims if name not in ds.coords]
    lookup = {name.lower(): name for name in available}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    raise ValueError(
        f"Could not identify the {label} coordinate. Available coordinates/dimensions: {available}"
    )


def standardise_coordinates(ds: xr.Dataset, source: Path) -> xr.Dataset:
    """Rename common coordinate aliases to CF-like ``time``, ``lat`` and ``lon``."""
    time_name = coordinate_name(ds, ("time", "date", "datetime"), "time")
    lat_name = coordinate_name(ds, ("lat", "latitude", "y"), "latitude")
    lon_name = coordinate_name(ds, ("lon", "longitude", "x"), "longitude")

    rename_map = {
        old: new
        for old, new in ((time_name, "time"), (lat_name, "lat"), (lon_name, "lon"))
        if old != new
    }
    if rename_map:
        logging.info("Normalising coordinates in %s: %s", source.name, rename_map)
        ds = ds.rename(rename_map)

    if ds["lat"].ndim != 1 or ds["lon"].ndim != 1:
        raise ValueError(
            "This script expects a rectilinear 1-D latitude/longitude grid. "
            f"Got lat ndim={ds['lat'].ndim}, lon ndim={ds['lon'].ndim}."
        )
    return ds


def choose_variable(
    ds: xr.Dataset,
    configured_name: str | None,
    candidates: tuple[str, ...],
    role: str,
) -> xr.DataArray:
    """Select an input variable, preferring an explicit configuration."""
    if configured_name is not None:
        if configured_name not in ds.data_vars:
            raise KeyError(
                f"Configured {role} variable '{configured_name}' is not in the dataset. "
                f"Available variables: {list(ds.data_vars)}"
            )
        return ds[configured_name]

    lower_names = {name.lower(): name for name in ds.data_vars}
    for candidate in candidates:
        if candidate.lower() in lower_names:
            selected = lower_names[candidate.lower()]
            logging.info("Auto-detected %s variable: %s", role, selected)
            return ds[selected]

    if len(ds.data_vars) == 1:
        selected = next(iter(ds.data_vars))
        warnings.warn(
            f"No standard {role} variable name was found. Using the only variable "
            f"available: '{selected}'. Verify that this is the intended field.",
            stacklevel=2,
        )
        return ds[selected]

    raise KeyError(
        f"Could not auto-detect the {role} variable. Available variables: {list(ds.data_vars)}. "
        "Set the corresponding variable in USER CONFIGURATION."
    )


def ensure_units(da: xr.DataArray, assumed_units: str, role: str) -> xr.DataArray:
    """Supply a documented fallback only when an input field lacks units."""
    da = da.copy()
    if not da.attrs.get("units"):
        warnings.warn(
            f"{role} has no units attribute. Assuming '{assumed_units}'. "
            "Confirm this assumption before interpreting the results.",
            stacklevel=2,
        )
        da.attrs["units"] = assumed_units
    return da


def prepare_daily_precipitation(pr: xr.DataArray) -> xr.DataArray:
    """Represent Xavier daily precipitation amounts in the rate units xclim expects.

    The Xavier ``pr`` field records one accumulated daily amount per timestamp.
    Thus, on its regular daily time axis, a value in ``mm`` has the same
    numerical magnitude as its one-day rate in ``mm d-1``. This is a metadata
    normalisation, not a numerical conversion; it allows xclim to apply the
    1 mm d-1 thresholds and to return PRCPTOT in millimetres correctly.
    """
    original_units = str(pr.attrs.get("units", "")).strip()
    normalised_units = original_units.lower().replace(" ", "")
    amount_units = {"mm", "millimeter", "millimeters", "millimetre", "millimetres"}

    if normalised_units in amount_units:
        time = pd.DatetimeIndex(pd.to_datetime(pr["time"].values))
        if len(time) < 2 or not np.all(np.diff(time.values) == np.timedelta64(1, "D")):
            raise ValueError(
                "Precipitation in length units can only be interpreted as a daily rate "
                "when the time axis has a regular one-day step."
            )
        pr = pr.copy()
        pr.attrs["original_units"] = original_units
        pr.attrs["units"] = "mm d-1"
        pr.attrs["unit_normalisation"] = (
            "Input is a daily accumulated precipitation amount; values are "
            "numerically equivalent to the mean daily rate."
        )
        logging.info("Interpreting daily precipitation amounts in %s as mm d-1.", original_units)
        return pr

    return convert_units_to(pr, "mm d-1")


def prepare_temperature_units(tasmax: xr.DataArray) -> xr.DataArray:
    """Assign trustworthy Xavier Tmax units before any xclim unit parsing."""
    original_units = str(tasmax.attrs.get("units", "")).strip()
    if TASMAX_UNITS_OVERRIDE is not None:
        tasmax = tasmax.copy()
        tasmax.attrs["original_units"] = original_units
        tasmax.attrs["units"] = TASMAX_UNITS_OVERRIDE
        tasmax.attrs["unit_normalisation"] = (
            "Known Xavier Tmax input; forced to degC before xclim unit validation."
        )
        logging.info("Using configured Tmax units: %s (input metadata: %s).", TASMAX_UNITS_OVERRIDE, original_units)
        return tasmax

    normalised_units = original_units.lower().replace(" ", "")
    celsius_aliases = {
        "celcius",  # spelling used in the Xavier NetCDF metadata
        "celsius",
        "degreecelsius",
        "degreescelsius",
        "degc",
        "°c",
    }
    if normalised_units in celsius_aliases:
        tasmax = tasmax.copy()
        tasmax.attrs["original_units"] = original_units
        tasmax.attrs["units"] = "degC"
        tasmax.attrs["unit_normalisation"] = "Corrected Celsius unit spelling in input metadata."
        logging.info("Corrected temperature units from %s to degC.", original_units)
        return tasmax
    return convert_units_to(tasmax, "degC")


def open_and_concatenate(
    files: list[Path],
    role: str,
    chunks: dict[str, int],
) -> xr.Dataset:
    """Open three original BR-DWGD files, concatenate them in time, and validate."""
    if len(files) != 3:
        raise ValueError(f"{role}: exactly three BR-DWGD files are required.")

    datasets: list[xr.Dataset] = []
    for path in files:
        require_file(path, f"{role} NetCDF")
        ds = standardise_coordinates(xr.open_dataset(path), path)
        datasets.append(ds)

    combined = xr.concat(
        datasets,
        dim="time",
        data_vars="minimal",
        coords="minimal",
        compat="override",
        join="exact",
    ).sortby("time")

    time_index = pd.DatetimeIndex(pd.to_datetime(combined["time"].values))

    if time_index.has_duplicates:
        duplicated = time_index[time_index.duplicated()].unique()
        raise ValueError(
            f"{role}: duplicated timestamps found after concatenation: "
            f"{duplicated[:10].tolist()}"
        )

    if not time_index.is_monotonic_increasing:
        raise ValueError(f"{role}: time coordinate is not monotonically increasing.")

    return combined.chunk(chunks)


def open_inputs() -> tuple[xr.DataArray, xr.DataArray]:
    """Open, concatenate, subset and standardise Tmax and precipitation."""
    chunks = {"time": -1, "lat": SPATIAL_CHUNK_SIZE, "lon": SPATIAL_CHUNK_SIZE}
    logging.info("Opening original BR-DWGD files with chunks: %s", chunks)

    ds_pr = open_and_concatenate(
        PRECIPITATION_FILES,
        "Precipitation",
        chunks,
    )
    ds_tas = open_and_concatenate(
        TASMAX_FILES,
        "Daily maximum temperature",
        chunks,
    )

    pr = choose_variable(
        ds_pr,
        PRECIPITATION_VARIABLE,
        ("pr", "precip", "precipitation", "prec", "rain"),
        "precipitation",
    )
    tasmax = choose_variable(
        ds_tas,
        TASMAX_VARIABLE,
        ("Tmax", "tasmax", "tmax", "tx", "t_max", "maximum_temperature", "tas"),
        "daily-maximum temperature",
    )

    if tasmax.name.lower() == "tas":
        warnings.warn(
            "The fallback variable 'tas' is being used for Tmax-based indicators. "
            "Continue only if this variable is daily maximum temperature.",
            stacklevel=2,
        )

    pr = ensure_units(pr, PRECIPITATION_UNITS_IF_MISSING, "Precipitation")
    tasmax = ensure_units(
        tasmax,
        TEMPERATURE_UNITS_IF_MISSING,
        "Daily maximum temperature",
    )

    pr = prepare_daily_precipitation(pr).sel(time=slice(START_DATE, END_DATE))
    tasmax = prepare_temperature_units(tasmax).sel(
        time=slice(START_DATE, END_DATE)
    )

    if pr.sizes.get("time", 0) == 0 or tasmax.sizes.get("time", 0) == 0:
        raise ValueError("The requested 1961–2025 time subset is empty.")

    if not np.array_equal(pr["time"].values, tasmax["time"].values):
        raise ValueError(
            "Precipitation and Tmax do not have identical time coordinates "
            "after concatenation and subsetting."
        )

    return tasmax, pr

def describe_annual_index(index: xr.DataArray, code: str) -> xr.DataArray:
    """Apply consistent name, metadata and storage type to one annual index."""
    meta = INDEX_METADATA[code]
    index = index.rename(code).astype("float32")
    index.attrs.update(
        {
            "long_name": meta["long_name"],
            "description": meta["definition"],
            "frequency": "annual, calendar year",
            "reference": "ETCCDI-compatible calculation with xclim",
            "spatial_domain": "Brazilian gridded input domain",
        }
    )
    return index


def call_xclim_index(function: Any, *args: Any, **kwargs: Any) -> xr.DataArray:
    """Call an xclim index while omitting unsupported optional keywords.

    xclim changed some low-level function signatures between releases. The
    optional keywords below always reproduce the ETCCDI-compatible defaults,
    so omitting them on an older release preserves the intended calculation.
    """
    parameters = inspect.signature(function).parameters
    accepts_keyword_dict = any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()
    )
    if not accepts_keyword_dict:
        unsupported = sorted(set(kwargs).difference(parameters))
        if unsupported:
            logging.info(
                "xclim compatibility: omitting unsupported optional keyword(s) for %s: %s",
                function.__name__,
                ", ".join(unsupported),
            )
            kwargs = {name: value for name, value in kwargs.items() if name in parameters}
    return function(*args, **kwargs)


def calculate_indices(tasmax: xr.DataArray, pr: xr.DataArray) -> dict[str, xr.DataArray]:
    """Build lazy xclim computations for the six requested annual indices."""
    logging.info("Preparing annual ETCCDI-style indices for 1961–2025.")

    # This is the computationally intensive step. Keeping time in one chunk and
    # tiling space lets xclim calculate each grid-cell percentile efficiently.
    reference_tasmax = tasmax.sel(time=slice(WSDI_REFERENCE_START, WSDI_REFERENCE_END))
    if reference_tasmax.sizes.get("time", 0) < 365 * 25:
        raise ValueError(
            "The WSDI reference period contains too few days. Verify the time coordinate "
            "and the 1961–1990 availability in the temperature NetCDF."
        )

    tasmax_p90 = percentile_doy(
        reference_tasmax,
        per=WSDI_PERCENTILE,
        window=WSDI_PERCENTILE_WINDOW,
    ).sel(percentiles=WSDI_PERCENTILE)
    tasmax_p90.attrs["units"] = tasmax.attrs["units"]

    indices = {
        "WSDI": call_xclim_index(
            xci.warm_spell_duration_index,
            tasmax,
            tasmax_p90,
            window=WSDI_SPELL_LENGTH,
            freq="YS",
            resample_before_rl=True,
            bootstrap=False,
            op=">",
        ),
        "SU35": call_xclim_index(xci.tx_days_above, tasmax, thresh="35 degC", freq="YS", op=">"),
        "TXx": call_xclim_index(xci.tx_max, tasmax, freq="YS"),
        "CDD": call_xclim_index(
            xci.maximum_consecutive_dry_days,
            pr,
            thresh="1 mm d-1",
            freq="YS",
            resample_before_rl=True,
        ),
        "R1mm": call_xclim_index(xci.wetdays, pr, thresh="1 mm d-1", freq="YS", op=">="),
        "PRCPTOT": call_xclim_index(xci.prcptot, pr, thresh="1 mm d-1", freq="YS"),
    }
    return {code: describe_annual_index(da, code) for code, da in indices.items()}


def write_index(index: xr.DataArray, code: str) -> Path:
    """Materialise a Dask index once and store it as a compressed NetCDF file."""
    if INDICES_DIR is None:
        raise RuntimeError("Index output directory was not configured.")
    destination = INDICES_DIR / f"{code}_annual.nc"
    dataset = index.to_dataset(name=code)
    dataset.attrs.update(
        {
            "title": f"Annual {code} climate index",
            "summary": INDEX_METADATA[code]["definition"],
            "source_data": "Xavier daily gridded weather data (1961–2025)",
            "software": "xclim",
        }
    )
    logging.info("Writing %s", destination.name)
    with dask.config.set(scheduler="threads", num_workers=DASK_NUM_WORKERS):
        dataset.to_netcdf(
            destination,
            engine=NETCDF_ENGINE,
            encoding={code: NETCDF_ENCODING},
        )
    dataset.close()
    return destination


def open_arc_geometry() -> gpd.GeoDataFrame:
    """Read the arc boundary and put it in the geographical CRS of the grid."""
    if SHAPEFILE is None:
        raise RuntimeError("Arc shapefile path was not configured.")
    require_file(SHAPEFILE, "Arc of Deforestation shapefile")
    arc = gpd.read_file(SHAPEFILE)
    arc = arc.loc[arc.geometry.notna()].copy()
    if arc.empty:
        raise ValueError(f"The shapefile has no valid geometries: {SHAPEFILE}")
    if arc.crs is None:
        warnings.warn(
            "The shapefile CRS is undefined. Assuming EPSG:4326. Confirm this before use.",
            stacklevel=2,
        )
        arc = arc.set_crs("EPSG:4326")
    else:
        arc = arc.to_crs("EPSG:4326")
    return arc


def align_longitude_to_geometry(da: xr.DataArray, geometry: gpd.GeoDataFrame) -> xr.DataArray:
    """Convert 0–360° longitude coordinates when the polygon uses −180–180°."""
    lon_min = float(da["lon"].min())
    geom_min_x = float(geometry.total_bounds[0])
    if lon_min >= 0 and geom_min_x < 0:
        logging.info("Converting longitude coordinates from 0–360° to −180–180° for masking.")
        da = da.assign_coords(lon=((da["lon"] + 180) % 360) - 180).sortby("lon")
    return da


def weighted_arc_mean(index_file: Path, code: str, arc: gpd.GeoDataFrame) -> xr.DataArray:
    """Use regionmask and cosine-latitude weights to calculate the arc mean."""
    with xr.open_dataset(index_file, chunks={"time": -1}) as ds:
        da = align_longitude_to_geometry(ds[code], arc)
        mask_3d = regionmask.mask_3D_geopandas(
            arc,
            da["lon"],
            da["lat"],
            overlap=True,
            wrap_lon=None,
        )
        mask = mask_3d.any(dim="region")
        if not bool(mask.any()):
            raise ValueError(
                f"The arc shapefile does not overlap the {code} grid. "
                "Check the shapefile CRS and longitude convention."
            )

        # On this regular latitude–longitude grid, cos(latitude) is proportional
        # to cell area. The mask is applied through the data, not the weights,
        # so xarray's weighted mean ignores cells outside the arc.
        latitude_weights = np.cos(np.deg2rad(da["lat"]))
        arc_mean = da.where(mask).weighted(latitude_weights).mean(dim=("lat", "lon"))
        arc_mean = arc_mean.compute().load()

    arc_mean = arc_mean.rename(code)
    arc_mean.attrs.update(
        {
            "spatial_aggregation": "regionmask arc mask; cosine-latitude area-weighted mean",
            "region": "Arc of Deforestation",
        }
    )
    return arc_mean


def year_from_timestamp(timestamp: Any) -> int:
    """Support both NumPy datetimes and cftime objects without pandas coercion."""
    if hasattr(timestamp, "year"):
        return int(timestamp.year)
    return int(pd.Timestamp(timestamp).year)


def arc_mean_to_series(arc_mean: xr.DataArray, code: str) -> pd.Series:
    """Transform a compact annual xarray field into a year-indexed pandas Series."""
    years = [year_from_timestamp(time) for time in arc_mean["time"].values]
    series = pd.Series(arc_mean.values.astype(float), index=pd.Index(years, name="Year"), name=code)
    series = series.loc[~series.index.duplicated(keep="first")].sort_index()
    expected_years = pd.Index(range(1961, 2026), name="Year")
    return series.reindex(expected_years)


def pettitt_test(values: np.ndarray) -> dict[str, float | int | bool]:
    """Calculate Pettitt's rank-based single-change-point test with SciPy.

    The p-value uses Pettitt's standard analytical approximation,
    ``2 exp(-6 K² / (n³ + n²))``. SciPy's average-rank convention correctly
    handles tied annual values. No package beyond SciPy is required.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise ValueError("Pettitt's test requires a one-dimensional finite series with at least two values.")

    n = len(values)
    ranks = rankdata(values, method="average")
    positions = np.arange(1, n)
    u_values = 2 * np.cumsum(ranks)[:-1] - positions * (n + 1)
    absolute_u = np.abs(u_values)
    cp_position = int(np.argmax(absolute_u) + 1)  # one-based last year before the shift
    statistic = float(absolute_u[cp_position - 1])
    p_value = min(1.0, float(2 * np.exp((-6 * statistic**2) / (n**3 + n**2))))

    return {
        "significant": p_value < PETTITT_ALPHA,
        "change_point_position": cp_position,
        "p_value": p_value,
        "statistic": statistic,
    }


def run_pettitt(series: pd.Series, code: str) -> dict[str, Any]:
    """Run Pettitt's test and map its one-based position to the corresponding year."""
    valid = series.dropna()
    if len(valid) < 10:
        raise ValueError(f"{code} has fewer than 10 valid annual values inside the arc mask.")

    result = pettitt_test(valid.to_numpy())
    cp_position = int(result["change_point_position"])
    candidate_year = int(valid.index[cp_position - 1])
    significant = bool(result["significant"])
    break_year: int | None = candidate_year if significant else None
    break_value: float | None = float(valid.loc[candidate_year]) if significant else None
    mean_before = float(valid.iloc[:cp_position].mean())
    mean_after = float(valid.iloc[cp_position:].mean())

    return {
        "Indicator": code,
        "Definition": INDEX_METADATA[code]["definition"],
        "Pettitt alpha": PETTITT_ALPHA,
        "Pettitt p-value method": "Analytical approximation",
        "Significant change point": significant,
        "Break year": break_year,
        "Break value": break_value,
        "Candidate change-point year": candidate_year,
        "Candidate position (1-based)": cp_position,
        "p-value": float(result["p_value"]),
        "Pettitt U statistic": float(result["statistic"]),
        "Mean before candidate": mean_before,
        "Mean after candidate": mean_after,
        "Difference after − before": mean_after - mean_before,
        "Valid annual values": int(len(valid)),
        "Missing annual values": int(series.isna().sum()),
    }


def style_axis(ax: plt.Axes, code: str, panel_letter: str | None = None) -> None:
    """Apply a clear journal-ready style shared by all individual panels."""
    ax.set_title(code, loc="center", pad=9)
    ax.set_xlabel("Year")
    ax.set_ylabel(INDEX_METADATA[code]["y_label"])
    ax.grid(axis="y", color=GRID_COLOUR, linewidth=0.7, alpha=0.9)
    ax.grid(axis="x", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#7A858C")
    ax.spines["bottom"].set_color("#7A858C")
    ax.tick_params(length=3.5, width=0.8)
    ax.set_xlim(1960.2, 2025.8)
    ax.set_xticks(np.arange(1965, 2026, 10))
    if panel_letter:
        ax.text(
            -0.14,
            1.04,
            panel_letter,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=13,
            fontweight="bold",
            color=TEXT_COLOUR,
            clip_on=False,
        )


def plot_series(
    ax: plt.Axes,
    series: pd.Series,
    pettitt: dict[str, Any],
    code: str,
    panel_letter: str | None = None,
) -> None:
    """Draw one annual series and, only when significant, its Pettitt breakpoint."""
    style_axis(ax, code, panel_letter)
    valid = series.dropna()
    ax.plot(valid.index, valid.values, color=LINE_COLOUR, linewidth=1.9, zorder=2)
    ax.scatter(valid.index, valid.values, color=POINT_COLOUR, s=13, linewidths=0, zorder=3)

    break_year = pettitt["Break year"]
    if break_year is not None:
        break_value = float(pettitt["Break value"])
        ax.axvline(
            break_year,
            color=BREAK_COLOUR,
            linestyle=(0, (4, 3)),
            linewidth=1.5,
            zorder=1,
        )
        ax.scatter(
            [break_year],
            [break_value],
            s=52,
            color=BREAK_COLOUR,
            edgecolor="white",
            linewidth=0.9,
            zorder=5,
        )
        ax.annotate(
            str(break_year),
            xy=(break_year, break_value),
            xytext=(6, 9),
            textcoords="offset points",
            color=BREAK_COLOUR,
            fontsize=9.5,
            fontweight="bold",
            ha="left",
            va="bottom",
        )


def make_figures(series_by_code: dict[str, pd.Series], pettitt_by_code: dict[str, dict[str, Any]]) -> None:
    """Export six individual panels and one vertical 3×2 multi-panel figure."""
    if FIGURES_DIR is None:
        raise RuntimeError("Figure output directory was not configured.")
    order = ["WSDI", "SU35", "TXx", "CDD", "R1mm", "PRCPTOT"]
    panel_letters = list("abcdef")

    for code, letter in zip(order, panel_letters, strict=True):
        fig, ax = plt.subplots(figsize=(6.7, 4.0))
        plot_series(ax, series_by_code[code], pettitt_by_code[code], code, panel_letter=letter)
        fig.subplots_adjust(left=0.16, right=0.97, bottom=0.16, top=0.88)
        destination = FIGURES_DIR / f"{code}_annual_arc_deforestation_pettitt.png"
        fig.savefig(destination, dpi=600)
        plt.close(fig)
        logging.info("Wrote %s", destination.name)

    # Sized as a single vertical page and rendered at 600 dpi. There is no
    # global title: the centred index codes are the only panel titles.
    fig, axes = plt.subplots(3, 2, figsize=(7.25, 10.15))
    for ax, code, letter in zip(axes.flat, order, panel_letters, strict=True):
        plot_series(ax, series_by_code[code], pettitt_by_code[code], code, panel_letter=letter)
    fig.subplots_adjust(left=0.14, right=0.98, bottom=0.065, top=0.965, hspace=0.47, wspace=0.32)
    destination = FIGURES_DIR / "annual_extremes_arc_deforestation_pettitt.png"
    fig.savefig(destination, dpi=600)
    plt.close(fig)
    logging.info("Wrote %s", destination.name)


def write_pettitt_workbook(
    pettitt_by_code: dict[str, dict[str, Any]],
    series_by_code: dict[str, pd.Series],
) -> Path:
    """Write the requested single XLSX with results and the plotted annual means."""
    if INDICES_DIR is None:
        raise RuntimeError("Index output directory was not configured.")
    destination = INDICES_DIR / "pettitt_breakpoints_arc_deforestation.xlsx"
    results = pd.DataFrame(pettitt_by_code.values())
    annual_series = pd.DataFrame(series_by_code)
    annual_series.index.name = "Year"

    with pd.ExcelWriter(destination, engine="openpyxl") as writer:
        results.to_excel(writer, sheet_name="Pettitt_results", index=False)
        annual_series.to_excel(writer, sheet_name="Arc_annual_series")

        for worksheet in writer.sheets.values():
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                column_letter = column_cells[0].column_letter
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 44)

    logging.info("Wrote %s", destination.name)
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Calculate annual climate-extreme indices from the three original "
            "BR-DWGD precipitation files and three original BR-DWGD Tmax files, "
            "aggregate them over the Arc of Deforestation, apply Pettitt's test, "
            "and generate figures."
        )
    )

    parser.add_argument(
        "--precipitation-files",
        nargs=3,
        required=True,
        metavar=("PR_1961_1980", "PR_1981_2000", "PR_2001_2025"),
        help=(
            "Three original BR-DWGD precipitation NetCDF files, preferably "
            "provided in chronological order."
        ),
    )
    parser.add_argument(
        "--tasmax-files",
        nargs=3,
        required=True,
        metavar=("TMAX_1961_1980", "TMAX_1981_2000", "TMAX_2001_2025"),
        help=(
            "Three original BR-DWGD daily maximum temperature NetCDF files, "
            "preferably provided in chronological order."
        ),
    )
    parser.add_argument(
        "--arc-shapefile",
        required=True,
        help="Path to the Arc of Deforestation shapefile.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help=(
            "Base output directory. Subdirectories 'indices' and 'figures' "
            "are created automatically."
        ),
    )

    return parser


def main(args: argparse.Namespace) -> None:
    """Run the complete calculation, regionalisation, Pettitt and plotting workflow."""
    global PRECIPITATION_FILES, TASMAX_FILES, SHAPEFILE, INDICES_DIR, FIGURES_DIR

    configure_logging()

    PRECIPITATION_FILES = [Path(path) for path in args.precipitation_files]
    TASMAX_FILES = [Path(path) for path in args.tasmax_files]
    SHAPEFILE = Path(args.arc_shapefile)

    output_dir = Path(args.output_dir)
    INDICES_DIR = output_dir / "indices"
    FIGURES_DIR = output_dir / "figures"

    INDICES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting annual climate-index workflow.")
    logging.info("Script revision: %s", SCRIPT_VERSION)

    tasmax, pr = open_inputs()
    indices = calculate_indices(tasmax, pr)

    index_files: dict[str, Path] = {}
    for code, index in indices.items():
        index_files[code] = write_index(index, code)

    arc = open_arc_geometry()
    series_by_code: dict[str, pd.Series] = {}
    pettitt_by_code: dict[str, dict[str, Any]] = {}

    for code, index_file in index_files.items():
        logging.info("Calculating the Arc of Deforestation mean for %s.", code)
        arc_mean = weighted_arc_mean(index_file, code, arc)
        series = arc_mean_to_series(arc_mean, code)
        series_by_code[code] = series
        pettitt_by_code[code] = run_pettitt(series, code)

    write_pettitt_workbook(pettitt_by_code, series_by_code)
    make_figures(series_by_code, pettitt_by_code)
    logging.info("Workflow completed successfully.")


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    try:
        main(args)
    except Exception as exc:
        logging.exception("Workflow failed: %s", exc)
        sys.exit(1)
