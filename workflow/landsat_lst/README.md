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

## Scenes used

| Year | Product ID | Acquisition date | Path/Row |
|---:|---|---|---|
| 2013 | `LC08_L2SP_230067_20130930_20200912_02_T1` | 2013-09-30 | 230/067 |
| 2020 | `LC08_L2SP_223068_20201002_20201015_02_T1` | 2020-10-02 | 223/068 |
| 2026 | `LC08_L2SP_233069_20260331_20260407_02_T1` | 2026-03-31 | 233/069 |



## Geographic selection

The workflow does not use one fixed Landsat footprint across all three years.

For each year, a representative critical scene was selected within the southern and southeastern Brazilian Legal Amazon and the Arc of Deforestation.

Selection favored areas displaying strong surface thermal conditions and overlapping municipalities or sectors highlighted by the land-use and hydroclimatic analyses.

The scenes should therefore be treated as representative case-study locations within the broader deforestation frontier rather than as repeated observations of an identical geographic footprint.


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
