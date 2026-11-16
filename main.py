import argparse
import logging
from pathlib import Path
from config.settings import Settings
from utils.excel_reader import read_lease_record
from automation.lease_form import LeaseFormAutomation

def configure_logging(log_dir):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(Path(log_dir) / "automation.log", encoding="utf-8")],
    )

def main():
    parser = argparse.ArgumentParser(description="Populate the deployed Lease Information form from Excel.")
    parser.add_argument("--excel", required=True, help="Path to .xlsx or .xlsm file")
    parser.add_argument("--row", type=int, default=2, help="Excel row number (default: 2)")
    args = parser.parse_args()
    settings = Settings()
    configure_logging(settings.log_dir)
    logger = logging.getLogger("lease_form_automation")
    try:
        record = read_lease_record(args.excel, args.row)
        logger.info("Excel record loaded: row=%s", args.row)
        LeaseFormAutomation(settings).run(record, args.excel)
        logger.info("Browser flow completed; inspect the form result and logs.")
    except Exception:
        logger.exception("Browser automation failed")
        Path(settings.screenshot_dir).mkdir(parents=True, exist_ok=True)
        raise

if __name__ == "__main__":
    main()
