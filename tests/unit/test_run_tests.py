from reporting.run_context import RunContext
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
