# Landsat land-surface-temperature analysis

## Objective

We analyzed land surface temperature (LST) over a representative sector of southeastern Brazilian Legal Amazonia within the Arc of Deforestation.

The analysis was designed to characterize surface thermal conditions in an area affected by intense land-use change, agricultural expansion, and hydroclimatic stress.


## Study areas

The LST analysis focused on representative critical sectors of southeastern Brazilian Legal Amazonia and the Arc of Deforestation.

Rather than enforcing an identical Landsat footprint for all analyzed years, scenes were selected to represent locations exhibiting particularly high surface-temperature conditions and overlapping areas highlighted by the other environmental analyses in the study.

The selected sectors therefore represent comparable high-stress environments within the deforestation frontier, but they should not be interpreted as an identical spatial footprint observed repeatedly through time.

Querência and its surrounding region were used as an important geographic reference because this sector lies within a highly transformed portion of the southern and southeastern Amazonian frontier.


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

The following Landsat 8 Collection 2 Level-2 products were used:

| Year | Landsat product ID | Acquisition date | Sensor |
|---:|---|---|---|
| 2013 | `LC08_L2SP_230067_20130930_20200912_02_T1` | 2013-09-30 | Landsat 8 OLI/TIRS |
| 2020 | `LC08_L2SP_223068_20201002_20201015_02_T1` | 2020-10-02 | Landsat 8 OLI/TIRS |
| 2026 | `LC08_L2SP_233069_20260331_20260407_02_T1` | 2026-03-31 | Landsat 8 OLI/TIRS |

The acquisition dates used in the analysis were selected to represent high-temperature conditions during the dry season in the southern Amazon region.

The selected dates were:

- 30 September 2013;
- [TO BE CONFIRMED FOR 2020];
- 31 March 2026.

The 2020 acquisition date should be verified against the Landsat product identifier before the archived repository release.

## Scene-selection criteria

## Scene-selection criteria

Multiple Landsat scenes were evaluated for each analyzed year.

Scene selection prioritized:

- periods associated with particularly high temperatures during the corresponding year;
- low cloud contamination, preferentially below approximately 10–20%;
- adequate coverage of sectors within the southern and southeastern Brazilian Legal Amazon and the Arc of Deforestation;
- areas exhibiting pronounced surface thermal conditions;
- geographic consistency with municipalities and environmental-pressure areas identified in the other analyses of the study.

The selected scenes were therefore intended to characterize representative critical thermal conditions within the deforestation frontier rather than to provide repeated observations of one fixed Landsat footprint.

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

## Temporal and spatial representation

Each analyzed year is represented by one individual Landsat scene acquired on a specific date.

The three scenes do not necessarily represent the same Landsat path/row or an identical spatial footprint. They were selected as representative high-temperature sectors within the broader southern and southeastern Amazonian deforestation frontier.

Accordingly, the analysis should be interpreted as a comparison of representative critical surface-temperature conditions observed in 2013, 2020, and 2026, rather than as a pixel-by-pixel temporal change analysis of the same geographic area.

The maps are also not annual means, seasonal means, mosaics, or multi-scene composites.

## Cartographic representation

The resulting LST fields were classified into temperature intervals for visualization.

The final maps illustrate the spatial distribution and intensity of surface thermal conditions within the selected southeastern Amazonian sector.

## Interpretation

LST represents the thermal state of the land surface and should not be interpreted as equivalent to near-surface air temperature.

The analysis is used as an indicator of spatial surface thermal stress and its relationship with land-cover transformation and hydroclimatic conditions.

## Software

Processing software:

`QGIS 3.34`
