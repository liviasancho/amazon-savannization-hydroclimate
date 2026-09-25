# Land-use and land-cover analysis

## Data source

We obtained annual land-use and land-cover rasters from MapBiomas Brazil Collection 11.

Reference years used in the study:

- 1985
- 1995
- 2005
- 2015
- 2024

The annual rasters follow the URL pattern:

`https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection11/lulc/coverage/brazil_coverage/brazil_coverage-col11_<YEAR>.tif`

Example for 2024:

https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection11/lulc/coverage/brazil_coverage/brazil_coverage-col11_2024.tif

## Software

Land-cover processing was performed in ArcGIS Pro 3.7.

## Spatial clipping

Each annual MapBiomas raster was clipped to the Brazilian Legal Amazon using the ArcGIS Pro `Clip Raster` tool.

No raster reprojection was performed.

The original MapBiomas geographic grid was retained in WGS 84 geographic coordinates (EPSG:4326).

Avoiding reprojection prevented the resampling of categorical land-cover data and therefore preserved the original class membership of each raster cell.

## Land-cover classes

Each raster pixel was assigned to the class indicated by its MapBiomas `Value` code, following the official MapBiomas legend.

We excluded pixels with value 0 (`NoData`).

The analysed classes were:

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

## Area calculation

Because the raster is stored in geographic coordinates, the physical area represented by a pixel varies with latitude.

Therefore, we did not calculate class area by multiplying total pixel count by a single constant pixel area.

Instead, we calculated the geodesic area of each raster cell separately for each raster row using the WGS 84 ellipsoid.

For each land-cover class and raster row, class area was calculated as:

`number of pixels of the class in the row × geodesic pixel area at that latitude`

We then summed the row-specific areas across the Brazilian Legal Amazon.

We converted final class areas to square kilometres.

The resulting total mapped area was approximately 5.01 million km², consistent with the extent of the Brazilian Legal Amazon.

## Temporal comparison

For each selected reference year, we calculated the total area occupied by each class in km².

We then used these values to calculate absolute and relative changes in land-cover composition between years.

