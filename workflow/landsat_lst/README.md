# Landsat land-surface-temperature workflow

This directory documents the QGIS workflow for deriving land surface temperature (LST) maps from Landsat 8 Collection 2 Level-2 products.

## Software

QGIS 3.34

## Data access

Landsat products were obtained through:

USGS EarthExplorer

Product type:

Landsat Collection 2 Level-2 Surface Temperature Science Product

Sensor:

Landsat 8 OLI/TIRS

Surface-temperature band:

`ST_B10`

## Scenes used

| Year | Product ID |
|---:|---|
| 2013 | `LC08_L2SP_230067_20130930_20200912_02_T1` |
| 2020 | `LC08_L2SP_001059_20200101_20200823_02_T1` |
| 2026 | `LC08_L2SP_233069_20260331_20260407_02_T1` |

We are verifying the exact 2020 acquisition date before releasing the archived repository.

## Area of interest

The analysis focuses on a representative sector of southeastern Brazilian Legal Amazonia within the Arc of Deforestation.

Approximate central coordinate:

`10°36'01.00"S, 49°50'54.57"W`

## Workflow

### 1. Download Landsat products

Download the selected Landsat Collection 2 Level-2 scenes from USGS EarthExplorer.

### 2. Apply quality masks

Use the Landsat quality layers to exclude invalid or contaminated observations.

Pixels affected by the following conditions are removed:

- clouds;
- cloud shadows;
- cirrus;
- saturation.

### 3. Extract surface temperature

Use:

`ST_B10`

from the Collection 2 Level-2 Surface Temperature Science Product.

### 4. Convert digital values to temperature

Apply:

`Temperature (K) = ST_B10 × 0.00341802 + 149.0`

Then convert to Celsius:

`LST (°C) = Temperature (K) - 273.15`

or equivalently:

`LST (°C) = (ST_B10 × 0.00341802 + 149.0) - 273.15`

### 5. Clip to the area of interest

Clip the resulting surface-temperature layer to the selected southeastern Amazonian study sector.

### 6. Classify temperature

Classify the LST values into temperature intervals for cartographic representation.

### 7. Generate final maps

Produce one LST map for each selected Landsat scene.

The final manuscript figure contains the maps corresponding to:

- 2013;
- 2020;
- 2026.

## Important temporal interpretation

Each year is represented by an individual Landsat scene.

The resulting maps are not annual or seasonal composites and should not be interpreted as annual mean land-surface temperature.

They represent selected high-temperature surface conditions for the corresponding acquisition dates.

## Related documentation

Detailed methodology:

`docs/methodology_lst.md`

General data provenance:

`data/README.md`

Overall study provenance:

`docs/provenance.md`
