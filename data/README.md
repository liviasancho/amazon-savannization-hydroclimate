# Data access

This GitHub repository does not store raw research datasets.

This directory documents the datasets required to reproduce the analyses.

## Standardized Precipitation-Evapotranspiration Index (SPEI)

Dataset:

Brazilian Daily Weather Gridded Data (BR-DWGD)

Version used:

```text
v3.2.4
```

Variables used:
```text
pr   - precipitation
ETo  - reference evapotranspiration
```

Temporal resolution:
```text
daily
```

Temporal coverage used:
```text
1961-01-01 to 2025-12-31
```

### SPEI methodology

The climatic water balance is calculated as:
```text
D = P - ETo
```

where `P` is monthly precipitation and `ETo` is monthly reference evapotranspiration.

SPEI is calculated at 1-, 3-, 6-, and 12-month accumulation scales using:

- calibration period: 1981–2010;
- three-parameter log-logistic distribution;
- generalized logistic parameterization;
- unbiased probability-weighted moments (ub-PWM).

Detailed methodology is available in:
```text
docs/methodology_spei.md
```

Dataset information and download page:
```text
https://sites.google.com/site/alexandrecandidoxavierufes/brazilian-daily-weather-gridded-data
```

Official code repository:

```text
https://github.com/AlexandreCandidoXavier/BR-DWGD
```

Reference:

```text
Xavier, A. C., Scanlon, B. R., King, C. W., & Alves, A. I. (2022).
New improved Brazilian daily weather gridded data (1961–2020).
International Journal of Climatology, 42(16), 8390–8404.
https://doi.org/10.1002/joc.7731
```

### Required BR-DWGD files
Precipitation
```text
pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
pr_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
```
Reference evapotranspiration
```text
ETo_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
ETo_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
ETo_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc
```


## Atmospheric Blocking Index (ABI)

We generated atmospheric-blocking outputs independently using the RiskClima ERA5 workflow.

Repository:

https://github.com/lammoc-uff/cnpq-riskclima

Data source used:
```text
ERA5
```

Temporal coverage used:
```text
1961-01-01 to 2025-12-31
```

Calibration period:
```text
1981-2010
```

Required output for the downstream analysis:
```text
daily_blocking_series.csv
```

The exact RiskClima revision used to generate this file is documented in:
```text
workflow/blocking/README.md
```


## Brazilian Legal Amazon boundary

The spatial domain of the Brazilian Legal Amazon was defined using the official 2024 Legal Amazon boundary distributed by the Brazilian Institute of Geography and Statistics (IBGE).

Dataset:
Legal Amazon boundary

Provider:
Instituto Brasileiro de Geografia e Estatística (IBGE)

Year:
2024

File used:
`Limites_Amazonia_Legal_2024.shp`

Download:
https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/amazonia_legal/2024/Limites_Amazonia_Legal_2024_shp.zip

Original CRS:
SIRGAS 2000 (EPSG:4674)

Used in this study:
- spatial mask for the SPEI workflow;
- spatial domain for hydroclimatic analyses;
- cartographic boundary in figures.

The original IBGE shapefile is not redistributed in this repository.


## MapBiomas land-use and land-cover data

We obtained annual land-use and land-cover data from MapBiomas Brazil Collection 11.

Provider:
MapBiomas

Collection:
Collection 11

Spatial product:
Brazil annual land-use and land-cover coverage raster

Reference years used in the study:
- 1985
- 1995
- 2005
- 2015
- 2024

The annual raster files follow the URL pattern:

`https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection11/lulc/coverage/brazil_coverage/brazil_coverage-col11_<YEAR>.tif`

For example, the 2024 raster is available at:

https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection11/lulc/coverage/brazil_coverage/brazil_coverage-col11_2024.tif

The original MapBiomas raster files are not redistributed in this repository.


