from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "database" / "market.db"

UPDATE_INTERVAL = 60

TGJU_SUBDOMAINS = [
    "call2",
    "call3",
    "call4"
]

REQUEST_TIMEOUT = 10

API_TITLE = "Gold Analyzer Pro"

API_VERSION = "1.0"

LOG_FILE = BASE_DIR / "logs" / "app.log"