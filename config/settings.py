import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    form_url: str = os.getenv("FORM_URL", "https://d2o76zyt1pudn4.cloudfront.net")
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"
    page_load_timeout: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    wait_timeout: int = int(os.getenv("WAIT_TIMEOUT", "20"))
    screenshot_dir: str = os.getenv("SCREENSHOT_DIR", "screenshots")
    log_dir: str = os.getenv("LOG_DIR", "logs")
