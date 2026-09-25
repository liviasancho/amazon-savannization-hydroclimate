# Arc of Deforestation

This directory contains the Arc of Deforestation polygon derived specifically for this study.

## Purpose

The polygon represents the recent deforestation frontier within the Brazilian Legal Amazon.

Rather than adopting a fixed historical Arc boundary, the study defined the Arc from the spatial concentration of PRODES deforestation observed in 2024.

## Source data

### Municipal boundaries

Municipal boundaries were obtained from the Brazilian Institute of Geography and Statistics (IBGE).

Product:
Municipal boundary mesh (`Malha Municipal`)

Year:
2025

Source:
https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/Brasil/BR_Municipios_2025.zip

Original file:
`BR_Municipios_2025`

Coordinate reference system:
SIRGAS 2000 geographic coordinates

EPSG:
4674

Municipality identification field:
`Nome`

The Brazilian municipal layer was clipped to the Brazilian Legal Amazon boundary before the deforestation analysis.

### PRODES deforestation

Deforestation data were obtained from PRODES for the year 2024.

Provider:
Instituto Nacional de Pesquisas Espaciais (INPE) / TerraBrasilis / PRODES

Source:
https://terrabrasilis.dpi.inpe.br/download/dataset/legal-amz-prodes/raster/prodes_amazonia_legal_2025_v20260408.zip

Reference year used for Arc definition:
2024

## Construction workflow

Processing was performed in ArcGIS Pro 3.7.

The Arc was derived according to the following procedure:

1. The PRODES 2024 raster and the municipal layer clipped to the Brazilian Legal Amazon were used as inputs.
2. Deforested area was calculated for each municipality using the ArcGIS Pro `Zonal Statistics as Table` tool.
3. Municipalities were ranked in descending order according to their total mapped deforestation in 2024.
4. The cumulative percentage of total deforestation was calculated.
5. Municipalities cumulatively accounting for approximately 75% of total 2024 deforestation were selected.
6. This initial selection resulted in 82 municipalities.
7. The 82 selected municipalities were evaluated for spatial connectivity.
8. The largest spatially connected component among the selected municipalities was retained.
9. Municipalities or groups of municipalities spatially disconnected from this main component were excluded.
10. The remaining connected municipalities were combined to generate the final Arc of Deforestation polygon used in the study.

## Selection statistics

Total deforestation mapped in 2024:

`626,154.54 ha`

Municipalities initially selected:

`82`

Accumulated deforestation represented by the initial 82 municipalities:

`469,986.33 ha`

Percentage of total 2024 deforestation represented by the initial selection:

`75.0592%`

The final Arc polygon corresponds to the largest spatially continuous component of this high-deforestation municipal set.

Because disconnected municipalities were excluded after the initial 75% selection, the final continuous polygon should not be interpreted as necessarily retaining exactly 75.0592% of total 2024 deforestation.

## Spatial reference

Coordinate reference system:

SIRGAS 2000 geographic coordinates

EPSG:

`4674`

## Files

The derived Arc shapefile is stored in this directory using the following files:

```text
deforestation_arc_2024.shp
deforestation_arc_2024.shx
deforestation_arc_2024.dbf
deforestation_arc_2024.prj
deforestation_arc_2024.cpg
```


## Use in the study

The Arc polygon was used to:

- define the principal study region associated with the recent deforestation frontier;
- spatially aggregate annual climate-extreme indices;
- calculate cosine-latitude-weighted regional climate-index means;
- compare climate-extreme distributions between 1985–2004 and 2005–2025;
- perform Pettitt change-point analyses on regional climate-index time series;
- provide spatial context for comparisons among land-use change, climate extremes, drought, and atmospheric-circulation changes.


## Detailed methodology

A full description of the Arc construction procedure is available in:

```text
docs/methodology_deforestation_arc.md
```


## Provenance

The municipal boundaries and PRODES raster are external datasets and are not redistributed in this repository.

The Arc polygon stored here is a derived product created for this study.

