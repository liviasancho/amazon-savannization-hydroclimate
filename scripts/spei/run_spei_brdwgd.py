#!/usr/bin/env python3
"""Compute SPEI-1, SPEI-3, SPEI-6 and SPEI-12 from BR-DWGD."""

from __future__ import annotations

import argparse
from pathlib import Path

from pipeline import build_spei_dataset, prepare_monthly_balance, write_netcdf
from spei_statistics import calculate_spei


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--precipitation-dir", type=Path, required=True)
    parser.add_argument("--eto-dir", type=Path, required=True)
    parser.add_argument("--shapefile", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--scales", type=int, nargs="+", default=[1, 3, 6, 12], choices=range(1, 49)
    )
    parser.add_argument("--save-monthly-balance", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    balance, mask, _geometry, bounds, source_crs = prepare_monthly_balance(
        args.precipitation_dir,
        args.eto_dir,
        args.shapefile,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.save_monthly_balance:
        balance.where(mask).to_dataset().to_netcdf(
            args.output_dir / "brdwgd_monthly_climatic_water_balance_1961_2025.nc"
        )

    for scale in args.scales:
        print(f"Calculating SPEI-{scale}...")
        spei, params = calculate_spei(
            balance,
            scale=scale,
            calibration_start="1981-01-01",
            calibration_end="2010-12-31",
        )
        ds = build_spei_dataset(
            spei,
            params,
            mask,
            scale=scale,
            shapefile=args.shapefile,
            bounds=bounds,
            source_crs=source_crs,
        )
        output = args.output_dir / f"spei_{scale}_BR-DWGD_AmazoniaLegal_1961_2025.nc"
        write_netcdf(ds, output)
        print(f"Written: {output}")


if __name__ == "__main__":
    main()

