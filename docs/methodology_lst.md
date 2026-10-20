# Landsat land-surface-temperature analysis

## Objective

We analysed land surface temperature (LST) in representative critical sectors of the southern and southeastern Brazilian Legal Amazon within the broader Arc of Deforestation.

The analysis was designed to characterise surface thermal conditions in areas affected by land-use transformation and hydroclimatic stress.

## Geographic selection

The LST analysis did not enforce one identical Landsat footprint for all analysed years.

Instead, scenes were selected to represent locations exhibiting pronounced surface-temperature conditions and overlapping sectors highlighted by the other environmental analyses in the study.

The selected scenes therefore represent comparable high-stress environments within the deforestation frontier but should not be interpreted as repeated observations of one identical spatial footprint.

Querência and surrounding sectors were used as an important geographic reference within the southern and southeastern Amazonian frontier.

The approximate analysis extent was delimited by the following geographic coordinates:

1. 13°11'21"S, 52°36'39"W
2. 08°42'11"S, 52°34'01"W
3. 08°47'24"S, 47°35'32"W
4. 13°16'29"S, 47°26'58"W

These coordinates document the spatial extent used to contextualise the analysed sectors rather than a common Landsat footprint shared by all three scenes.

## Data source

Landsat Collection 2 Level-2 Surface Temperature products were obtained from the U.S. Geological Survey (USGS) EarthExplorer platform.

Platform:

`USGS EarthExplorer`

Product:

`Landsat Collection 2 Level-2 Surface Temperature Science Product`

Sensor:

`Landsat 8 OLI/TIRS`

Surface-temperature band:

`ST_B10`

## Landsat scenes

The following products were used in the original analysis:

| Year | Landsat product ID | Acquisition date | Path/Row |
|---:|---|---|---|
| 2013 | `LC08_L2SP_230067_20130930_20200912_02_T1` | 2013-09-30 | 230/067 |
| 2020 | `LC08_L2SP_223068_20201002_20201015_02_T1` | 2020-10-02 | 223/068 |
| 2026 | `LC08_L2SP_233069_20260331_20260407_02_T1` | 2026-03-31 | 233/069 |

The 2020 scene was subsequently re-verified in the USGS catalogue.

The original locally archived products used for 2013 and 2026 could not be fully re-verified under the current USGS catalogue configuration during repository preparation. This issue is documented in:

`docs/data_availability_notes.md`

## Scene-selection criteria

Multiple candidate Landsat scenes were evaluated.

Scene selection prioritised:

- periods associated with high temperatures during the corresponding year;
- low cloud contamination, preferentially below approximately 10–20%;
- coverage of relevant sectors of the southern and southeastern Brazilian Legal Amazon;
- locations exhibiting pronounced surface thermal conditions;
- spatial consistency with municipalities and environmental-pressure regions highlighted by the other analyses in the study.

The selected scenes were therefore intended to characterise representative critical thermal conditions rather than to provide a controlled repeated observation of one fixed Landsat footprint.

## Cloud and quality masking

Quality-control information from the Landsat Collection 2 Level-2 products was used to remove contaminated observations.

The `QA_PIXEL` layer was used to mask:

- clouds;
- cloud shadows;
- cirrus.

Saturated pixels were also excluded.

Only valid surface-temperature pixels remaining after quality filtering were used in the final maps.

## Surface-temperature processing

The Landsat Collection 2 Level-2 `ST_B10` band was used to derive surface temperature.

Digital values were converted to physical temperature using:

`Temperature (K) = ST_B10 × 0.00341802 + 149.0`

Temperature was then converted from Kelvin to degrees Celsius:

`LST (°C) = (ST_B10 × 0.00341802 + 149.0) - 273.15`

## Spatial processing

Processing was performed in:

`QGIS 3.34`

The workflow consisted of:

1. downloading Landsat Collection 2 Level-2 scenes;
2. applying quality masks using `QA_PIXEL`;
3. excluding saturated pixels;
4. extracting `ST_B10`;
5. applying the temperature scale factor and additive offset;
6. converting temperature from Kelvin to Celsius;
7. clipping the resulting LST field to the selected area of interest;
8. classifying temperature values into intervals for cartographic representation;
9. generating the final maps used in the manuscript.

## Temporal and spatial interpretation

Each analysed year is represented by one individual Landsat scene acquired on a specific date.

The three scenes do not necessarily represent the same Landsat path/row or an identical spatial footprint.

Accordingly, the maps should be interpreted as representative critical surface-temperature conditions observed in 2013, 2020, and 2026 rather than as a pixel-by-pixel temporal change analysis of one fixed geographic area.

The maps are not annual means, seasonal means, mosaics, or multi-scene composites.

## Cartographic representation

The resulting LST fields were classified into temperature intervals for visualisation and assembled into the final manuscript figure.

## Interpretation

LST represents the thermal state of the land surface and should not be interpreted as equivalent to near-surface air temperature.

The analysis is used as an indicator of surface thermal stress in regions affected by land-cover transformation and hydroclimatic pressure.

## Data-availability limitation

The original 2013 and 2026 files used in the analysis are retained locally by the authors, but their exact catalogue availability is currently being clarified with USGS.

No substitute scenes were introduced into the present repository release.

Future releases may update the provenance information if further clarification is provided by USGS.
