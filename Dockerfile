
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    CHROME_BIN=/usr/bin/chromium

WORKDIR /app

# Install Chromium and ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Make Chromium discoverable by Selenium
RUN ln -sf /usr/bin/chromium /usr/bin/google-chrome

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Selenium automation entry point
ENTRYPOINT ["python", "main.py"]
