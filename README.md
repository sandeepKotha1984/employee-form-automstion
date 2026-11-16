# Lease Information Form — Selenium Automation

Local Python/Selenium scaffold for the React form:
https://d2o76zyt1pudn4.cloudfront.net

## Workflow
- Reads one data row from the first worksheet of an `.xlsx` or `.xlsm` file.
- Maps six columns: Type of Request, Lease Category, Company Code, Vendor Name, Monthly Lease Amount, Payment Frequency.
- Opens Chrome, fills the form, attaches the same Excel file and clicks Submit.

**Important:** The current React frontend validates in the browser and displays a confirmation; it does not save the submission to a backend/API. A browser confirmation is not proof of persistence.

## Expected Excel columns
Use these headers in row 1:
`Type of Request`, `Lease Category`, `Company Code`, `Vendor Name`, `Monthly Lease Amount`, `Payment Frequency`.

The first data record is row 2. Dropdown values must match the form:
- Type of Request: `Contract`, `New Contract`, `Renewal Contract`
- Payment Frequency: `Monthly`, `Quarterly`, `Yearly`, `Bi-Annual`

## macOS setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Install Google Chrome. Selenium Manager (included with modern Selenium) manages ChromeDriver.

## Run
```bash
python main.py --excel "/absolute/path/to/lease-data.xlsx"
```
Use another worksheet row:
```bash
python main.py --excel "/absolute/path/to/lease-data.xlsx" --row 3
```
Set `HEADLESS=true` in `.env` to run without a visible browser.

## Structure
```text
lease-form-automation/
├── automation/lease_form.py
├── config/settings.py
├── utils/excel_reader.py
├── logs/
├── screenshots/
├── main.py
├── requirements.txt
└── .env.example
```

## Next AWS phase
We will containerize this worker, push it to ECR and run it as an ECS Fargate task. The eventual Lambda/Step Functions handoff will pass an S3 bucket/key; the worker will download the workbook before running Selenium.

Before production, add stable `data-testid` selectors to the React form, an explicit submit-result element, backend persistence, idempotency and failure screenshot capture.
