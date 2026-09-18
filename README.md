# Amazon Savannization Hydroclimate

Reproducible Python workflows used to investigate hydroclimatic changes and atmospheric circulation associated with environmental change in the Brazilian Legal Amazon.

This repository contains the code used to:

- calculate the Standardized Precipitation-Evapotranspiration Index (SPEI) from BR-DWGD precipitation and reference evapotranspiration;
- Evaluate SPEI at 1-, 3-, 6-, and 12-month accumulation scales;
- Analyze temporal trends using the Mann-Kendall test;
- Analyze atmospheric blocking frequency and persistence;
- Investigate relationships between atmospheric blocking and hydroclimatic drought;
- Generate spatial correlation and composite maps used in the associated study.

## Reproducibility status

The SPEI calculation and hydroclimatic-analysis workflows are currently available.
Additional analysis components from manuscript coauthors will be incorporated before the archived v1.0.0 release.

## External software dependencies

Atmospheric blocking is generated externally using the RiskClima repository.
The exact commit used for the manuscript is recorded in `workflow/blocking/README.md`.
The blocking implementation is not duplicated here.

## Associated study

This repository supports the hydroclimatic component of a manuscript investigating environmental change and potential savannization processes in the Brazilian Amazon.

Manuscript citation: **to be added after publication**.

## Study domain

The analyses focus on the Brazilian Legal Amazon.

The hydroclimatic analysis covers 1961–2025, with 1981–2010 used as the climatological reference period for SPEI calibration and atmospheric-blocking anomalies.

## Repository structure

```text
scripts/
  spei/
      SPEI calculation workflow
  analysis/
      Hydroclimatic and atmospheric-blocking analyses

workflow/
  blocking/
      Documentation of the external RiskClima blocking workflow

docs/
      Data, methodology, provenance, and reproducibility documentation

data/
      Data-access instructions only; original datasets are not redistributed
```

## Hydroclimatic analyses

The analysis workflow includes:

- pixel-wise Mann-Kendall trends in SPEI;
- Mann-Kendall trends in annual atmospheric-blocking frequency;
- monthly blocking–SPEI associations;
- lagged blocking–SPEI correlations;
- spatial Pearson-correlation maps;
- high- versus low-blocking SPEI composites.

Detailed methodology is available in:
```text
docs/methodology_hydroclimate.md
```

## Installation

A Conda environment is recommended because the workflow depends on geospatial libraries such as Cartopy, GEOS, and PROJ.
```text
conda env create -f environment.yml
conda activate amazon-hydroclimate
```

Reproducing the analysis

See:
```text
docs/reproduction.md
```
for the complete workflow.

## Data availability

Original BR-DWGD and ERA5 datasets are not redistributed in this repository.

Users must obtain the original datasets from their respective providers.

Generated large NetCDF files are also excluded from Git version control.

## Citation

A software citation will be provided through `CITATION.cff` and a Zenodo DOI for the release associated with the manuscript.

License

This software is distributed under the Apache License 2.0.

## Contributions

Contributions associated with the manuscript are documented in `AUTHORS.md`.

See `CONTRIBUTING.md` for repository contribution guidelines.


