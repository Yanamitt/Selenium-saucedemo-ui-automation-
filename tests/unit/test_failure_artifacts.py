from types import SimpleNamespace

from conftest import _append_failure_log, _attach_html_screenshot


def test_html_screenshot_is_embedded_as_a_data_uri(tmp_path):
    screenshot = tmp_path / "failure.png"
    screenshot.write_bytes(b"\x89PNG\r\n\x1a\nexample")
    report = SimpleNamespace(extras=[])

    _attach_html_screenshot(report, screenshot)

    content = report.extras[0]["content"]
    assert "data:image/png;base64," in content
    assert str(screenshot) not in content


def test_failure_log_timestamp_is_utc(tmp_path):
    failure_log = tmp_path / "failures.txt"
    report = SimpleNamespace(
        nodeid="tests/test_demo.py::test_failure",
        when="call",
        outcome="failed",
        longrepr="assertion failed",
    )

    _append_failure_log(report, None, None, failure_log)

    first_line = failure_log.read_text(encoding="utf-8").splitlines()[0]
    timestamp = first_line.split("]", 1)[0]
    assert timestamp.startswith("[")
    assert timestamp.endswith("Z")
