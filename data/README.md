# Data access and provenance

This GitHub repository does not redistribute the original research datasets used in the study.

This directory documents the external datasets, versions, input files, derived spatial products, and intermediate data required to reproduce the analyses.

## Overview

The study uses the following principal data sources:

- BR-DWGD precipitation, daily maximum air temperature, and reference evapotranspiration;
- ERA5 reanalysis;
- IBGE 2024 Brazilian Legal Amazon boundary;
- IBGE 2025 municipal boundary mesh;
- PRODES 2024 deforestation data;
- MapBiomas Brazil Collection 11 land-use and land-cover rasters;
- a study-derived Arc of Deforestation polygon.

Additional Landsat land-surface-temperature data will be documented when the corresponding processing workflow is incorporated into the repository.

## 1. BR-DWGD

### Dataset

Brazilian Daily Weather Gridded Data (BR-DWGD)

Version used:

```text
v3.2.4
```

Provider information and download page:

```text
https://sites.google.com/site/alexandrecandidoxavierufes/brazilian-daily-weather-gridded-data
```

Official code repository:

```text
https://github.com/AlexandreCandidoXavier/BR-DWGD
```

Reference:

```text
Xavier, A. C., Scanlon, B. R., King, C. W., & Alves, A. I. (2022). New improved Brazilian daily weather gridded data (1961–2020). International Journal of Climatology, 42(16), 8390–8404. https://doi.org/10.1002/joc.7731
```

Temporal resolution:
```text
daily
```

Temporal coverage used:
```text
1961-01-01 to 2025-12-31
```

Variables used:
```text
pr   - precipitation
Tmax  - daily maximum air temperature
ETo  - reference evapotranspiration
```

Required precipitation files:
```text
pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
pr_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
```


Required daily maximum temperature files:
```text
Tmax_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
Tmax_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
Tmax_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
```


Required reference evapotranspiration files:
```text
ETo_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
ETo_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
ETo_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
```

### Use in the study

1. SPEI
   
Precipitation and reference evapotranspiration are used to calculate the climatic water balance:
$`
D = P - ETo
`$

SPEI is calculated at:
```text
1, 3, 6 and 12 months
```

Calibration period:
```text
1981-2010
```

Detailed methodology:
```text
docs/methodology_spei.md
```

2. Climate-extreme indices
   
Daily precipitation and daily maximum air temperature are used to calculate:
- WSDI;
- SU35;
- TXx;
- CDD;
- R1mm;
- PRCPTOT.
  
The climate-extreme workflow reads the three original BR-DWGD files for each variable directly and concatenates them internally.

Detailed methodology:
```text
docs/methodology_climate_extremes.md
```

Scripts:
```text
scripts/climate_extremes/calculate_climate_extremes_and_pettitt.py
scripts/climate_extremes/plot_climate_extremes_kde.py
```

The original BR-DWGD NetCDF files are not redistributed in this repository.


## 2. ERA5 reanalysis

ERA5 reanalysis is used as input to the atmospheric-blocking workflow.

Provider:
Copernicus Climate Change Service / ECMWF

Temporal coverage used:
```text
1961-01-01 to 2025-12-31
```

Reference climatology used in the blocking workflow:
```text
1981-2010
```

Atmospheric-blocking calculations are performed externally using the RiskClima workflow.

Repository:

https://github.com/lammoc-uff/cnpq-riskclima

Exact RiskClima revision used:
```text
b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc
```

Required downstream output:
```text
daily_blocking_series.csv
```

Detailed workflow documentation:
```text
workflow/blocking/README.md
```

The RiskClima blocking implementation is not duplicated in this repository.


## 3. Brazilian Legal Amazon boundary

The spatial domain of the Brazilian Legal Amazon is defined using the official 2024 Legal Amazon boundary distributed by the Brazilian Institute of Geography and Statistics (IBGE).

Dataset:

Legal Amazon boundary

Provider:

Instituto Brasileiro de Geografia e Estatística (IBGE)

Year:
```text
2024
```

File used:

Limites_Amazonia_Legal_2024.shp

Download:

https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/amazonia_legal/2024/Limites_Amazonia_Legal_2024_shp.zip

Original coordinate reference system:
```text
SIRGAS 2000
EPSG:4674
```

