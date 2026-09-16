# Amazon Savannization Hydroclimate

Reproducible Python workflows used to investigate hydroclimatic changes and atmospheric circulation associated with environmental change in the Brazilian Legal Amazon.

This repository contains the code used to:

- calculate the Standardized Precipitation-Evapotranspiration Index (SPEI) from BR-DWGD precipitation and reference evapotranspiration;
- Evaluate SPEI at 1-, 3-, 6-, and 12-month accumulation scales;
- Analyze temporal trends using the Mann-Kendall test;
- Analyze atmospheric blocking frequency and persistence;
- Investigate relationships between atmospheric blocking and hydroclimatic drought;
- Generate spatial correlation and composite maps used in the associated study.

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
