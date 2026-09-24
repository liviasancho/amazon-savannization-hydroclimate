# Data

## Download BR-DWGD

BR-DWGD files must currently be obtained from the official dataset page:

https://sites.google.com/site/alexandrecandidoxavierufes/brazilian-daily-weather-gridded-data

Download the six NetCDF files listed in `data/README.md`.

This repository does not include an automated download for BR-DWGD files because the official distribution URL may change, and the workflow relies only on provider-supported access methods.

# Analysis

## Reproducing the hydroclimatic analyses

### 1. Create the environment

```bash
conda env create -f environment.yml
conda activate amazon-hydroclimate
```

### 2. Obtain spatial boundaries


### 3. Obtain BR-DWGD data

Download the required precipitation and reference-evapotranspiration files listed in:

```bash
data/README.md
```

### 4. Calculate SPEI

Example:

```bash
python scripts/spei/run_spei_brdwgd.py \
    --precipitation-dir /path/to/pr \
    --eto-dir /path/to/eto \
    --shapefile /path/to/legal_amazon.shp \
    --output-dir /path/to/spei_results \
    --save-monthly-balance
```

### 5. Calculate climate-extreme indices and Pettitt change points

The workflow uses the three original BR-DWGD precipitation files and the three
original BR-DWGD daily maximum temperature files directly. No concatenated
intermediate input file is required.

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

The workflow produces annual gridded WSDI, SU35, TXx, CDD, R1mm and PRCPTOT
fields, Arc-averaged annual series, Pettitt change-point results and associated
figures.


### 6. Generate KDE comparison

```bash
python scripts/climate_extremes/plot_climate_extremes_kde.py \
    --indices-dir outputs/climate_extremes/indices \
    --arc-shapefile \
        data/derived/deforestation_arc/deforestation_arc_2024.shp \
    --output-dir \
        outputs/climate_extremes/kde
```


### 7. Generate atmospheric blocking with RiskClima

Follow the RiskClima blocking workflow documented in:

```bash
workflow/blocking/README.md
```

The downstream analysis requires:

```bash
daily_blocking_series.csv
```

### 8. Run blocking–SPEI analysis

```bash
python scripts/analysis/hydroclimate_blocking_spei_analysis.py \
    --blocking-csv /path/to/daily_blocking_series.csv \
    --spei1 /path/to/spei_1.nc \
    --spei3 /path/to/spei_3.nc \
    --spei6 /path/to/spei_6.nc \
    --spei12 /path/to/spei_12.nc \
    --amazon-shapefile /path/to/legal_amazon.shp \
    --output-dir /path/to/results \
    --spatial-blocking-regions \
        total north north_h1 north_h2 south south_h1 south_h2
```

### 9. Obtain/process MapBiomas


### 10. [later] Landsat LST workflow


### 11. Expected outputs

The workflow generates:

```bash
tables/
figures/
netcdf/
analysis_settings.json
```

The `analysis_settings.json` file records the principal statistical settings used in each execution.

