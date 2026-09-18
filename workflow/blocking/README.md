# Atmospheric blocking index workflow

Atmospheric blocking index used in this study was generated using the external RiskClima implementation.

## Source repository

RiskClima:

https://github.com/lammoc-uff/cnpq-riskclima

Component:

```text
index-blocking/era5
```

## Study configuration

Dataset:

```text
ERA5
```

Analysis period:

```text
1961-2025
```

Reference climatology:

```text
1981-2010
```

Blocking output used by the analyses in this repository:

```text
daily_blocking_series.csv
```

Blocking regions:

```text
total
north
north_h1
north_h2
south
south_h1
south_h2
```

## Reproducibility

The blocking implementation is intentionally not copied into this repository.

The version used in the manuscript must be identified by the exact RiskClima Git commit:

```text
RiskClima commit: b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc
```
The user should obtain the exact commit from the RiskClima checkout used to generate the blocking data.

### Provenance

The resulting `daily_blocking_series.csv` is used as an external intermediate product by:

```text
scripts/analysis/hydroclimate_blocking_spei_analysis.py
```
This repository therefore depends on the RiskClima blocking workflow for atmospheric-circulation diagnostics but does not maintain a duplicate implementation.


