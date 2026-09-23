# Data and software provenance

## Workflow overview

```text
IBGE Legal Amazon 2024
          |
          +-------------------+
          |                   |
          v                   v
       BR-DWGD             MapBiomas 11
       /     \                 |
      /       \                v
     v         v          Land-cover analysis
   SPEI    Climate extremes
     |       /          \
     |      v            v
     |   Pettitt         KDE
     |      \            /
     |       \          /
     |        Arc of Deforestation
     |               ^
     |               |
     |          PRODES 2024
     |               +
     |       municipal boundaries
     |
   ERA5
    |
    v
 RiskClima
 commit b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc
  |
  v
daily_blocking_series.csv
  |
  +---------------+
                  |
                  v
       Hydroclimatic analysis
                  |
   +--------------+--------------+
   |              |              |
 trends      correlations    composites
```


## BR-DWGD

Version: 3.2.4
Period: 1961-2025
Variables:

- pr
- ETo

## SPEI

Calibration: 1981-2010

Scales: 1, 3, 6, 12 months


## Atmospheric blocking

Software: RiskClima

Repository:

```text
https://github.com/lammoc-uff/cnpq-riskclima
```

Commit:

```text
b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc
```

Period: 1961-2025

Climatology: 1981-2010

Municipal boundary source: TO BE DOCUMENTED

## Analysis software

Repository release:

```text
TO BE ADDED
```

Zenodo DOI:

```text
TO BE ADDED
```