### Use in the study:
- spatial mask for the SPEI workflow;
- spatial domain for hydroclimatic analyses;
- clipping boundary for MapBiomas land-cover rasters;
- spatial domain for constructing the Arc of Deforestation;
- cartographic boundary in figures.
The original IBGE shapefile is not redistributed in this repository.


## 4. IBGE municipal boundaries

Municipal boundaries are used in the construction of the study-derived Arc of Deforestation.

Provider:

Instituto Brasileiro de Geografia e Estatística (IBGE)

Product:

Municipal boundary mesh (Malha Municipal)

Year:
```text
2025
```

Download:

https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/Brasil/BR_Municipios_2025.zip

Original file:
```text
BR_Municipios_2025
```

Coordinate reference system:
```text
SIRGAS 2000
EPSG:4674
```

Municipality identification field used:
```text
Nome
```

The national municipal layer was clipped to the Brazilian Legal Amazon before the deforestation analysis.

The original IBGE municipal boundary file is not redistributed in this repository.


## 5. PRODES deforestation

Deforestation data used to construct the Arc of Deforestation were obtained from PRODES.

Provider:

Instituto Nacional de Pesquisas Espaciais (INPE) / TerraBrasilis / PRODES

Reference deforestation year:
```text
2024
```

Source dataset:

https://terrabrasilis.dpi.inpe.br/download/dataset/legal-amz-prodes/raster/prodes_amazonia_legal_2025_v20260408.zip

Use in the study:
- calculation of 2024 deforested area by municipality;
- ranking municipalities by contribution to total deforestation;
- definition of the study-derived Arc of Deforestation.
  
The PRODES raster is not redistributed in this repository.

Detailed Arc-construction methodology:
```text
docs/methodology_deforestation_arc.md
```

## 6. Study-derived Arc of Deforestation

The Arc of Deforestation polygon used in this study is a derived spatial product generated from:
- PRODES 2024 deforestation;
- IBGE 2025 municipal boundaries;
- the IBGE Legal Amazon spatial domain.
  
The initial municipal selection contained 82 municipalities cumulatively representing:
```text
469,986.33 ha
```

of a total:
```text
626,154.54 ha
```

of mapped 2024 deforestation, corresponding to:
```text
75.0592%
```

The largest spatially connected component among these municipalities was retained to define the final continuous Arc polygon.

Derived files are stored in:
```text
data/derived/deforestation_arc/
```

Detailed documentation:
```text
data/derived/deforestation_arc/README.md
```

Scientific methodology:
```text
docs/methodology_deforestation_arc.md
```


## 7. MapBiomas land-use and land-cover data
   
Annual land-use and land-cover rasters were obtained from MapBiomas Brazil Collection 11.

Provider:

MapBiomas

Collection:
```text
Collection 11
```

Product:

Brazil annual land-use and land-cover coverage raster

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

Example for 2024:

https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection11/lulc/coverage/brazil_coverage/brazil_coverage-col11_2024.tif

Processing

The MapBiomas analysis was performed in:
```text
ArcGIS Pro 3.7
```

The rasters were clipped to the Brazilian Legal Amazon using Clip Raster.

No raster reprojection was performed.

The original WGS 84 geographic raster grid was preserved:
```text
EPSG:4326
```

Class areas were calculated using latitude-dependent geodesic pixel areas on the WGS 84 ellipsoid.

Detailed workflow:
```text
workflow/mapbiomas/README.md
```

Scientific methodology:
```text
docs/methodology_land_cover.md
```

The original MapBiomas rasters are not redistributed in this repository.


## 8. Landsat land-surface temperature

The manuscript also includes a land-surface-temperature analysis based on Landsat data.

The complete Landsat/LST data provenance and processing workflow will be documented after the corresponding analysis metadata are incorporated into the repository.

This section will be completed before the archived software release associated with the manuscript.


## Data redistribution policy

Original third-party datasets are not stored in this repository unless their redistribution terms explicitly allow it and redistribution is necessary for reproducibility.

The repository primarily stores:
- source code;
- workflow documentation;
- derived study-specific spatial products;
- metadata;
- provenance information.
  
Users should obtain original datasets directly from the corresponding data providers using the links documented above.




