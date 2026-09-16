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
Pₘ = \sum{P_{d}}
`$
$`
EToₘ = \sum{ETo_{d}}
`$
The monthly climatic water balance is then defined as:
$`
Dₘ = P_{m} − ETo_{m}
`$
Positive D values indicate a relative surplus of precipitation compared to reference evaporative demand; negative values ​​indicate a relative deficit.

## SPEI accumulation scales

The SPEI is multi-scalar. For each scale k, the monthly water balance is accumulated using a non-shifted rectangular moving sum:
$`
Dₜ^(k) = Σᵢ₌₀^(k−1) Dₜ₋ᵢ
`$
The pipeline calculates values ​​for k = 1, 3, 6, and 12 months. Consequently, the first k−1 months of each series remain undefined, as a complete accumulation window is not available.

## Calibration period

## Probability distribution

## Unbiased probability-weighted moments

## L-moments

## Standard-normal transformation

## Spatial mask

## Outputs

## References
