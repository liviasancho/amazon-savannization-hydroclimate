"""Spatial utilities for the Legal Amazon domain."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import shapely
import xarray as xr


def read_geometry(shapefile: Path) -> tuple[object, tuple[float, float, float, float], str]:
    """Read, validate and transform a shapefile geometry to EPSG:4326."""
    gdf = gpd.read_file(shapefile)
    if gdf.empty:
        raise ValueError(f"Shapefile has no features: {shapefile}")
    if gdf.crs is None:
        raise ValueError(f"Shapefile has no CRS: {shapefile}")
    source_crs = str(gdf.crs)
    if not gdf.geometry.is_valid.all():
        gdf["geometry"] = gdf.geometry.make_valid()
    gdf = gdf.to_crs("EPSG:4326")
    geometry = gdf.geometry.union_all()
    return geometry, tuple(map(float, gdf.total_bounds)), source_crs


def crop_bbox(ds: xr.Dataset | xr.DataArray, bounds: tuple[float, float, float, float]):
    """Crop to (west, south, east, north), independent of coordinate ordering."""
    west, south, east, north = bounds
    lat = ds["latitude"]
    lon = ds["longitude"]

    lat_slice = slice(south, north) if float(lat[0]) < float(lat[-1]) else slice(north, south)
    lon_slice = slice(west, east) if float(lon[0]) < float(lon[-1]) else slice(east, west)
    return ds.sel(latitude=lat_slice, longitude=lon_slice)


def legal_amazon_mask(
    latitude: xr.DataArray, longitude: xr.DataArray, geometry: object
) -> xr.DataArray:
    """Create a boolean mask based on grid-cell centres inside the geometry."""
    lon2d, lat2d = np.meshgrid(longitude.values, latitude.values)
    mask = shapely.contains_xy(geometry, lon2d, lat2d)
    return xr.DataArray(
        mask,
        coords={"latitude": latitude, "longitude": longitude},
        dims=("latitude", "longitude"),
        name="legal_amazon_mask",
    )

