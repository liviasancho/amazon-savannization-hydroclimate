# Definition of the Arc of Deforestation

## Rationale

The Arc of Deforestation used in this study represents the recent spatial frontier of deforestation within the Brazilian Legal Amazon.

Rather than adopting a fixed historical Arc boundary, the study defined the region based on the spatial concentration of PRODES deforestation observed in 2024.

## Data sources

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
SIRGAS 2000 geographic coordinates, EPSG:4674.

Municipality identification field:
`Nome`

The Brazilian municipal layer was clipped to the Brazilian Legal Amazon boundary before the deforestation analysis.

### PRODES deforestation

Deforestation data were obtained from PRODES for the year 2024.

Provider:
Instituto Nacional de Pesquisas Espaciais (INPE) / TerraBrasilis / PRODES

Source:
https://terrabrasilis.dpi.inpe.br/download/dataset/legal-amz-prodes/raster/prodes_amazonia_legal_2025_v20260408.zip

## Construction of the Arc of Deforestation

The Arc of Deforestation was defined from the spatial concentration of mapped deforestation among municipalities of the Brazilian Legal Amazon.

Processing was performed in ArcGIS Pro 3.7.

First, the PRODES raster and the municipal layer clipped to the Brazilian Legal Amazon were used to calculate the deforested area within each municipality. Municipal deforestation totals were obtained using the `Zonal Statistics as Table` tool.

Municipalities were then ranked in descending order according to their 2024 deforested area. The cumulative percentage of total deforestation was calculated, and municipalities jointly accounting for approximately 75% of the total mapped deforestation were selected.

The initial selection resulted in:

- total 2024 deforestation: 626,154.54 ha;
- selected municipalities: 82;
- accumulated deforestation represented by the selected municipalities: 469,986.33 ha;
- percentage of total deforestation represented: 75.0592%.

## Spatial continuity criterion

The 82 selected municipalities did not form a single spatially continuous region.

To define a continuous deforestation frontier, the largest spatially connected component among the selected municipalities was identified. Only municipalities belonging to this largest continuous component were retained.

Municipalities or groups of municipalities spatially disconnected from the main component were excluded.

The final Arc of Deforestation therefore corresponds to the largest contiguous territorial set derived from the municipalities collectively representing approximately 75% of the 2024 deforestation.

## Output

The resulting polygon was stored in SIRGAS 2000 geographic coordinates (EPSG:4674) and used as the Arc of Deforestation mask throughout the climate-extreme analyses.
