# Amazon Savannization Hydroclimate

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23511898.svg)](https://doi.org/10.5281/zenodo.23511898)


Reproducible workflows, methodological documentation, and derived spatial data supporting analyses of environmental change across the Brazilian Legal Amazon.

The repository accompanies a scientific study integrating land-use change, climate extremes, drought, atmospheric blocking, and land-surface temperature.

## Repository scope

The repository documents workflows used to:

- calculate the Standardized Precipitation-Evapotranspiration Index (SPEI) from BR-DWGD precipitation and reference evapotranspiration;
- evaluate SPEI at 1-, 3-, 6-, and 12-month accumulation scales;
- calculate annual climate-extreme indices from BR-DWGD precipitation and daily maximum air temperature;
- detect climate-extreme change points using the Pettitt test;
- compare climate-extreme distributions using Gaussian kernel density estimation;
- derive and document the Arc of Deforestation used in the study;
- quantify land-use and land-cover changes from MapBiomas Brazil Collection 11;
- analyse atmospheric-blocking trends and blocking–SPEI relationships;
- document Landsat-based land-surface-temperature analyses;
- reproduce the principal statistical and spatial analyses associated with the manuscript.

## Associated study

This repository supports a manuscript investigating compound climate and land-use pressures across the Brazilian Amazon.

The final manuscript citation will be added after publication.

## Study periods

Different workflows use periods appropriate to their respective datasets:

- BR-DWGD climate analyses: 1961–2025;
- SPEI calibration period: 1981–2010;
- atmospheric-blocking analysis: 1961–2025;
- MapBiomas reference years: 1985, 1995, 2005, 2015, and 2024;
- Landsat LST representative scenes: 2013, 2020, and 2026.

## Repository structure

```text
scripts/
  spei/
      SPEI calculation workflow

  climate_extremes/
      Climate-extreme indices, Pettitt test, and KDE workflow

  analysis/
      Hydroclimatic and atmospheric-blocking analyses

workflow/
  blocking/
      Documentation of the external RiskClima blocking workflow

  mapbiomas/
      ArcGIS Pro workflow for MapBiomas land-cover analysis

  landsat_lst/
      QGIS workflow for Landsat land-surface temperature

docs/
      Methodology, provenance, data-availability, and reproduction documentation

data/
  README.md
      External data sources and provenance
  derived/
      Study-derived spatial products
```

## Main analytical components

### SPEI

SPEI is calculated from BR-DWGD precipitation and reference evapotranspiration at 1-, 3-, 6-, and 12-month timescales.

Detailed methodology:

```text
docs/methodology_spei.md
```

### Climate extremes

The repository calculates:
- WSDI;
- SU35;
- TXx;
- CDD;
- R1mm;
- PRCPTOT.
The workflow also performs Pettitt change-point analysis and KDE comparison between 1985–2004 and 2005–2025.

Detailed methodology:

```text
docs/methodology_climate_extremes.md
```

### Arc of Deforestation

The study-specific Arc of Deforestation was derived from 2024 PRODES deforestation and 2025 IBGE municipal boundaries.

Detailed methodology:

```text
docs/methodology_deforestation_arc.md
```
Derived spatial data:

```text
data/derived/deforestation_arc/
```


### Land-use and land-cover

MapBiomas Brazil Collection 11 was used to quantify land-cover changes for 1985, 1995, 2005, 2015, and 2024.

Detailed methodology:

```text
docs/methodology_land_cover.md
```

Workflow documentation:

```text
workflow/mapbiomas/README.md
```

### Atmospheric blocking and hydroclimate

Atmospheric blocking was generated externally using RiskClima.

The exact RiskClima commit used in the study is recorded in:

```text
workflow/blocking/README.md
```

The downstream analysis includes:
- pixel-wise Mann-Kendall trends in SPEI;
- Mann-Kendall trends in annual atmospheric-blocking frequency;
- monthly blocking–SPEI associations;
- lagged blocking–SPEI correlations;
- spatial Pearson-correlation maps;
- high- versus low-blocking SPEI composites.

Detailed methodology:

```text
docs/methodology_hydroclimate_analysis.md
```

### Landsat land-surface temperature

Representative Landsat 8 Collection 2 Level-2 Surface Temperature scenes were analysed for 2013, 2020, and 2026.

The scenes do not necessarily share an identical spatial footprint and are interpreted as representative critical thermal conditions rather than as a pixel-by-pixel temporal series.

Detailed methodology:

```text
docs/methodology_lst.md
```

Workflow documentation:

```text
workflow/landsat_lst/README.md
```

Known catalogue-availability limitations are documented in:

```text
docs/data_availability_notes.md
```

## Installation

A Conda environment is recommended because the workflows depend on geospatial and scientific libraries.

```text
conda env create -f environment.yml
conda activate amazon-savannization
```

## Reproducing the analyses

See:

```text
docs/reproduction.md
```

for the complete workflow.

## Data availability

Original third-party datasets are not redistributed in this repository.

Data sources, versions, filenames, access locations, and provenance are documented in:

```text
data/README.md
```

Large generated NetCDF files and intermediate outputs are excluded from Git version control.

## Citation

Software citation metadata are provided in:

```text
CITATION.cff
```

## License

This software is distributed under the Apache License 2.0.

## Authors and contributions

Scientific, software, data-processing, visualization, and manuscript contributions are documented in:

```text
AUTHORS.md
```

## Archived release

Version `v1.0.0` is permanently archived on Zenodo:

`https://doi.org/10.5281/zenodo.23511898`
