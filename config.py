import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# API KEYS - Add your keys in .env file
# ============================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")

# ============================================
# LLM Settings
# ============================================
LLM_MODEL_OPENAI = "gpt-5.2"

# ============================================
# Scraper Settings
# ============================================
HEADLESS_MODE = True       # True = browser runs in background
WAIT_TIME = 10             # Seconds to wait for page load
MAX_RETRIES = 3            # Retry attempts if scraping fails
DELAY_BETWEEN_REQUESTS = 3 # Seconds between requests

# ============================================
# Chrome Settings
# ============================================
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-gpu",
    "--window-size=1920,1080",
]

# ============================================
# Indian Airports Code Reference
# ============================================
AIRPORT_CODES = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "chennai": "MAA",
    "kolkata": "CCU",
    "hyderabad": "HYD",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "goa": "GOI",
    "kochi": "COK",
    "lucknow": "LKO",
    "chandigarh": "IXC",
    "nagpur": "NAG",
    "indore": "IDR",
    "bhopal": "BHO",
    "patna": "PAT",
    "varanasi": "VNS",
    "amritsar": "ATQ",
    "srinagar": "SXR",
    "leh": "IXL",
    "guwahati": "GAU",
    "bhubaneswar": "BBI",
    "visakhapatnam": "VTZ",
    "coimbatore": "CJB",
    "madurai": "IXM",
    "tiruchirappalli": "TRZ",
    "mangalore": "IXE",
    "ranchi": "IXR",
    "raipur": "RPR",
}