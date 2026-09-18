# Data and software provenance

## Workflow overview

```text
BR-DWGD precipitation
          +
BR-DWGD reference evapotranspiration
          |
          v
      SPEI workflow
          |
          +--> SPEI-1
          +--> SPEI-3
          +--> SPEI-6
          +--> SPEI-12
          |
          |
ERA5 ---> RiskClima atmospheric-blocking workflow
          |
          v
 daily_blocking_series.csv
          |
          +---------------------+
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
TO BE ADDED
```

Period: 1961-2025

Climatology: 1981-2010

## Analysis software

Repository release:

```text
TO BE ADDED
```

Zenodo DOI:

```text
TO BE ADDED
```



