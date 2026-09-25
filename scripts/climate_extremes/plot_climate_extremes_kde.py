"""Compare KDEs of annual Arc of Deforestation climate indices.

The six annual NetCDF indices are supplied through ``--indices-dir`` and are
spatially aggregated over the Arc of Deforestation using the same regionmask
and cosine-latitude weighting as the index/Pettitt workflow.

Kernel density estimates are calculated from annual regional means for:

- 1985–2004;
- 2005–2025.

This is a distributional comparison of annual regional means, not a KDE of all
grid cells. Each curve therefore represents 20 and 21 annual values,
respectively.

Expected annual-index files
---------------------------
WSDI_annual.nc
SU35_annual.nc
TXx_annual.nc
CDD_annual.nc
R1mm_annual.nc
PRCPTOT_annual.nc

Inputs and outputs are supplied explicitly on the command line.
"""

from __future__ import annotations

import argparse
import logging
import sys
import warnings
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import regionmask
import xarray as xr
from scipy.stats import gaussian_kde


# =============================================================================
# USER CONFIGURATION
# =============================================================================

INDICES_DIR: Path | None = None
FIGURES_DIR: Path | None = None
SHAPEFILE: Path | None = None

PERIOD_1 = (1985, 2004)
PERIOD_2 = (2005, 2025)
ORDER = ("WSDI", "SU35", "TXx", "CDD", "R1mm", "PRCPTOT")
PANEL_LETTERS = tuple("abcdef")
INDEX_FILES: dict[str, Path] = {}


# =============================================================================
# FIGURE STYLE
# =============================================================================

# Graphite and muted plum are deliberately non-directional: neither colour
# implies cooling/warming or wetting/drying, including in temperature panels.
PERIOD_1_COLOUR = "#4E5A63"
PERIOD_2_COLOUR = "#8A6E88"
GRID_COLOUR = "#D9DEE2"
TEXT_COLOUR = "#20282D"

INDEX_METADATA: dict[str, dict[str, str]] = {
    "WSDI": {"x_label": "Days"},
    "SU35": {"x_label": "Days"},
    "TXx": {"x_label": "Temperature (°C)"},
    "CDD": {"x_label": "Days"},
    "R1mm": {"x_label": "Days"},
    "PRCPTOT": {"x_label": "Precipitation (mm)"},
}

# Fixed density-axis maxima requested for the two temperature-related counts.
# Other panels retain automatic limits so their distributional shapes remain
# fully visible.
KDE_Y_MAX: dict[str, float] = {
    "WSDI": 0.025,
    "SU35": 0.06,
}

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


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} was not found: {path}")


def open_arc_geometry() -> gpd.GeoDataFrame:
    """Read the study-region polygon in the geographical CRS used by the grid."""
    if SHAPEFILE is None:
        raise RuntimeError("Arc shapefile path was not configured.")
    require_file(SHAPEFILE, "Arc of Deforestation shapefile")
    arc = gpd.read_file(SHAPEFILE)
    arc = arc.loc[arc.geometry.notna()].copy()
    if arc.empty:
        raise ValueError(f"The shapefile has no valid geometries: {SHAPEFILE}")
    if arc.crs is None:
        warnings.warn("The arc shapefile has no CRS; EPSG:4326 is assumed.", stacklevel=2)
        return arc.set_crs("EPSG:4326")
    return arc.to_crs("EPSG:4326")


def coordinate_name(da: xr.DataArray, candidates: tuple[str, ...], label: str) -> str:
    """Find a coordinate/dimension name without assuming a particular NetCDF convention."""
    names = list(da.coords) + [name for name in da.dims if name not in da.coords]
    lookup = {name.lower(): name for name in names}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    raise ValueError(f"Could not identify the {label} coordinate. Available: {names}")


def standardise_coordinates(da: xr.DataArray) -> xr.DataArray:
    """Rename usual coordinate aliases to time, lat and lon for regionmask."""
    time = coordinate_name(da, ("time", "date", "datetime"), "time")
    lat = coordinate_name(da, ("lat", "latitude", "y"), "latitude")
    lon = coordinate_name(da, ("lon", "longitude", "x"), "longitude")
    rename = {old: new for old, new in ((time, "time"), (lat, "lat"), (lon, "lon")) if old != new}
    return da.rename(rename) if rename else da


def year_from_timestamp(timestamp: Any) -> int:
    """Support numpy datetimes and cftime calendar objects."""
    if hasattr(timestamp, "year"):
        return int(timestamp.year)
    return int(np.datetime_as_string(timestamp, unit="Y"))


