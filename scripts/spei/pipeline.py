"""BR-DWGD -> monthly climatic water balance -> SPEI pipeline."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

try:
    import dask.array  # noqa: F401
    HAS_DASK = True
except ImportError:
    HAS_DASK = False

from spatial import crop_bbox, legal_amazon_mask, read_geometry
from spei_statistics import calculate_spei

PR_FILES = (
    "pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "pr_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
)
ETO_FILES = (
    "ETo_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "ETo_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
    "ETo_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc",
)


def _open_series(directory: Path, filenames: tuple[str, ...], variable: str) -> xr.DataArray:
    paths = [directory / name for name in filenames]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing input file(s):\n" + "\n".join(missing))

    chunks = {"time": 366, "latitude": 80, "longitude": 80} if HAS_DASK else None
    datasets = [
        xr.open_dataset(
            path,
            decode_cf=True,
            mask_and_scale=True,
            chunks=chunks,
        )
        for path in paths
    ]
    for path, ds in zip(paths, datasets, strict=True):
        if variable not in ds:
            raise KeyError(f"Variable {variable!r} not found in {path}")

    arrays = [ds[variable] for ds in datasets]
    result = xr.concat(arrays, dim="time", coords="minimal", compat="equals")
    result = result.sortby("time")

    if result.get_index("time").duplicated().any():
        raise ValueError(f"Duplicate timestamps detected in {variable}")

    units = result.attrs.get("units", "")
    if units != "mm":
        raise ValueError(f"Expected {variable} units='mm', found {units!r}")
    return result


def _validate_daily_time(time: xr.DataArray, start: str, end: str) -> None:
    actual = pd.DatetimeIndex(time.values)
    expected = pd.date_range(start, end, freq="D")
    if not actual.equals(expected):
        missing = expected.difference(actual)
        extra = actual.difference(expected)
        raise ValueError(
            "Daily time axis is not complete. "
            f"Expected {start}..{end}; missing={len(missing)}, extra={len(extra)}"
        )


def _validate_same_grid(pr: xr.DataArray, eto: xr.DataArray) -> None:
    for coord in ("latitude", "longitude", "time"):
        if not np.array_equal(pr[coord].values, eto[coord].values):
            raise ValueError(f"Precipitation and ETo do not share identical {coord} coordinates")


def prepare_monthly_balance(
    precipitation_dir: Path,
    eto_dir: Path,
    shapefile: Path,
) -> tuple[xr.DataArray, xr.DataArray, object, tuple[float, float, float, float], str]:
    """Read BR-DWGD, bbox-crop, aggregate monthly, and calculate P-ETo."""
    geometry, bounds, source_crs = read_geometry(shapefile)

    pr = _open_series(precipitation_dir, PR_FILES, "pr")
    eto = _open_series(eto_dir, ETO_FILES, "ETo")

    _validate_daily_time(pr.time, "1961-01-01", "2025-12-31")
    _validate_daily_time(eto.time, "1961-01-01", "2025-12-31")
    _validate_same_grid(pr, eto)

    pr = crop_bbox(pr, bounds)
    eto = crop_bbox(eto, bounds)

    # Strict monthly totals. The preceding daily validation guarantees that no
    # calendar day is absent from the series.
    pr_monthly = pr.resample(time="MS").sum(skipna=False)
    eto_monthly = eto.resample(time="MS").sum(skipna=False)
    balance = (pr_monthly - eto_monthly).rename("climatic_water_balance")
    balance.attrs.update(
        long_name="Monthly climatic water balance (precipitation minus reference evapotranspiration)",
        units="mm",
        precipitation_source="BR-DWGD pr",
        evapotranspiration_source="BR-DWGD ETo",
    )

    mask = legal_amazon_mask(balance.latitude, balance.longitude, geometry)
    return balance, mask, geometry, bounds, source_crs


def build_spei_dataset(
    spei: xr.DataArray,
    params: xr.DataArray,
    mask: xr.DataArray,
    *,
    scale: int,
    shapefile: Path,
    bounds: tuple[float, float, float, float],
    source_crs: str,
) -> xr.Dataset:
    """Mask to Legal Amazon and attach reproducibility metadata."""
    spei_masked = spei.where(mask).astype("float32")
    params_masked = params.where(mask).astype("float32")
    ds = xr.Dataset({f"spei_{scale}": spei_masked, "fit_parameters": params_masked})

    ds[f"spei_{scale}"].attrs.update(
        long_name=f"Standardized Precipitation-Evapotranspiration Index ({scale}-month)",
        standard_name="standardized_precipitation_evapotranspiration_index",
        units="1",
        description=(
            "Positive values indicate wetter-than-normal climatic water balance and negative "
            "values indicate drier-than-normal conditions."
        ),
    )
    ds["fit_parameters"].attrs.update(
        long_name="Three-parameter log-logistic/GLO fit parameters by calendar month",
        description="parameter coordinate contains xi (location), alpha (scale), kappa (shape)",
    )
    ds.attrs.update(
        title=f"BR-DWGD SPEI-{scale} for the Brazilian Legal Amazon",
        source=(
            "Brazilian Daily Weather Gridded Data (BR-DWGD) precipitation (pr) and reference "
            "evapotranspiration (ETo), version 3.2.4"
        ),
        temporal_coverage="1961-01-01 to 2025-12-31",
        calibration_period="1981-01-01 to 2010-12-31",
        spei_scale_months=scale,
        climatic_water_balance="monthly precipitation minus monthly ETo, in mm",
        accumulation_kernel="unshifted rectangular rolling sum",
        distribution="three-parameter log-Logistic (Generalized Logistic/GLO parameterisation)",
        fitting_method="unbiased probability-weighted moments (ub-PWM) converted to L-moments",
        standardization="fitted GLO CDF transformed with inverse standard normal CDF",
        probability_clipping=(
            "CDF probabilities are clipped only at float64 machine epsilon to avoid +/- infinity"
        ),
        spatial_domain="Brazilian Legal Amazon; cell centres inside supplied polygon",
        shapefile=shapefile.name,
        shapefile_source_crs=source_crs,
        shapefile_processing_crs="EPSG:4326",
        shapefile_bounds_wgs84=(
            f"west={bounds[0]:.8f}, south={bounds[1]:.8f}, "
            f"east={bounds[2]:.8f}, north={bounds[3]:.8f}"
        ),
        note_initial_values=(
            f"For SPEI-{scale}, the first {scale - 1} month(s) are undefined because the full "
            "accumulation window is not available."
        ),
    )
    return ds


def write_netcdf(ds: xr.Dataset, path: Path) -> None:
    """Write a compressed NetCDF atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    encoding = {}
    for name, da in ds.data_vars.items():
        chunks = []
        for dim in da.dims:
            if dim == "time":
                chunks.append(min(120, da.sizes[dim]))
            elif dim in ("latitude", "longitude"):
                chunks.append(min(80, da.sizes[dim]))
            else:
                chunks.append(da.sizes[dim])
        encoding[name] = {
            "zlib": True,
            "complevel": 4,
            "shuffle": True,
            "dtype": "float32",
            "chunksizes": tuple(chunks),
            "_FillValue": np.float32(-9999.0),
        }
    engines = xr.backends.list_engines()
    if "netcdf4" in engines:
        ds.to_netcdf(tmp, engine="netcdf4", encoding=encoding)
    else:
        # Fallback mainly for lightweight environments. Production use should
        # install netCDF4 as listed in requirements.txt to retain compression.
        fallback_encoding = {
            name: {"dtype": "float32", "_FillValue": np.float32(-9999.0)}
            for name in ds.data_vars
        }
        ds.to_netcdf(tmp, engine="scipy", encoding=fallback_encoding)
    tmp.replace(path)

