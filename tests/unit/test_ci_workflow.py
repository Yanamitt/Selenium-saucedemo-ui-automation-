from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ui-tests.yml"
WORKFLOW_TEXT = WORKFLOW_PATH.read_text(encoding="utf-8")
WORKFLOW = yaml.safe_load(WORKFLOW_TEXT)
JOBS = WORKFLOW["jobs"]
CHECKOUT_ACTION = "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5"
SETUP_PYTHON_ACTION = "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"
UPLOAD_ARTIFACT_ACTION = (
    "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
)


def find_step(job, *, name=None, uses=None):
    for step in job["steps"]:
        if name is not None and step.get("name") == name:
            return step
        if uses is not None and step.get("uses") == uses:
            return step
    raise AssertionError(f"Step not found: name={name!r}, uses={uses!r}")


def test_ci_triggers_pr_main_schedule_and_manual_runs_only():
    triggers = WORKFLOW["on"]

    assert triggers["push"] == {"branches": ["main"]}
    assert triggers["pull_request"] is None
    assert triggers["schedule"] == [{"cron": "0 18 * * 0-4"}]
    assert triggers["workflow_dispatch"] is None


def test_ci_has_actionlint_and_fast_unit_quality_gate():
    lint_job = JOBS["workflow-lint"]
    unit_job = JOBS["unit-tests"]

    assert lint_job["runs-on"] == "ubuntu-latest"
    assert lint_job["timeout-minutes"] == 5
    find_step(lint_job, uses="docker://rhysd/actionlint:1.7.7")

    assert unit_job["runs-on"] == "ubuntu-latest"
    assert unit_job["timeout-minutes"] == 10
    find_step(unit_job, uses=SETUP_PYTHON_ACTION)
    assert find_step(unit_job, name="Run unit tests")["run"] == (
        "python scripts/run_tests.py tests/unit -q"
    )


def test_pull_requests_run_cross_browser_smoke_matrix():
    smoke_job = JOBS["ui-smoke"]

    assert smoke_job["if"] == "github.event_name == 'pull_request'"
    assert smoke_job["runs-on"] == "windows-latest"
    assert smoke_job["timeout-minutes"] == 15
    assert smoke_job["strategy"] == {
        "fail-fast": False,
        "matrix": {"browser": ["edge", "chrome", "firefox"]},
    }
    assert smoke_job["env"] == {
        "BROWSER": "${{ matrix.browser }}",
        "HEADLESS": "true",
        "SELENIUM_TIMEOUT": "15",
    }
    assert find_step(smoke_job, name="Run smoke tests")["run"] == (
        "python scripts/run_tests.py -m smoke -q"
    )


def test_main_schedule_and_manual_runs_use_full_regression_matrix():
    regression_job = JOBS["ui-regression"]

    assert regression_job["if"] == (
        "github.event_name == 'schedule' || "
        "github.event_name == 'workflow_dispatch' || "
        "(github.event_name == 'push' && github.ref == 'refs/heads/main')"
    )
    assert regression_job["runs-on"] == "windows-latest"
    assert regression_job["timeout-minutes"] == 30
    assert regression_job["strategy"] == {
        "fail-fast": False,
        "matrix": {"browser": ["edge", "chrome", "firefox"]},
    }
    assert find_step(regression_job, name="Run regression tests")["run"] == (
        "python scripts/run_tests.py -m regression -q"
    )


def test_test_jobs_always_upload_unique_artifacts_for_fourteen_days():
    expected_names = {
        "workflow-lint": "lint-${{ github.run_id }}-${{ github.run_attempt }}",
        "unit-tests": "unit-${{ github.run_id }}-${{ github.run_attempt }}",
        "ui-smoke": (
            "smoke-${{ matrix.browser }}-${{ github.run_id }}-"
            "${{ github.run_attempt }}"
        ),
        "ui-regression": (
            "regression-${{ matrix.browser }}-${{ github.run_id }}-"
            "${{ github.run_attempt }}"
        ),
    }

    for job_name, artifact_name in expected_names.items():
        step = find_step(JOBS[job_name], uses=UPLOAD_ARTIFACT_ACTION)
        assert step["if"] == "always()"
        assert step["with"] == {
            "name": artifact_name,
            "path": "artifacts/",
            "if-no-files-found": "warn",
            "retention-days": 14,
        }


def test_official_actions_are_pinned_to_immutable_commits():
    expected = {CHECKOUT_ACTION, SETUP_PYTHON_ACTION, UPLOAD_ARTIFACT_ACTION}
    actual = {
        step["uses"]
        for job in JOBS.values()
        for step in job["steps"]
        if step.get("uses", "").startswith("actions/")
    }

    assert actual == expected


def test_ci_uses_minimum_permissions_and_never_hides_failures():
    assert WORKFLOW["permissions"] == {"contents": "read"}
    assert WORKFLOW["concurrency"] == {
        "group": "quality-gates-${{ github.workflow }}-${{ github.ref }}",
        "cancel-in-progress": True,
    }

    for job in JOBS.values():
        assert "continue-on-error" not in job
        for step in job["steps"]:
            assert "continue-on-error" not in step

    normalized = WORKFLOW_TEXT.lower()
    assert "rerun" not in normalized
    assert "retry" not in normalized
