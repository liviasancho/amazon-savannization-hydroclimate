# Amazon Savannization Hydroclimate

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
