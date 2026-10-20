# Data and software provenance

## Workflow overview

```text
IBGE Legal Amazon 2024
          |
          +----------------------+----------------------+
          |                     |                       |
          v                     v                       v
       BR-DWGD             MapBiomas 11        IBGE municipalities 2025
       /     \                  |                      |
      /       \                 v                      |
     v         v         Land-cover analysis          |
   SPEI    Climate extremes                            |
     |       /          \                              |
     |      v            v                             |
     |   Pettitt         KDE                           |
     |                                                 |
     |                                PRODES 2024 -----+
     |                                      |
     |                                      v
     |                            Arc of Deforestation
     |                                      |
     +----------------------+---------------+
                            |
 ERA5                       |
  |                         |
  v                         |
RiskClima                   |
commit                      |
b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc
  |
  v
daily_blocking_series.csv
  |
  +-------------------------+
                            |
                            v
                 Hydroclimatic analysis
                            |
               +------------+------------+
               |            |            |
               v            v            v
             trends    correlations   composites


USGS Landsat 8 Collection 2 Level-2
                 |
                 v
          QGIS LST workflow
                 |
                 v
       Representative LST maps
```

## BR-DWGD

Version: 3.2.4
Period: 1961-2025
Variables:

- pr
- Tmax
- ETo

BR-DWGD supports both the SPEI and climate-extreme workflows.

## SPEI

Calibration period: 1981-2010

Accumulation scales: 1, 3, 6, 12 months

Implementation:

```text
scripts/spei/
```

## Climate extremes

Input variables:
- pr;
- Tmax.
  
Indices:
- WSDI;
- SU35;
- TXx;
- CDD;
- R1mm;
- PRCPTOT.
  
Implementation:

```text
scripts/climate_extremes/
Brazilian Legal Amazon
```

Provider: IBGE

Boundary year: 2024

CRS:SIRGAS 2000 / EPSG:4674

## Municipal boundaries

Provider: IBGE

Product: BR_Municipios_2025

Year: 2025
 
CRS: SIRGAS 2000 / EPSG:4674

Use: construction of the study-derived Arc of Deforestation.

## PRODES

Provider: INPE / TerraBrasilis / PRODES

Deforestation reference year: 2024

Use: municipality-level deforestation quantification and construction of the Arc of Deforestation.

## Arc of Deforestation

The derived Arc is stored in:

```text
data/derived/deforestation_arc/
```

Detailed methodology:

```text
docs/methodology_deforestation_arc.md
```

## MapBiomas

Collection: MapBiomas Brazil Collection 11

Reference years:
- 1985;
- 1995;
- 2005;
- 2015;
- 2024.

Processing software: ArcGIS Pro 3.7

Detailed workflow:

```text
workflow/mapbiomas/README.md
```

## Atmospheric blocking

Software: RiskClima

Repository:

```text
[https://github.com/lammoc-uff/cnpq-riskclima](https://github.com/lammoc-uff/cnpq-riskclima)
```

Exact commit:

```text
b1a6948d73b0cc2f6a13e4ecd5bc09f5be54b7dc
```

Analysis period: 1961-2025

Reference climatology: 1981-2010

Intermediate product used downstream:

```text
daily_blocking_series.csv
```

## Landsat land-surface temperature

Provider: USGS

Product: Landsat 8 Collection 2 Level-2 Surface Temperature Science Product

Years represented:
- 2013;
- 2020;
- 2026.

Processing software: QGIS 3.34

Detailed workflow:
 
 ```text
workflow/landsat_lst/README.md
```

Known catalogue-availability limitations:

```text
docs/data_availability_notes.md
```

## Repository release

Repository: 

```text
[https://github.com/liviasancho/amazon-savannization-hydroclimate](https://github.com/liviasancho/amazon-savannization-hydroclimate)
```

Release: v1.0.0

Zenodo DOI:

```text
TO BE ADDED
```

Subsequent releases may receive new version-specific DOIs while retaining the same conceptual software record.



