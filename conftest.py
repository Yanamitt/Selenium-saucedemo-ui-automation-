import base64
import os
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
import selenium
from selenium import webdriver

from reporting.result_writer import TestResultCollector, build_metadata, write_json
from reporting.run_context import RunContext, format_utc
from settings import get_base_url, get_browser_name, get_timeout, is_headless


try:
    from pytest_html import extras as pytest_html_extras
except ImportError:
    pytest_html_extras = None


def _build_options(browser_name, headless):
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-features=PasswordLeakDetection")
        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.password_manager_leak_detection": False,
            },
        )
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


def _append_failure_log(report, screenshot_path, driver, failure_log):
    timestamp = format_utc(datetime.now(timezone.utc))
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

    with failure_log.open("a", encoding="utf-8") as failure_file:
        failure_file.write("\n".join(lines))
        failure_file.write("\n\n")


def _attach_html_screenshot(report, screenshot_path):
    if pytest_html_extras is None or not screenshot_path:
        return

    encoded_image = base64.b64encode(Path(screenshot_path).read_bytes()).decode("ascii")
    html = (
        '<div><img src="data:image/png;base64,{0}" alt="screenshot" '
        'style="width:304px;height:228px;" '
        'onclick="window.open(this.src)" align="right"/></div>'
    ).format(encoded_image)
    extras = getattr(report, "extras", [])
    extras.append(pytest_html_extras.html(html))
    report.extras = extras


def _git_value(project_root, *args):
    try:
        completed = subprocess.run(
            ["git", "-c", f"safe.directory={project_root.as_posix()}", *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None

    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _metadata_environment():
    configuration_errors = []
    try:
        browser = get_browser_name()
    except ValueError as exc:
        browser = os.getenv("BROWSER", "edge").strip().lower()
        configuration_errors.append(str(exc))

    try:
        selenium_timeout = get_timeout()
    except ValueError as exc:
        selenium_timeout = None
        configuration_errors.append(str(exc))

    return {
        "base_url": get_base_url(),
        "browser": browser,
        "headless": is_headless(),
        "selenium_timeout": selenium_timeout,
        "configuration_errors": configuration_errors,
    }


def pytest_configure(config):
    context = RunContext.create(Path(str(config.rootpath)))
    collector = TestResultCollector(context)
    config._test_run_context = context
    config._test_result_collector = collector

    metadata = build_metadata(
        context,
        _metadata_environment(),
        {
            "commit": _git_value(context.project_root, "rev-parse", "HEAD"),
            "branch": _git_value(context.project_root, "branch", "--show-current"),
        },
        {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pytest": pytest.__version__,
            "selenium": selenium.__version__,
        },
    )
    write_json(context.metadata_path, metadata)


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
    context = item.config._test_run_context
    collector = item.config._test_result_collector
    web_driver = item.funcargs.get("driver") if "driver" in item.funcargs else None
    screenshot_reference = None

    if report.failed:
        if web_driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            screenshot_name = f"{_safe_file_name(item.name)}_{timestamp}.png"
            screenshot_path = context.screenshots_dir / screenshot_name
            try:
                web_driver.save_screenshot(str(screenshot_path))
                _attach_html_screenshot(report, str(screenshot_path))
                screenshot_reference = screenshot_path.relative_to(
                    context.run_dir
                ).as_posix()
            except Exception as exc:
                screenshot_reference = f"<capture failed: {exc}>"

        _append_failure_log(
            report,
            screenshot_reference,
            web_driver,
            context.failure_log,
        )

    collector.record_phase(
        nodeid=report.nodeid,
        name=item.name,
        markers=[marker.name for marker in item.iter_markers()],
        phase=report.when,
        outcome=report.outcome,
        duration=getattr(report, "duration", 0.0),
        failure_message=str(report.longrepr) if report.failed else None,
        screenshot=screenshot_reference,
    )


def pytest_sessionfinish(session, exitstatus):
    session.config._test_result_collector.write_results(exitstatus)
