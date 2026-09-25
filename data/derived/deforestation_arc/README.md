# Arc of Deforestation

This directory contains the Arc of Deforestation polygon derived for the study.

## Purpose

The polygon represents the recent deforestation frontier within the Brazilian Legal Amazon.

## Source deforestation data

Deforestation data were obtained from PRODES for 2024.

Provider:
Instituto Nacional de Pesquisas Espaciais (INPE) / TerraBrasilis / PRODES

Source dataset:

https://terrabrasilis.dpi.inpe.br/download/dataset/legal-amz-prodes/raster/prodes_amazonia_legal_2025_v20260408.zip

Reference year used for the Arc definition:
2024

## Construction procedure

The Arc was derived from 2024 deforestation concentrations among municipalities in the Brazilian Legal Amazon.

The following procedure was applied:

1. PRODES deforestation data for 2024 were intersected with the municipalities of the Brazilian Legal Amazon.
2. Municipal deforestation totals were calculated.
3. Municipalities were ordered according to their contribution to total deforestation.
4. Municipalities cumulatively representing approximately 75% of total 2024 deforestation were selected.
5. Selected municipalities that were spatially isolated from the remaining selected municipalities were excluded in order to retain a spatially continuous deforestation-frontier region.
6. The remaining municipalities were combined to generate the final Arc of Deforestation polygon used in the study.

## Selection statistics

Total deforestation in 2024:
626,154.54 ha

Municipalities initially selected:
82

Accumulated deforestation represented by these municipalities:
469,986.33 ha

Percentage of total 2024 deforestation represented:
75.0592%

The final Arc polygon excludes spatially isolated selected municipalities and retains the connected portion of this high-deforestation municipal set.

## Spatial reference

CRS:
SIRGAS 2000

EPSG:
4674

## File

`deforestation_arc_2024.shp`

## Use in the study

The Arc polygon was used to:

- define the main study region associated with the recent deforestation frontier;
- spatially aggregate annual climate-extreme indices;
- calculate cosine-latitude-weighted regional climate-index means;
- compare climate-extreme distributions between periods;
- perform change-point analyses.


