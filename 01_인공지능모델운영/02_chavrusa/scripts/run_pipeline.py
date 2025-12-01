"""CLI helper to download data, load sqlite, and build analytics artifacts."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from chavrusa import data_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AdventureWorks analytics pipeline")
    parser.add_argument("--force-download", action="store_true", help="Re-download source csv files")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading raw csv files")
    parser.add_argument("--skip-sqlite", action="store_true", help="Skip writing to sqlite")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    if not args.skip_download:
        data_pipeline.download_raw_tables(force=args.force_download)
    if not args.skip_sqlite:
        data_pipeline.load_into_sqlite()
    enriched = data_pipeline.build_enriched_sales()
    outputs = data_pipeline.export_curated_datasets(enriched)
    logging.info("Generated artifacts: %s", outputs)


if __name__ == "__main__":
    main()

