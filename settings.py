import os


DEFAULT_BASE_URL = "https://www.saucedemo.com/"
SUPPORTED_BROWSERS = {"chrome", "edge", "firefox"}


def get_base_url():
    base_url = os.getenv("BASE_URL", DEFAULT_BASE_URL).strip()
    return base_url.rstrip("/") + "/"


def get_browser_name():
    browser = os.getenv("BROWSER", "edge").strip().lower()
    if browser not in SUPPORTED_BROWSERS:
        supported = ", ".join(sorted(SUPPORTED_BROWSERS))
        raise ValueError(f"BROWSER must be one of: {supported}")
    return browser


def is_headless():
    return os.getenv("HEADLESS", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def get_timeout():
    value = os.getenv("SELENIUM_TIMEOUT", os.getenv("TIMEOUT", "10")).strip()
    try:
        timeout = int(value)
    except ValueError as exc:
        raise ValueError("SELENIUM_TIMEOUT must be a positive integer") from exc

    if timeout <= 0:
        raise ValueError("SELENIUM_TIMEOUT must be a positive integer")
    return timeout
