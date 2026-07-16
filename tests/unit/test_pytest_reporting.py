import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_direct_pytest_writes_structured_results(tmp_path):
    environment = os.environ.copy()
    environment["TEST_ARTIFACTS_ROOT"] = str(tmp_path)
    for name in ("TEST_RUN_ID", "TEST_ARTIFACT_DIR", "TEST_RUN_STARTED_AT"):
        environment.pop(name, None)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_run_context.py::test_generate_run_id_uses_utc_timestamp_and_suffix",
            "-q",
            "-o",
            "addopts=",
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
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    assert metadata["schema_version"] == "1.0"
    assert results["summary"] == {
        "total": 1,
        "passed": 1,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
    }
    assert (run_dir / "failures.txt").is_file()
    assert (run_dir / "screenshots").is_dir()
