# Landsat land-surface-temperature analysis

## Objective

We analyzed land surface temperature (LST) over a representative sector of southeastern Brazilian Legal Amazonia within the Arc of Deforestation.

The analysis was designed to characterize surface thermal conditions in an area affected by intense land-use change, agricultural expansion, and hydroclimatic stress.

## Study area

The analyzed sector is located in southeastern Brazilian Legal Amazonia, within the Arc of Deforestation.

The approximate central coordinates of the mapped area are:

`10°36'01.00"S, 49°50'54.57"W`

We selected this area as a representative region showing strong land-use transformation and elevated surface thermal conditions.

## Data source

We obtained Landsat Collection 2 Level-2 Surface Temperature products from the U.S. Geological Survey (USGS) EarthExplorer platform.

Platform:

USGS EarthExplorer

Product:

Landsat Collection 2 Level-2 Surface Temperature Science Product

Sensor:

Landsat 8 OLI/TIRS

Surface-temperature band:

`ST_B10`

## Landsat scenes

The following Landsat 8 products were used in the analysis:

| Year | Landsat product ID | Sensor |
|---:|---|---|
| 2013 | `LC08_L2SP_230067_20130930_20200912_02_T1` | Landsat 8 OLI/TIRS |
| 2020 | `LC08_L2SP_001059_20200101_20200823_02_T1` | Landsat 8 OLI/TIRS |
| 2026 | `LC08_L2SP_233069_20260331_20260407_02_T1` | Landsat 8 OLI/TIRS |

The acquisition dates used in the analysis were selected to represent high-temperature conditions during the dry season in the southern Amazon region.

The selected dates were:

- 30 September 2013;
- [TO BE CONFIRMED FOR 2020];
- 31 March 2026.

The 2020 acquisition date should be verified against the Landsat product identifier before the archived repository release.

## Scene-selection criteria

Several candidate Landsat scenes were evaluated.

Scenes were selected according to the following criteria:

- representation of high-temperature conditions for the corresponding year;
- relevance to the dry-season thermal-stress context of southern Amazonia;
- low cloud coverage, preferentially below approximately 10–20%;
- adequate spatial coverage of the selected area of interest;
- representation of locations showing strong surface-temperature anomalies in the analyzed region.

We consulted meteorological information from official and operational sources when selecting representative high-temperature periods.

## Cloud and quality masking

We used quality-control information from the Landsat Collection 2 Level-2 products to remove contaminated pixels.

The `QA_PIXEL` layer was used to mask:

- clouds;
- cloud shadows;
- cirrus.

We also excluded saturated pixels from the analysis.

We used only valid surface-temperature pixels remaining after quality filtering to generate the final maps.

## Surface-temperature processing

The Landsat Collection 2 Level-2 `ST_B10` band was used to derive surface temperature.

The digital values were converted to physical temperature using the scale factor and additive offset applied in the analysis:

`Temperature (K) = ST_B10 × 0.00341802 + 149.0`

Temperature was then converted from Kelvin to degrees Celsius:

`LST (°C) = (ST_B10 × 0.00341802 + 149.0) - 273.15`

## Spatial processing

Processing was performed in:

`QGIS 3.34`

The main processing sequence was:

1. download Landsat Collection 2 Level-2 scenes;
2. apply quality masks using `QA_PIXEL`;
3. remove saturated pixels;
4. extract the `ST_B10` surface-temperature band;
5. apply the Landsat scale factor and additive offset;
6. convert temperature from Kelvin to degrees Celsius;
7. clip the resulting LST field to the selected area of interest;
8. classify temperatures into intervals for cartographic representation;
9. generate the final maps used in the manuscript.

## Temporal representation

Each mapped year corresponds to one individual Landsat scene acquired on a specific date.

The maps therefore represent selected scene-based surface-temperature conditions rather than:

- annual mean LST;
- seasonal mean LST;
- temporal composites;
- multi-scene mosaics.

Consequently, interpret differences among years as differences among selected representative scenes rather than as a continuous annual temperature trend.

## Cartographic representation

The resulting LST fields were classified into temperature intervals for visualization.

The final maps illustrate the spatial distribution and intensity of surface thermal conditions within the selected southeastern Amazonian sector.

## Interpretation

LST represents the thermal state of the land surface and should not be interpreted as equivalent to near-surface air temperature.

The analysis is used as an indicator of spatial surface thermal stress and its relationship with land-cover transformation and hydroclimatic conditions.

## Software

Processing software:

`QGIS 3.34`
