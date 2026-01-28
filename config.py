"""
Configuration management for URL scraper project.
Loads settings from config/email_config.json (and optionally .env if you extend it).
"""
import json
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"
EMAIL_CONFIG_FILE = CONFIG_DIR / "email_config.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Data files
JOINCLASSACTIONS_URLS_FILE = DATA_DIR / "joinclassactions_urls.json"
RANKITEO_URLS_FILE = DATA_DIR / "rankiteo_urls.json"

# Scraping configuration
SOURCES = {
    "classactions_sitemap": "https://joinclassactions.com/class_actions-sitemap1.xml",
    "rankiteo_blog": "https://blog.rankiteo.com",
}

# Request configuration
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries


def load_email_config() -> dict:
    if not EMAIL_CONFIG_FILE.exists():
        raise ValueError(f"Missing email config file: {EMAIL_CONFIG_FILE}")

    try:
        with open(EMAIL_CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {EMAIL_CONFIG_FILE}: {e}")

    if not isinstance(cfg, dict):
        raise ValueError(f"Email config must be a JSON object in {EMAIL_CONFIG_FILE}")

    return cfg


# Email configuration (loaded once at import time)
_email_cfg = load_email_config()

SMTP_SERVER = _email_cfg.get("smtp_server", "smtp.gmail.com")
SMTP_PORT = int(_email_cfg.get("smtp_port", 587))
USE_SSL = bool(_email_cfg.get("use_ssl", False))

SMTP_USERNAME = _email_cfg.get("sender_email")
SMTP_PASSWORD = _email_cfg.get("sender_password")

EMAIL_FROM = SMTP_USERNAME
EMAIL_TO = _email_cfg.get("receiver_emails", [])


def validate_config() -> bool:
    errors = []

    if not SMTP_USERNAME:
        errors.append("sender_email is missing in config/email_config.json")
    if not SMTP_PASSWORD:
        errors.append("sender_password is missing in config/email_config.json")
    if not EMAIL_TO or not isinstance(EMAIL_TO, list):
        errors.append("receiver_emails must be a non-empty list in config/email_config.json")

    if errors:
        raise ValueError(
            "Configuration errors:\n" +
            "\n".join(f"  - {e}" for e in errors)
        )

    return True
