# SPEI methodology

## Input data

Precipitation and ETo are read from three consecutive NetCDF files for each variable, covering 1961–1980, 1981–2000, and 2001–2025. In the provided files, both variables have units of millimeters (mm) 
and a daily temporal resolution. Reading is performed using xarray with `decode_cf=True` and `mask_and_scale=True`, ensuring that `scale_factor`, `add_offset`, and `_FillValue` are interpreted according
to NetCDF CF metadata. 
• Precipitation: variable `pr`, in mm. 
• Reference evapotranspiration: variable `ETo`, in mm. 
• Total period: January 1, 1961, to December 31, 2025.
• Calibration period: January 1, 1981, to December 31, 2010.
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



## Spatial mask

## Outputs

## References
