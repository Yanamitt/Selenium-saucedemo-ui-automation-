import os
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from reporting.run_context import RunContext


def build_pytest_args(context, user_args):
    return [
        "-o",
        "addopts=-vs",
        *user_args,
        f"--basetemp={context.run_dir / 'tmp'}",
        f"--html={context.report_path}",
        "--self-contained-html",
        f"--junitxml={context.junit_path}",
    ]


def main(argv=None):
    context = RunContext.create(PROJECT_ROOT)
    context.export_environment()
    os.chdir(PROJECT_ROOT)
    user_args = list(sys.argv[1:] if argv is None else argv)
    arguments = build_pytest_args(context, user_args)
    print(f"Test artifacts: {context.run_dir}")
    try:
        return int(pytest.main(arguments))
    finally:
        shutil.rmtree(context.run_dir / "tmp", ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
