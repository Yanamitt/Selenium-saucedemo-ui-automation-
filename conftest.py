import re
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver

from settings import get_browser_name, is_headless


try:
    import pytest_html
except ImportError:
    pytest_html = None


SCREENSHOT_DIR = Path("screenshots")
FAILURE_LOG = Path("failures.txt")


def _build_options(browser_name, headless):
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
    elif browser_name == "firefox":
        options = webdriver.FirefoxOptions()
    else:
        options = webdriver.EdgeOptions()

    if browser_name == "firefox":
        if headless:
            options.add_argument("--headless")
    else:
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        else:
            options.add_argument("--start-maximized")

    return options


def _create_driver(browser_name, options):
    if browser_name == "chrome":
        return webdriver.Chrome(options=options)
    if browser_name == "firefox":
        return webdriver.Firefox(options=options)
    return webdriver.Edge(options=options)


def _safe_file_name(value):
    return re.sub(r'[<>:"/\\|?*\[\]\s]+', "_", value).strip("_")


def _driver_value(driver, attribute):
    try:
        return getattr(driver, attribute)
    except Exception as exc:
        return f"<unavailable: {exc}>"


def _browser_logs(driver):
    try:
        logs = driver.get_log("browser")
    except Exception:
        return []
    return [f"{entry.get('level', 'INFO')}: {entry.get('message', '')}" for entry in logs[-20:]]


def _append_failure_log(report, screenshot_path, driver):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    browser_logs = _browser_logs(driver) if driver else []
    lines = [
        f"[{timestamp}] {report.nodeid}",
        f"phase: {report.when}",
        f"outcome: {report.outcome}",
        f"current_url: {_driver_value(driver, 'current_url') if driver else '<no driver>'}",
        f"screenshot: {screenshot_path or '<not captured>'}",
        "error:",
        str(report.longrepr),
    ]

    if browser_logs:
        lines.append("browser_logs:")
        lines.extend(browser_logs)

    with FAILURE_LOG.open("a", encoding="utf-8") as failure_file:
        failure_file.write("\n".join(lines))
        failure_file.write("\n\n")


def _attach_html_screenshot(report, screenshot_path):
    if pytest_html is None or not screenshot_path:
        return

    html = (
        '<div><img src="{0}" alt="screenshot" '
        'style="width:304px;height:228px;" '
        'onclick="window.open(this.src)" align="right"/></div>'
    ).format(screenshot_path)
    extras = getattr(report, "extras", [])
    extras.append(pytest_html.extras.html(html))
    report.extras = extras


@pytest.fixture(scope="function")
def driver():
    browser_name = get_browser_name()
    options = _build_options(browser_name, is_headless())
    web_driver = _create_driver(browser_name, options)
    if browser_name == "firefox" and not is_headless():
        web_driver.maximize_window()

    yield web_driver
    web_driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.failed:
        web_driver = item.funcargs.get("driver") if "driver" in item.funcargs else None
        screenshot_path = None

        if web_driver:
            SCREENSHOT_DIR.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{_safe_file_name(item.name)}_{timestamp}.png"
            screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
            try:
                web_driver.save_screenshot(screenshot_path)
                _attach_html_screenshot(report, screenshot_path)
            except Exception as exc:
                screenshot_path = f"<capture failed: {exc}>"

        _append_failure_log(report, screenshot_path, web_driver)
