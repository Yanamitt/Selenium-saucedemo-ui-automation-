from datetime import datetime, timezone
from pathlib import Path

import pytest

from reporting.run_context import RunContext, generate_run_id


def test_generate_run_id_uses_utc_timestamp_and_suffix():
    now = datetime(2026, 7, 10, 12, 30, 45, 123456, tzinfo=timezone.utc)

    assert generate_run_id(now, "abc12345") == "20260710T123045123456Z-abc12345"


def test_create_resolves_relative_artifact_root(tmp_path):
    environment = {"TEST_ARTIFACTS_ROOT": "build-artifacts"}

    context = RunContext.create(tmp_path, environment, suffix="abc12345")

    assert context.run_dir.parent == tmp_path / "build-artifacts"
    assert context.run_dir.is_dir()


def test_create_rejects_unsafe_run_id(tmp_path):
    with pytest.raises(ValueError, match="TEST_RUN_ID"):
        RunContext.create(tmp_path, {"TEST_RUN_ID": "../escape"})


def test_export_environment_preserves_context(tmp_path):
    environment = {}
    context = RunContext.create(tmp_path, environment, suffix="abc12345")

    context.export_environment(environment)

    assert environment["TEST_RUN_ID"] == context.run_id
    assert Path(environment["TEST_ARTIFACT_DIR"]) == context.run_dir
    assert environment["TEST_RUN_STARTED_AT"].endswith("Z")


def test_create_rejects_populated_directory_for_a_new_run(tmp_path):
    run_dir = tmp_path / "artifacts" / "fixed-run"
    run_dir.mkdir(parents=True)
    (run_dir / "stale.png").write_bytes(b"old")

    with pytest.raises(ValueError, match="already contains artifacts"):
        RunContext.create(tmp_path, {"TEST_RUN_ID": "fixed-run"})


def test_create_attaches_to_a_fully_exported_context(tmp_path):
    context = RunContext.create(tmp_path, {}, suffix="abc12345")
    environment = {}
    context.export_environment(environment)

    attached = RunContext.create(tmp_path, environment)

    assert attached == context
