from pathlib import Path
from openpyxl import load_workbook

FIELD_ALIASES = {
    "type of request": ["type of request", "request type"],
    "lease category": ["lease category", "category"],
    "company code": ["company code", "company"],
    "vendor name": ["vendor name", "vendor"],
    "monthly lease amount": ["monthly lease amount", "lease amount", "monthly amount"],
    "payment frequency": ["payment frequency", "frequency"],
}
REQUIRED_FIELDS = list(FIELD_ALIASES)

def _normalise(value):
    return " ".join(str(value or "").strip().lower().replace("_", " ").split())

def read_lease_record(file_path: str, row_number: int = 2) -> dict:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Excel file not found: {path}")
    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise ValueError("Only .xlsx and .xlsm files are supported.")
    workbook = load_workbook(path, data_only=True, read_only=True)
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        headers = next(rows, None)
        if not headers:
            raise ValueError("The worksheet is empty.")
        header_map = {}
        for index, header in enumerate(headers):
            key = _normalise(header)
            for canonical, aliases in FIELD_ALIASES.items():
                if key in aliases:
                    header_map[canonical] = index
                    break
        missing = [field for field in REQUIRED_FIELDS if field not in header_map]
        if missing:
            raise ValueError("Missing required Excel columns: " + ", ".join(missing))
        record = None
        for current_row, values in enumerate(rows, start=2):
            if current_row == row_number:
                record = {field: values[index] if index < len(values) else None
                          for field, index in header_map.items()}
                break
        if record is None:
            raise ValueError(f"Excel row {row_number} does not exist.")
        empty = [key for key, value in record.items()
                 if value is None or str(value).strip() == ""]
        if empty:
            raise ValueError("Empty values in Excel row: " + ", ".join(empty))
        record["company code"] = str(record["company code"]).strip()
        record["monthly lease amount"] = str(record["monthly lease amount"]).strip()
        for key in ("type of request", "lease category", "vendor name", "payment frequency"):
            record[key] = str(record[key]).strip()
        return record
    finally:
        workbook.close()
