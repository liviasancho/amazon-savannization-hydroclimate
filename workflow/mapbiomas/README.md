# MapBiomas land-use and land-cover workflow

This directory documents the workflow used to quantify land-use and land-cover changes in the Brazilian Legal Amazon from MapBiomas Brazil Collection 11.

The analysis was performed in ArcGIS Pro 3.7.

## Input data

### MapBiomas

Provider:
MapBiomas

Collection:
Collection 11

Product:
Annual land-use and land-cover coverage raster for Brazil

Reference years used:

- 1985
- 1995
- 2005
- 2015
- 2024

Annual raster URL pattern:

```text
https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection11/lulc/coverage/brazil_coverage/brazil_coverage-col11_<YEAR>.tif
```

### Example for 2024:

https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection11/lulc/coverage/brazil_coverage/brazil_coverage-col11_2024.tif


## Brazilian Legal Amazon boundary

Provider:
Instituto Brasileiro de Geografia e Estatística (IBGE)

Year:
2024

Source:

```text
https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/amazonia_legal/2024/Limites_Amazonia_Legal_2024_shp.zip
```

The IBGE Legal Amazon polygon was used as the clipping boundary for all MapBiomas rasters.

Software
ArcGIS Pro 3.7

Processing workflow

The same procedure was applied independently to each reference year.

1. Download annual raster

Download the MapBiomas Collection 11 raster corresponding to the reference year.

For example:

```text
brazil_coverage-col11_2024.tif
```

2. Load the raster in ArcGIS Pro

Open the annual MapBiomas raster in ArcGIS Pro 3.7 together with the 2024 IBGE Legal Amazon boundary.

4. Clip to the Brazilian Legal Amazon

Use the ArcGIS Pro Clip Raster tool to restrict the MapBiomas raster to the Brazilian Legal Amazon.

The raster remains in its original geographic coordinate reference system:

```text
WGS 84
EPSG:4326
```

No raster reprojection is performed.

4. Preserve the original categorical grid
   
Raster reprojection was intentionally avoided because categorical rasters require resampling.

Even when nearest-neighbour resampling is used, reprojection changes the raster grid and may duplicate or remove cells, which can affect area estimates, especially for spatially small classes such as Urban Area and Mining.

The analysis therefore preserves the original MapBiomas grid and calculates pixel area directly on the geographic grid.

6. Identify land-cover classes
   
Each raster pixel is assigned to the MapBiomas class represented by its Value code.

Pixels with value 0 (NoData) are excluded.

The analysed classes are:

| Code | Class |
|---:|---|
| 3 | Forest Formation |
| 4 | Savanna Formation |
| 6 | Floodable Forest |
| 11 | Wetland |
| 15 | Pasture |
| 20 | Sugar Cane |
| 24 | Urban Area |
| 30 | Mining |
| 35 | Palm Oil |
| 39 | Soybean |
| 40 | Rice |
| 41 | Other Temporary Crops |

The raster attribute-table Count field provides the number of pixels assigned to each class.

6. Calculate pixel area by raster row
   
Because the raster is stored in geographic coordinates, pixel area varies with latitude.

A single constant pixel area is therefore not used.

Instead, the geodesic area of a raster cell is calculated separately for each raster row using the WGS 84 ellipsoid.

For each row and land-cover class:

```text
class area in the row =
number of class pixels in the row
×
geodesic area of one raster cell at that latitude
```

7. Sum class area across the Legal Amazon
   
For each land-cover class, the row-specific areas are summed across the complete Brazilian Legal Amazon domain.

Final class areas are converted from square metres to square kilometres.

9. Validate total mapped area
    
The resulting total mapped area is approximately:

```text
5.01 million km²
```

which is consistent with the geographic extent of the Brazilian Legal Amazon.

9. Compare reference years
    
For each reference year, class areas are stored in km².

These values are used to calculate:
- absolute land-cover changes between years;
- relative percentage changes;
- changes in the proportional contribution of each class to the total mapped area.

## Output

The workflow generates the class-area values used in the manuscript tables and land-cover figures.

Each reported area corresponds to the geodesically calculated area occupied by a single MapBiomas class within the Brazilian Legal Amazon for the corresponding year.

## Reproducibility note

The MapBiomas analysis was performed interactively in ArcGIS Pro rather than through a Python script.

This README therefore documents the exact processing sequence used in the study.

The original MapBiomas rasters are not redistributed in this repository.


## Related documentation

Scientific methodology:

```text
docs/methodology_land_cover.md
```

Data sources:

```text
data/README.md
```

Workflow provenance:

```text
docs/provenance.md
```

