import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_standard_run_creates_complete_artifact_contract(tmp_path):
    environment = os.environ.copy()
    environment["TEST_ARTIFACTS_ROOT"] = str(tmp_path)
    for name in ("TEST_RUN_ID", "TEST_ARTIFACT_DIR", "TEST_RUN_STARTED_AT"):
        environment.pop(name, None)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_tests.py",
            "tests/unit/test_run_context.py::test_create_resolves_relative_artifact_root",
            "-q",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    run_directories = [path for path in tmp_path.iterdir() if path.is_dir()]
    assert len(run_directories) == 1
    run_dir = run_directories[0]
    for name in (
        "metadata.json",
        "results.json",
        "junit.xml",
        "report.html",
        "failures.txt",
    ):
        assert (run_dir / name).is_file(), name
    assert (run_dir / "screenshots").is_dir()
    assert not (run_dir / "tmp").exists()

    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    assert metadata["schema_version"] == "1.0"
    assert results["summary"]["total"] == 1


def test_invalid_browser_still_creates_complete_failure_contract(tmp_path):
    environment = os.environ.copy()
    environment["BROWSER"] = "safari"
    environment["TEST_ARTIFACTS_ROOT"] = str(tmp_path)
    for name in ("TEST_RUN_ID", "TEST_ARTIFACT_DIR", "TEST_RUN_STARTED_AT"):
        environment.pop(name, None)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_tests.py",
            "tests/test_login.py::test_login_failures[locked-out-user]",
            "-q",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1, completed.stdout + completed.stderr
    run_directories = [path for path in tmp_path.iterdir() if path.is_dir()]
    assert len(run_directories) == 1
    run_dir = run_directories[0]
    for name in (
        "metadata.json",
        "results.json",
        "junit.xml",
        "report.html",
        "failures.txt",
    ):
        assert (run_dir / name).is_file(), name

    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    assert metadata["environment"]["browser"] == "safari"
    assert metadata["environment"]["configuration_errors"] == [
        "BROWSER must be one of: chrome, edge, firefox"
    ]
    assert results["summary"] == {
        "total": 1,
        "passed": 0,
        "failed": 0,
        "errors": 1,
        "skipped": 0,
    }
    assert not (run_dir / "tmp").exists()
