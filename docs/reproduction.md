# Reproducing the analyses

## 1. Create the software environment

From the repository root:

```bash
conda env create -f environment.yml
conda activate amazon-savannization
```

## 2. Obtain the required datasets

Data providers, versions, filenames, and access locations are documented in:

```text
data/README.md
```

Original third-party datasets are not redistributed in this repository.

## 3. Obtain the Brazilian Legal Amazon boundary

Download the 2024 IBGE Legal Amazon boundary described in:

```text
data/README.md
```

This boundary is used by the SPEI, MapBiomas, hydroclimatic, and cartographic workflows.

## 4. Calculate SPEI

Download the three BR-DWGD precipitation files and three BR-DWGD reference-evapotranspiration files listed in:

```text
data/README.md
```

Run:

```bash
python scripts/spei/run_spei_brdwgd.py \
    --precipitation-dir /path/to/pr_directory \
    --eto-dir /path/to/eto_directory \
    --shapefile /path/to/Limites_Amazonia_Legal_2024.shp \
    --output-dir /path/to/spei_results \
    --save-monthly-balance
```

The default scales are: 1, 3, 6 and 12

The workflow generates one NetCDF file for each SPEI scale and optionally the monthly climatic water balance.

## 5. Calculate climate-extreme indices and Pettitt change points

The climate-extreme workflow reads the three original BR-DWGD precipitation files and the three original BR-DWGD Tmax files directly.

```bash
python scripts/climate_extremes/calculate_climate_extremes_and_pettitt.py \
    --precipitation-files \
        /path/to/pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc \
        /path/to/pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc \
        /path/to/pr_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc \
    --tasmax-files \
        /path/to/Tmax_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc \
        /path/to/Tmax_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc \
        /path/to/Tmax_20010101_20251231_BR-DWGD_UFES_UTEXAS_v_3.2.4.nc \
    --arc-shapefile \
        data/derived/deforestation_arc/deforestation_arc_2024.shp \
    --output-dir \
        outputs/climate_extremes
```

The workflow generates:

```text
outputs/climate_extremes/
├── indices/
│   ├── WSDI_annual.nc
│   ├── SU35_annual.nc
│   ├── TXx_annual.nc
│   ├── CDD_annual.nc
│   ├── R1mm_annual.nc
│   ├── PRCPTOT_annual.nc
│   └── pettitt_breakpoints_arc_deforestation.xlsx
└── figures/
```

## 6. Generate climate-extreme KDE comparisons

```bash
python scripts/climate_extremes/plot_climate_extremes_kde.py \
    --indices-dir outputs/climate_extremes/indices \
    --arc-shapefile \
        data/derived/deforestation_arc/deforestation_arc_2024.shp \
    --output-dir \
        outputs/climate_extremes/kde
```

## 7. Generate atmospheric blocking data

Atmospheric blocking is generated externally using RiskClima.

Follow:

```text
workflow/blocking/README.md
```

The downstream hydroclimatic analysis requires:

```text
daily_blocking_series.csv
```

## 8. Run the blocking–SPEI analysis

```bash
python scripts/analysis/hydroclimate_blocking_spei_analysis.py \
    --blocking-csv /path/to/daily_blocking_series.csv \
    --spei1 /path/to/spei_1_BR-DWGD_AmazoniaLegal_1961_2025.nc \
    --spei3 /path/to/spei_3_BR-DWGD_AmazoniaLegal_1961_2025.nc \
    --spei6 /path/to/spei_6_BR-DWGD_AmazoniaLegal_1961_2025.nc \
    --spei12 /path/to/spei_12_BR-DWGD_AmazoniaLegal_1961_2025.nc \
    --amazon-shapefile /path/to/Limites_Amazonia_Legal_2024.shp \
    --output-dir /path/to/hydroclimate_results \
    --spatial-blocking-regions \
        total north north_h1 north_h2 south south_h1 south_h2
```

Default statistical settings are documented in:

```text
docs/methodology_hydroclimate_analysis.md
```

The analysis generates tables, figures, NetCDF outputs, and:

```text
analysis_settings.json
```

which records the principal settings used in each execution.

## 9. Reproduce the MapBiomas analysis

The MapBiomas analysis was performed interactively in ArcGIS Pro 3.7 rather than through a Python script.

Follow the documented procedure in:

```text
workflow/mapbiomas/README.md
```

Scientific methodology is documented in:

```text
docs/methodology_land_cover.md
```

## 10. Reproduce the Landsat LST processing

The LST workflow was performed in QGIS 3.34.

Follow:

```text
workflow/landsat_lst/README.md
```

Scientific methodology:

```text
docs/methodology_lst.md
```

Known USGS catalogue-availability limitations are documented in:

```text
docs/data_availability_notes.md
```

Because the exact originally downloaded 2013 and 2026 products could not be re-verified in the current USGS catalogue during repository preparation, exact reproduction of those two original downloads may depend on future clarification from USGS.

## 11. Derived Arc of Deforestation

The derived spatial product used in the climate-extreme analysis is already included in:

```text
data/derived/deforestation_arc/
```

Its construction is documented in:

```text
docs/methodology_deforestation_arc.md
```
and:

```text
data/derived/deforestation_arc/README.md
```
