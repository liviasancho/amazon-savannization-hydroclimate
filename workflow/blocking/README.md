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

The atmospheric-blocking implementation is intentionally not duplicated in this repository.

The blocking data used in the manuscript were generated with the following exact RiskClima revision:

```text
b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc
```

Permanent source reference:

[https://github.com/lammoc-uff/cnpq-riskclima/tree/b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc/index-blocking/era5](https://github.com/lammoc-uff/cnpq-riskclima/tree/b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc/index-blocking/era5)

The resulting:

```text
daily_blocking_series.csv
```

is used as an external intermediate product by:

```text
scripts/analysis/hydroclimate_blocking_spei_analysis.py
```

This repository therefore depends on the RiskClima blocking workflow for atmospheric-circulation diagnostics without maintaining a duplicate implementation.

### Provenance

The resulting `daily_blocking_series.csv` is used as an external intermediate product by:

```text
scripts/analysis/hydroclimate_blocking_spei_analysis.py
```
This repository therefore depends on the RiskClima blocking workflow for atmospheric-circulation diagnostics but does not maintain a duplicate implementation.


