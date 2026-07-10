from reporting.run_context import RunContext
import scripts.run_tests as test_runner
from scripts.run_tests import build_pytest_args


def test_build_pytest_args_routes_reports_to_run_directory(tmp_path):
    context = RunContext.create(tmp_path, {}, suffix="abc12345")

    arguments = build_pytest_args(context, ["tests/test_login.py", "-q"])

    assert f"--html={context.report_path}" in arguments
    assert f"--junitxml={context.junit_path}" in arguments
    assert f"--basetemp={context.run_dir / 'tmp'}" in arguments
    assert "--self-contained-html" in arguments
    assert "tests/test_login.py" in arguments
    assert "-q" in arguments


def test_cleanup_runtime_temp_retries_and_warns(tmp_path, monkeypatch, capsys):
    runtime_temp = tmp_path / "tmp"
    runtime_temp.mkdir()
    attempts = []

    def locked_rmtree(path):
        attempts.append(path)
        raise PermissionError("locked")

    monkeypatch.setattr(test_runner.shutil, "rmtree", locked_rmtree)
    monkeypatch.setattr(test_runner.time, "sleep", lambda _seconds: None)

    cleaned = test_runner._cleanup_runtime_temp(runtime_temp)

    assert cleaned is False
    assert attempts == [runtime_temp, runtime_temp, runtime_temp]
    assert "Unable to remove pytest temp directory" in capsys.readouterr().err
