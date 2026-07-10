import json
from datetime import datetime, timedelta, timezone

from reporting.result_writer import TestResultCollector, build_metadata, write_json
from reporting.run_context import RunContext


def make_context(tmp_path):
    started = datetime(2026, 7, 10, tzinfo=timezone.utc)
    return RunContext.create(tmp_path, {}, now=started, suffix="abc12345")


def test_collector_aggregates_phases_into_one_passed_test(tmp_path):
    context = make_context(tmp_path)
    collector = TestResultCollector(context)
    collector.record_phase(
        "tests/test_demo.py::test_ok", "test_ok", ["smoke"], "setup", "passed", 0.1
    )
    collector.record_phase(
        "tests/test_demo.py::test_ok", "test_ok", ["smoke"], "call", "passed", 0.2
    )
    collector.record_phase(
        "tests/test_demo.py::test_ok", "test_ok", ["smoke"], "teardown", "passed", 0.1
    )

    payload = collector.write_results(0, context.started_at + timedelta(seconds=1))

    assert payload["summary"] == {
        "total": 1,
        "passed": 1,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
    }
    assert payload["tests"][0]["duration_seconds"] == 0.4
    assert payload["tests"][0]["markers"] == ["smoke"]


def test_setup_failure_is_reported_as_error(tmp_path):
    context = make_context(tmp_path)
    collector = TestResultCollector(context)

    collector.record_phase(
        "tests/test_demo.py::test_bad",
        "test_bad",
        [],
        "setup",
        "failed",
        0.3,
        "driver failed",
    )
    payload = collector.write_results(1, context.started_at + timedelta(seconds=1))

    assert payload["tests"][0]["outcome"] == "error"
    assert payload["tests"][0]["failure_phase"] == "setup"
    assert payload["summary"]["errors"] == 1


def test_teardown_error_overrides_call_failure(tmp_path):
    context = make_context(tmp_path)
    collector = TestResultCollector(context)
    collector.record_phase(
        "tests/test_demo.py::test_bad",
        "test_bad",
        [],
        "call",
        "failed",
        0.2,
        "assertion",
    )
    collector.record_phase(
        "tests/test_demo.py::test_bad",
        "test_bad",
        [],
        "teardown",
        "failed",
        0.1,
        "quit failed",
    )

    payload = collector.write_results(1, context.started_at + timedelta(seconds=1))

    assert payload["tests"][0]["outcome"] == "error"
    assert payload["tests"][0]["failure_message"] == "quit failed"


def test_write_json_preserves_unicode(tmp_path):
    path = tmp_path / "result.json"

    write_json(path, {"message": "测试通过"})

    assert json.loads(path.read_text(encoding="utf-8"))["message"] == "测试通过"


def test_collector_is_not_treated_as_a_pytest_test_class():
    assert TestResultCollector.__test__ is False


def test_build_metadata_has_stable_environment_and_git_fields(tmp_path):
    context = make_context(tmp_path)

    metadata = build_metadata(
        context,
        {
            "base_url": "https://example.test/",
            "browser": "edge",
            "headless": True,
            "selenium_timeout": 10,
        },
        {"commit": None, "branch": None},
        {
            "python": "3.12.13",
            "platform": "Windows",
            "pytest": "9.0.2",
            "selenium": "4.41.0",
        },
    )

    assert metadata["schema_version"] == "1.0"
    assert metadata["run_id"] == context.run_id
    assert metadata["environment"]["browser"] == "edge"
    assert metadata["environment"]["python"] == "3.12.13"
    assert metadata["git"] == {"commit": None, "branch": None}
