from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

FIELD_LABELS = {
    "type of request": "Type of Request",
    "lease category": "Lease Category",
    "company code": "Company Code",
    "vendor name": "Vendor Name",
    "monthly lease amount": "Monthly Lease Amount",
    "payment frequency": "Payment Frequency",
}

class LeaseFormAutomation:
    def __init__(self, settings):
        self.settings = settings
        self.driver = None

    def start(self):
        options = webdriver.ChromeOptions()
        if self.settings.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(self.settings.page_load_timeout)
        return self.driver

    def _wait(self):
        return WebDriverWait(self.driver, self.settings.wait_timeout)

    def _field(self, label):
        xpath = (
            f"//label[contains(normalize-space(.), '{label}')]/following::input[1] | "
            f"//label[contains(normalize-space(.), '{label}')]/following::select[1]"
        )
        found = self.driver.find_elements(By.XPATH, xpath)
        if found:
            return found[0]
        raise LookupError(
            f"Could not locate control for '{label}'. Add a matching label or data-testid."
        )

    def _set_value(self, label, value):
        element = self._field(label)
        self._wait().until(EC.visibility_of(element))
        if element.tag_name.lower() == "select":
            Select(element).select_by_visible_text(str(value))
        else:
            element.clear()
            element.send_keys(str(value))

    def run(self, record, excel_path):
        self.start()
        try:
            self.driver.get(self.settings.form_url)
            self._wait().until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            for key, label in FIELD_LABELS.items():
                self._set_value(label, record[key])
            upload = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            upload.send_keys(str(Path(excel_path).resolve()))
            submit = self._wait().until(EC.element_to_be_clickable((
                By.XPATH, "//form//button[@type='submit'] | //form//input[@type='submit']"
            )))
            # Submit once to avoid duplicate form submissions.
            submit.click()
            import time

            # Allow the React application to update
            time.sleep(3)

            # Capture browser state for debugging
            print("\n========== FORM DEBUG ==========")
            print("Current URL:", self.driver.current_url)
            print("Page title:", self.driver.title)

            page_text = self.driver.find_element(
                By.TAG_NAME, "body"
            ).text

            print("\nPAGE CONTENT:")
            print(page_text)

            # Save screenshot
            Path("screenshots").mkdir(exist_ok=True)

            self.driver.save_screenshot(
                "screenshots/form_after_submit.png"
            )

            print("\nScreenshot saved:")
            print("screenshots/form_after_submit.png")
            print("================================\n")
        finally:
            if self.driver:
                self.driver.quit()
