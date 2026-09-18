# SPEI methodology

The Standardized Precipitation-Evapotranspiration Index (SPEI) was calculated over the Brazilian Legal Amazon using precipitation (pr) and reference evapotranspiration (ETo) from the Brazilian Daily Weather Gridded Data (BR-DWGD), version 3.2.4. Daily fields covering 1961–2025 were used, and 1981–2010 was adopted as the reference period for distribution fitting. The BR-DWGD dataset methodology is described by [Xavier et al. (2022)](https://rmets.onlinelibrary.wiley.com/doi/abs/10.1002/joc.7731).

The adopted formulation follows the SPEI structure proposed by [Vicente-Serrano et al. (2010)](https://journals.ametsoc.org/view/journals/clim/23/7/2009jcli2909.1.xml): climatic water balance, accumulation at different time scales, probabilistic fitting, and transformation to a standard normal distribution. The choice of unbiased PWMs for distribution fitting follows the subsequent recommendation by [Beguería et al. (2014)](https://doi.org/10.1002/joc.3887). [Greenwood et al. (1979)](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/WR015i005p01049) and [Hosking (1990)](https://academic.oup.com/jrsssb/article/52/1/105/7027905) provide the theoretical basis for probability-weighted moments and L-moments.

## Input data

Precipitation and ETo are read from three consecutive NetCDF files for each variable, covering 1961–1980, 1981–2000, and 2001–2025. In the provided files, both variables have units of millimeters (mm) 
and a daily temporal resolution. Reading is performed using xarray with `decode_cf=True` and `mask_and_scale=True`, ensuring that `scale_factor`, `add_offset`, and `_FillValue` are interpreted according
to NetCDF CF metadata. 

- Precipitation: variable `pr`, in mm. 
- Reference evapotranspiration: variable `ETo`, in mm. 
- Total period: January 1, 1961, to December 31, 2025.
- Calibration period: January 1, 1981, to December 31, 2010.

Before calculation, the pipeline verifies file existence, the presence of expected variables, units, duplicate timestamps, daily continuity, and alignment of time, latitude, and longitude coordinates between `pr` and `ETo`. Any inconsistency halts processing to prevent the silent generation of incorrect results.

## Climatic water balance and Temporal aggregation

Because the SPEI is calculated monthly, daily precipitation and ETo data are summed monthly. Prior validation of daily data continuity allows a strict monthly sum, with the result 
recorded as missing if any daily value within the month is missing.

$`
P_{m} = \sum{P_{d}}
`$

$`
ETo_{m} = \sum{ETo_{d}}
`$

The monthly climatic water balance is then defined as:

$`
D_{m} = P_{m} − ETo_{m}
`$

Positive D values indicate a relative surplus of precipitation compared to reference evaporative demand; negative values ​​indicate a relative deficit.

## SPEI accumulation scales

The SPEI is multi-scalar. For each scale k, the monthly water balance is accumulated using a non-shifted rectangular moving sum:

$`
D_{k,t} = \sum_{i=0}^{k−1} D_{t-1}
`$

The pipeline calculates values ​​for k = 1, 3, 6, and 12 months. Consequently, the first k−1 months of each series remain undefined, as a complete accumulation window is not available.

## Calibration period

1981-2010

## Probability distribution

For each timescale, we fit the distribution independently for each grid point and calendar month. Thus, January values ​​are fitted against the Januarys of the calibration period, February values ​​against the Februarys, and so on. Based on the 1981–2010 period, each monthly fit comprises 30 values ​​when the series is complete.
The three-parameter log-logistic distribution is used with the Generalized Logistic (GLO) parameterization, following the formulation employed in the SPEI methodology. We estimate parameters using unbiased probability-weighted moments (ub-PWM), as recommended by [Beguería et al. (2014)](https://doi.org/10.1002/joc.3887).

## Unbiased probability-weighted moments and L-moments

For each monthly calibration sample, the unbiased probability-weighted moments $`\beta_{0}`$, $`\beta_{1}`$, and $`\beta_{2}`$ are calculated. The pipeline converts these values ​​into the first three L-moments:

$`
\lambda_{1} = \beta_{o}
`$

$`
\lambda_{2} = 2\beta_{1} − \beta_{o}
`$

$`
\lambda_{3} = 6\beta_{2} − 6\beta_{1} + \beta_{o}
`$

$`
\tau_{3} = \lambda_{3} / \lambda_{2}
`$

In the GLO parameterization implemented in the pipeline, the shape parameter is $`κ = −\tau_{3}`$. The parameters $`\epsilon`$ (location), $`\alpha`$ (scale), and $`k`$ (shape) are derived from $`\lambda_{1}`$, $`\lambda_{2}`$, and $`k`$. Fits with invalid parameters $`(\lambda_{2} \le 0, |k| \ge 1)`$ or missing values ​​during the calibration period are recorded as NaN.

## Standard-normal transformation

After the adjustment, each accumulated water balance value is converted into a cumulative probability using the GLO CDF. This probability is transformed by the quantile function of the standard normal distribution:

$`
SPEI = \phi^{-1}[F(D)]
`$

The final interpretation is the standard one for a standardized variable: negative values ​​represent conditions drier than the reference climate, and positive values ​​represent wetter conditions. Probabilities are limited only by float64 machine precision to avoid ±∞ values ​​during the normal transformation.

## Outputs

The pipeline produces four independent NetCDF files: SPEI-1, SPEI-3, SPEI-6, and SPEI-12. Each file contains the index time series and the parameters $`\epsilon`$, $`\alpha`$, and $`k`$ fitted for the 12 calendar months and for each grid point. Optionally, the pipeline also saves the monthly climatic water balance P−ETo.
The final files are written in float32 format, using zlib level 4 compression when the netCDF4 backend is available, and include metadata recording the period, scale, calibration, distribution, fitting method, and shapefile used.
