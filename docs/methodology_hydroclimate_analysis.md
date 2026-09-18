# Hydroclimatic analysis

## SPEI trend analysis

Monthly SPEI is aggregated to annual values before trend testing.

The default metric is the annual mean SPEI.

The Mann-Kendall test is applied independently to each grid cell.

Only pixels with:

```text
p < 0.05
```
are displayed in the trend maps.

Kendall's tau is interpreted as:

```text
tau < 0: negative trend
tau > 0: positive trend
```


## Atmospheric-blocking trends

Daily blocking indicators are aggregated to annual blocked-day fractions:

$`
blocked\_fraction = blocked\_days / available\_days
`$

We apply the Mann-Kendall test independently to each blocking region.

## Monthly blocking frequency

We also aggregate daily blocking indicators monthly.

## Blocking-SPEI relationships

We evaluate relationships using Pearson and Spearman correlations.

Lags are evaluated as:

```text
lag 0: blocking(t) vs SPEI(t)
lag 1: blocking(t) vs SPEI(t+1)
lag 2: blocking(t) vs SPEI(t+2)
lag 3: blocking(t) vs SPEI(t+3)
```

## Spatial blocking-SPEI correlations

For each grid cell:

$`
r(x,y) = corr(blocking(t), SPEI(x,y,t+k))
`$

Retain only cells with at least 10 valid pairs and non-zero variance.

## Blocking composites

Monthly blocking frequency is separated into low- and high-blocking classes using:

```text
low blocking: <= 25th percentile
high blocking: >= 75th percentile
```

The composite difference is:

$`
\delta SPEI = \overline{SPEI}_{high} - \overline{SPEI}_{low}
`$


## Statistical interpretation

Correlation and composite analyses identify associations and must not be interpreted as causal attribution.

The classical Mann-Kendall test implemented here does not explicitly correct for serial autocorrelation.

