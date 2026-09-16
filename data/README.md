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

Temporal coverage used:
```text
1961-01-01 to 2025-12-31
```

Climatology used:
```text
1981-2010
```

Temporal resolution:
```text
daily
```

Dataset information and download page:
```text
https://sites.google.com/site/alexandrecandidoxavierufes/brazilian-daily-weather-gridded-data

Official code repository:

https://github.com/AlexandreCandidoXavier/BR-DWGD

Reference:

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

Climatology used:
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

## Legal Amazon boundary

The study uses a Legal Amazon polygon as its spatial mask and cartographic boundary.

The exact source, version, and access information for this shapefile will be recorded here before the final software release.


