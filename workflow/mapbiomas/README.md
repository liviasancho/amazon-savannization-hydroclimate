1. Download annual Collection 11 raster
2. Open the raster in ArcGIS Pro 3.7
3. Clip the raster using the Legal Amazon polygon
4. Exclude NoData/value 0
5. Use the raster Value field as the class identifier
6. Count class pixels by raster row
7. Calculate row-specific geodesic pixel area in WGS 84
8. Multiply row pixel count by row pixel area
9. Sum across rows
10. Convert to km²
