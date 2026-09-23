# Climate-extreme indices and statistical analysis

## Input data

We obtained daily precipitation and daily maximum air temperature from BR-DWGD for 1961–2025.

Variables used:

- precipitation (`pr`);
- daily maximum air temperature (`Tmax`).

## Climate-extreme indices

Six annual climate-extreme indices were calculated:

- WSDI – Warm Spell Duration Index;
- SU35 – number of days with daily maximum temperature > 35 °C;
- TXx – annual maximum daily maximum temperature;
- CDD – maximum number of consecutive days with precipitation < 1 mm day−1;
- R1mm – annual number of days with precipitation ≥ 1 mm day−1;
- PRCPTOT – annual precipitation accumulated on days with precipitation ≥ 1 mm day−1.

We performed the calculations using `xclim`.

## WSDI reference climatology

WSDI uses the 1961–1990 reference period.

The calendar-day 90th percentile of daily maximum temperature is calculated using a centred 5-day window.

A warm spell is defined as at least six consecutive days exceeding the corresponding calendar-day 90th-percentile threshold.

## Precipitation units

BR-DWGD precipitation represents daily accumulated precipitation in millimetres.

Because each value corresponds to a regular one-day interval, the daily amounts are represented as `mm d−1` to match the precipitation thresholds required by the climate-index calculations. This operation changes the unit metadata but not the numerical values.

## Spatial aggregation

The annual gridded indices are spatially aggregated over the Arc of Deforestation.

The Arc polygon is applied using `regionmask`.

Because the BR-DWGD grid is a regular latitude–longitude grid, spatial means are weighted using the cosine of latitude:

`w = cos(latitude)`.

## Pettitt change-point analysis

We apply a Pettitt non-parametric change-point test independently to each annual regional climate-index series for 1961–2025.

The significance level is:

`alpha = 0.05`

The test identifies a single candidate change point from the maximum absolute cumulative rank statistic.

The reported breakpoint year corresponds to the final year of the pre-change segment. The post-change segment therefore begins in the following calendar year.

## Distributional analysis

Annual Arc-averaged values are separated into:

- 1985–2004;
- 2005–2025.

Gaussian kernel density estimates are calculated independently for each period.

The bandwidth is selected using Scott's rule.

The KDEs therefore represent distributions of annual regional means, rather than distributions of individual grid cells.