def annual_arc_mean(index_file: Path, code: str, arc: gpd.GeoDataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return annual, cosine-latitude-weighted Arc means from one index NetCDF."""
    require_file(index_file, f"Annual {code} NetCDF")
    with xr.open_dataset(index_file, chunks={"time": -1}) as ds:
        if code not in ds.data_vars:
            raise ValueError(f"{index_file.name} does not contain variable '{code}'.")
        da = standardise_coordinates(ds[code])
        if da["lat"].ndim != 1 or da["lon"].ndim != 1:
            raise ValueError(f"{code} must have a rectilinear 1-D latitude/longitude grid.")

        if float(da["lon"].min()) >= 0 and float(arc.total_bounds[0]) < 0:
            da = da.assign_coords(lon=((da["lon"] + 180) % 360) - 180).sortby("lon")

        mask = regionmask.mask_3D_geopandas(
            arc,
            da["lon"],
            da["lat"],
            overlap=True,
            wrap_lon=None,
        ).any(dim="region")
        if not bool(mask.any()):
            raise ValueError(f"The Arc shapefile does not overlap {index_file.name}.")

        latitude_weights = np.cos(np.deg2rad(da["lat"]))
        regional = da.where(mask).weighted(latitude_weights).mean(("lat", "lon")).compute()
        years = np.asarray([year_from_timestamp(value) for value in regional["time"].values], dtype=int)
        values = np.asarray(regional.values, dtype=float)
    return years, values


def select_period(years: np.ndarray, values: np.ndarray, period: tuple[int, int], code: str) -> np.ndarray:
    """Select finite annual means for one inclusive period and validate sample size."""
    start, end = period
    selected = values[(years >= start) & (years <= end)]
    selected = selected[np.isfinite(selected)]
    expected_count = end - start + 1
    if len(selected) != expected_count:
        raise ValueError(
            f"{code}: expected {expected_count} finite annual values for {start}–{end}, "
            f"but found {len(selected)}. Check the annual NetCDF time axis and mask."
        )
    if len(selected) < 2:
        raise ValueError(f"{code}: at least two years are required for a KDE.")
    return selected


def evaluation_grid(period_1: np.ndarray, period_2: np.ndarray) -> np.ndarray:
    """Build one x-grid shared by both curves so their shapes are comparable."""
    lower = float(min(period_1.min(), period_2.min()))
    upper = float(max(period_1.max(), period_2.max()))
    span = upper - lower
    if np.isclose(span, 0.0):
        span = max(abs(lower) * 0.08, 1.0)
    padding = span * 0.16
    return np.linspace(lower - padding, upper + padding, 512)


def kde_values(values: np.ndarray, x_grid: np.ndarray, code: str, period: tuple[int, int]) -> np.ndarray:
    """Evaluate Scott's Gaussian KDE, including an explicit constant-series fallback."""
    if np.isclose(np.nanstd(values, ddof=1), 0.0):
        # A KDE covariance is singular for equal values. Preserve the visible
        # location with a deliberately narrow Gaussian rather than failing.
        bandwidth = max((x_grid.max() - x_grid.min()) / 100, abs(values[0]) * 0.01, 1e-6)
        logging.warning(
            "%s has no interannual variation in %s–%s; using a narrow Gaussian fallback.",
            code,
            period[0],
            period[1],
        )
        return np.exp(-0.5 * ((x_grid - values[0]) / bandwidth) ** 2) / (bandwidth * np.sqrt(2 * np.pi))
    return gaussian_kde(values, bw_method="scott")(x_grid)


def style_axis(ax: plt.Axes, code: str, panel_letter: str | None = None) -> None:
    """Apply the same clear, journal-ready language as the Pettitt figure."""
    ax.set_title(code, loc="center", pad=9)
    ax.set_xlabel(INDEX_METADATA[code]["x_label"])
    ax.set_ylabel("Kernel density")
    ax.grid(axis="y", color=GRID_COLOUR, linewidth=0.7, alpha=0.9)
    ax.grid(axis="x", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#7A858C")
    ax.spines["bottom"].set_color("#7A858C")
    ax.tick_params(length=3.5, width=0.8)
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


def plot_kde(
    ax: plt.Axes,
    period_1: np.ndarray,
    period_2: np.ndarray,
    code: str,
    panel_letter: str | None = None,
) -> None:
    """Draw two period KDEs for one climate indicator."""
    style_axis(ax, code, panel_letter)
    x_grid = evaluation_grid(period_1, period_2)
    density_1 = kde_values(period_1, x_grid, code, PERIOD_1)
    density_2 = kde_values(period_2, x_grid, code, PERIOD_2)
    label_1 = f"{PERIOD_1[0]}–{PERIOD_1[1]}"
    label_2 = f"{PERIOD_2[0]}–{PERIOD_2[1]}"

    ax.plot(x_grid, density_1, color=PERIOD_1_COLOUR, linewidth=2.1, label=label_1, zorder=3)
    ax.plot(x_grid, density_2, color=PERIOD_2_COLOUR, linewidth=2.1, label=label_2, zorder=4)
    ax.fill_between(x_grid, 0, density_1, color=PERIOD_1_COLOUR, alpha=0.10, zorder=1)
    ax.fill_between(x_grid, 0, density_2, color=PERIOD_2_COLOUR, alpha=0.10, zorder=2)
    if code in KDE_Y_MAX:
        ax.set_ylim(0, KDE_Y_MAX[code])

    # One legend is sufficient for the shared two-period colour scheme. It is
    # retained only in WSDI, both in the individual figure and panel (a).
    if code == "WSDI":
        legend = ax.legend(
            loc="upper right",
            frameon=True,
            fontsize=8.5,
            borderpad=0.45,
            handlelength=2.0,
        )
        legend.get_frame().set_facecolor("white")
        legend.get_frame().set_edgecolor("#C7CDD1")
        legend.get_frame().set_alpha(0.94)


def make_figures(period_data: dict[str, tuple[np.ndarray, np.ndarray]]) -> None:
    """Export six individual figures plus portrait and landscape composites."""
    if FIGURES_DIR is None:
        raise RuntimeError("Figure output directory was not configured.")
    for code, letter in zip(ORDER, PANEL_LETTERS, strict=True):
        fig, ax = plt.subplots(figsize=(6.7, 4.0))
        values_1, values_2 = period_data[code]
        plot_kde(ax, values_1, values_2, code, panel_letter=letter)
        fig.subplots_adjust(left=0.16, right=0.97, bottom=0.16, top=0.88)
        output = FIGURES_DIR / f"{code}_kde_1985_2004_vs_2005_2025.png"
        fig.savefig(output, dpi=600)
        plt.close(fig)
        logging.info("Wrote %s", output.name)

    fig, axes = plt.subplots(3, 2, figsize=(7.25, 10.15))
    for ax, code, letter in zip(axes.flat, ORDER, PANEL_LETTERS, strict=True):
        values_1, values_2 = period_data[code]
        plot_kde(ax, values_1, values_2, code, panel_letter=letter)
    fig.subplots_adjust(left=0.14, right=0.98, bottom=0.065, top=0.965, hspace=0.47, wspace=0.32)
    output = FIGURES_DIR / "kde_extremes_1985_2004_vs_2005_2025.png"
    fig.savefig(output, dpi=600)
    plt.close(fig)
    logging.info("Wrote %s", output.name)

    # Landscape version: 2 rows × 3 columns, sized for a full horizontal page.
    fig, axes = plt.subplots(2, 3, figsize=(11.7, 7.6))
    for ax, code, letter in zip(axes.flat, ORDER, PANEL_LETTERS, strict=True):
        values_1, values_2 = period_data[code]
        plot_kde(ax, values_1, values_2, code, panel_letter=letter)
    fig.subplots_adjust(left=0.095, right=0.99, bottom=0.10, top=0.95, hspace=0.47, wspace=0.34)
    output = FIGURES_DIR / "kde_extremes_1985_2004_vs_2005_2025_horizontal.png"
    fig.savefig(output, dpi=600)
    plt.close(fig)
    logging.info("Wrote %s", output.name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Calculate Gaussian KDEs of Arc-averaged annual climate-extreme "
            "indices for 1985–2004 and 2005–2025."
        )
    )
    parser.add_argument(
        "--indices-dir",
        required=True,
        help=(
            "Directory containing WSDI_annual.nc, SU35_annual.nc, "
            "TXx_annual.nc, CDD_annual.nc, R1mm_annual.nc and PRCPTOT_annual.nc."
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
        help="Directory where KDE figures will be written.",
    )
    return parser


def main(args: argparse.Namespace) -> None:
    global INDICES_DIR, FIGURES_DIR, SHAPEFILE, INDEX_FILES

    configure_logging()

    INDICES_DIR = Path(args.indices_dir)
    FIGURES_DIR = Path(args.output_dir)
    SHAPEFILE = Path(args.arc_shapefile)
    INDEX_FILES = {
        code: INDICES_DIR / f"{code}_annual.nc"
        for code in ORDER
    }

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    arc = open_arc_geometry()
    period_data: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    for code in ORDER:
        logging.info("Preparing annual Arc means and KDE samples for %s.", code)
        years, values = annual_arc_mean(INDEX_FILES[code], code, arc)
        period_data[code] = (
            select_period(years, values, PERIOD_1, code),
            select_period(years, values, PERIOD_2, code),
        )

    make_figures(period_data)
    logging.info("KDE workflow completed successfully.")


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    try:
        main(args)
    except Exception as exc:
        logging.exception("KDE workflow failed: %s", exc)
        sys.exit(1)
