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

### 2. Obtain BR-DWGD data

Download the required precipitation and reference-evapotranspiration files listed in:

```bash
data/README.md
```

### 3. Calculate SPEI

Example:

```bash
python scripts/spei/run_spei_brdwgd.py \
    --precipitation-dir /path/to/pr \
    --eto-dir /path/to/eto \
    --shapefile /path/to/legal_amazon.shp \
    --output-dir /path/to/spei_results \
    --save-monthly-balance
```

### 4. Generate atmospheric-blocking data

Follow the RiskClima blocking workflow documented in:

```bash
workflow/blocking/README.md
```

The downstream analysis requires:

```bash
daily_blocking_series.csv
```

### 5. Run hydroclimatic analyses

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

### 6. Expected outputs

The workflow generates:

```bash
tables/
figures/
netcdf/
analysis_settings.json
```

The `analysis_settings.json` file records the principal statistical settings used in each execution.

