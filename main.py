import argparse
import logging
import os
from pathlib import Path

import boto3

from config.settings import Settings
from utils.excel_reader import read_lease_record
from automation.lease_form import LeaseFormAutomation


def configure_logging(log_dir):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(Path(log_dir) / "automation.log", encoding="utf-8"),
        ],
    )


def download_excel_from_s3(bucket: str, key: str) -> Path:
    filename = Path(key).name or "lease-input.xlsx"
    local_path = Path("/tmp") / filename
    logging.getLogger("lease_form_automation").info(
        "Downloading Excel input from s3://%s/%s", bucket, key
    )
    boto3.client("s3").download_file(bucket, key, str(local_path))
    return local_path


def main():
    parser = argparse.ArgumentParser(
        description="Populate the deployed Lease Information form from an Excel file."
    )
    parser.add_argument(
        "--excel",
        help="Local path to .xlsx or .xlsm file (for local runs)",
    )
    parser.add_argument("--s3-bucket", help="S3 bucket containing the validated Excel file")
    parser.add_argument("--s3-key", help="S3 object key for the validated Excel file")
    parser.add_argument(
        "--row",
        type=int,
        default=2,
        help="Excel row number (default: 2; row 1 contains headers)",
    )
    args = parser.parse_args()

    if bool(args.excel) == bool(args.s3_bucket and args.s3_key):
        parser.error("Provide either --excel OR both --s3-bucket and --s3-key.")

    settings = Settings()
    configure_logging(settings.log_dir)
    logger = logging.getLogger("lease_form_automation")

    try:
        excel_path = (
            Path(args.excel)
            if args.excel
            else download_excel_from_s3(args.s3_bucket, args.s3_key)
        )
        record = read_lease_record(str(excel_path), args.row)
        logger.info("Excel record loaded: row=%s", args.row)
        LeaseFormAutomation(settings).run(record, str(excel_path))
        logger.info("Browser flow completed; inspect the form result and logs.")
    except Exception:
        logger.exception("Browser automation failed")
        Path(settings.screenshot_dir).mkdir(parents=True, exist_ok=True)
        raise


if __name__ == "__main__":
    main()
