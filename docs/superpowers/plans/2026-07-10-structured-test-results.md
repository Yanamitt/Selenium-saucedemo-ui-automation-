# Structured Test Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为现有 Pytest UI 测试增加按 `run_id` 隔离的 HTML、JUnit XML、JSON、失败日志和截图产物。

**Architecture:** `RunContext` 统一运行 ID 和目录；`TestResultCollector` 将 Pytest 三阶段 report 聚合成稳定 JSON；`scripts/run_tests.py` 是标准运行入口，负责给 pytest-html 和 JUnit 指定同一个运行目录。现有 `conftest.py` 继续管理浏览器，同时负责连接结果收集器。

**Tech Stack:** Python 3.12+、Pytest 9、Selenium 4、pytest-html 4、标准库 JSON/dataclasses/subprocess。

## Global Constraints

- 保留当前 4 条业务测试及其断言。
- 不修改 `base/`、`pages/`、`tests/test_login.py` 或 `tests/test_e2e_flow.py`。
- 不增加第三方结果报告依赖。
- 不实现阶段 2 及之后的等待、Flow、用例扩充、CI 矩阵或重试。
- 不修改或提交 `.understand-anything/`。
- 所有时间字段使用 UTC ISO 8601，JSON 使用 UTF-8。

---

### Task 1: Run Context

**Files:**
- Create: `reporting/__init__.py`
- Create: `reporting/run_context.py`
- Create: `tests/unit/test_run_context.py`

**Interfaces:**
- Produces: `RunContext.create(project_root, environment=None, now=None, suffix=None)`
- Produces: `RunContext.export_environment(environment=None)`
- Produces: `generate_run_id(now=None, suffix=None)` and `format_utc(value)`

- [ ] **Step 1: Write failing run-context tests**

```python
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
```

- [ ] **Step 2: Verify RED**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_run_context.py -q -o addopts=`

Expected: collection error because `reporting.run_context` does not exist.

- [ ] **Step 3: Implement `RunContext` minimally**

```python
# reporting/run_context.py
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def format_utc(value):
    return _as_utc(value).isoformat().replace("+00:00", "Z")


def _parse_utc(value):
    return _as_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))


def generate_run_id(now=None, suffix=None):
    timestamp = _as_utc(now or datetime.now(timezone.utc))
    token = suffix or uuid4().hex[:8]
    return f"{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}-{token}"


@dataclass(frozen=True)
class RunContext:
    run_id: str
    project_root: Path
    run_dir: Path
    started_at: datetime

    @classmethod
    def create(cls, project_root, environment=None, now=None, suffix=None):
        env = os.environ if environment is None else environment
        root = Path(project_root).resolve()
        started_at = _parse_utc(env["TEST_RUN_STARTED_AT"]) if env.get("TEST_RUN_STARTED_AT") else _as_utc(now or datetime.now(timezone.utc))
        run_id = env.get("TEST_RUN_ID") or generate_run_id(started_at, suffix)
        if not _RUN_ID_PATTERN.fullmatch(run_id):
            raise ValueError("TEST_RUN_ID contains unsafe characters")

        configured_dir = env.get("TEST_ARTIFACT_DIR")
        if configured_dir:
            run_dir = Path(configured_dir)
            run_dir = run_dir if run_dir.is_absolute() else root / run_dir
        else:
            artifact_root = Path(env.get("TEST_ARTIFACTS_ROOT", "artifacts"))
            artifact_root = artifact_root if artifact_root.is_absolute() else root / artifact_root
            run_dir = artifact_root / run_id

        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "screenshots").mkdir(exist_ok=True)
        (run_dir / "failures.txt").touch(exist_ok=True)
        return cls(run_id, root, run_dir.resolve(), started_at)

    def export_environment(self, environment=None):
        env = os.environ if environment is None else environment
        env["TEST_RUN_ID"] = self.run_id
        env["TEST_ARTIFACT_DIR"] = str(self.run_dir)
        env["TEST_RUN_STARTED_AT"] = format_utc(self.started_at)

    @property
    def metadata_path(self):
        return self.run_dir / "metadata.json"

    @property
    def results_path(self):
        return self.run_dir / "results.json"

    @property
    def junit_path(self):
        return self.run_dir / "junit.xml"

    @property
    def report_path(self):
        return self.run_dir / "report.html"

    @property
    def failure_log(self):
        return self.run_dir / "failures.txt"

    @property
    def screenshots_dir(self):
        return self.run_dir / "screenshots"
```

- [ ] **Step 4: Verify GREEN**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_run_context.py -q -o addopts=`

Expected: `4 passed`.

### Task 2: Stable JSON Result Collector

**Files:**
- Create: `reporting/result_writer.py`
- Create: `tests/unit/test_result_writer.py`

**Interfaces:**
- Consumes: `RunContext`
- Produces: `TestResultCollector.record_phase(...)`
- Produces: `TestResultCollector.write_results(exit_code, finished_at=None)`
- Produces: `write_json(path, payload)`

- [ ] **Step 1: Write failing collector tests**

```python
import json
from datetime import datetime, timedelta, timezone

from reporting.result_writer import TestResultCollector, write_json
from reporting.run_context import RunContext


def make_context(tmp_path):
    started = datetime(2026, 7, 10, tzinfo=timezone.utc)
    return RunContext.create(tmp_path, {}, now=started, suffix="abc12345")


def test_collector_aggregates_phases_into_one_passed_test(tmp_path):
    context = make_context(tmp_path)
    collector = TestResultCollector(context)
    collector.record_phase("tests/test_demo.py::test_ok", "test_ok", ["smoke"], "setup", "passed", 0.1)
    collector.record_phase("tests/test_demo.py::test_ok", "test_ok", ["smoke"], "call", "passed", 0.2)
    collector.record_phase("tests/test_demo.py::test_ok", "test_ok", ["smoke"], "teardown", "passed", 0.1)
    payload = collector.write_results(0, context.started_at + timedelta(seconds=1))
    assert payload["summary"] == {"total": 1, "passed": 1, "failed": 0, "errors": 0, "skipped": 0}
    assert payload["tests"][0]["duration_seconds"] == 0.4


def test_setup_failure_is_reported_as_error(tmp_path):
    context = make_context(tmp_path)
    collector = TestResultCollector(context)
    collector.record_phase("tests/test_demo.py::test_bad", "test_bad", [], "setup", "failed", 0.3, "driver failed")
    payload = collector.write_results(1, context.started_at + timedelta(seconds=1))
    assert payload["tests"][0]["outcome"] == "error"
    assert payload["tests"][0]["failure_phase"] == "setup"
    assert payload["summary"]["errors"] == 1


def test_teardown_error_overrides_call_failure(tmp_path):
    context = make_context(tmp_path)
    collector = TestResultCollector(context)
    collector.record_phase("tests/test_demo.py::test_bad", "test_bad", [], "call", "failed", 0.2, "assertion")
    collector.record_phase("tests/test_demo.py::test_bad", "test_bad", [], "teardown", "failed", 0.1, "quit failed")
    payload = collector.write_results(1, context.started_at + timedelta(seconds=1))
    assert payload["tests"][0]["outcome"] == "error"
    assert payload["tests"][0]["failure_message"] == "quit failed"


def test_write_json_preserves_unicode(tmp_path):
    path = tmp_path / "result.json"
    write_json(path, {"message": "测试通过"})
    assert json.loads(path.read_text(encoding="utf-8"))["message"] == "测试通过"
```

- [ ] **Step 2: Verify RED**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_result_writer.py -q -o addopts=`

Expected: collection error because `reporting.result_writer` does not exist.

- [ ] **Step 3: Implement collector**

```python
# reporting/result_writer.py
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from reporting.run_context import format_utc


SCHEMA_VERSION = "1.0"
_PRIORITY = {"passed": 0, "skipped": 1, "failed": 2, "error": 3}


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_metadata(context, environment, git_info, versions):
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": context.run_id,
        "project": "saucedemo-automation",
        "started_at": format_utc(context.started_at),
        "environment": {
            "base_url": environment["base_url"],
            "browser": environment["browser"],
            "headless": environment["headless"],
            "selenium_timeout": environment["selenium_timeout"],
            "python": versions["python"],
            "platform": versions["platform"],
            "pytest": versions["pytest"],
            "selenium": versions["selenium"],
        },
        "git": {
            "commit": git_info.get("commit"),
            "branch": git_info.get("branch"),
        },
    }


def _final_outcome(phase, outcome):
    if outcome == "failed":
        return "failed" if phase == "call" else "error"
    if outcome == "skipped":
        return "skipped"
    return "passed"


@dataclass
class _TestRecord:
    nodeid: str
    name: str
    module: str
    markers: set = field(default_factory=set)
    outcome: str = "passed"
    duration_seconds: float = 0.0
    failure_phase: str | None = None
    failure_message: str | None = None
    screenshot: str | None = None
    phases: dict = field(default_factory=dict)

    def apply(self, markers, phase, outcome, duration, failure_message=None, screenshot=None):
        self.markers.update(markers)
        self.phases[phase] = outcome
        self.duration_seconds += duration
        candidate = _final_outcome(phase, outcome)
        if _PRIORITY[candidate] >= _PRIORITY[self.outcome]:
            self.outcome = candidate
            if candidate in {"failed", "error"}:
                self.failure_phase = phase
                self.failure_message = failure_message
        if screenshot:
            self.screenshot = screenshot

    def as_dict(self):
        return {
            "nodeid": self.nodeid,
            "name": self.name,
            "module": self.module,
            "markers": sorted(self.markers),
            "outcome": self.outcome,
            "duration_seconds": round(self.duration_seconds, 6),
            "failure_phase": self.failure_phase,
            "failure_message": self.failure_message,
            "screenshot": self.screenshot,
            "phases": dict(sorted(self.phases.items())),
        }


class TestResultCollector:
    def __init__(self, context):
        self.context = context
        self._tests = {}

    def record_phase(self, nodeid, name, markers, phase, outcome, duration, failure_message=None, screenshot=None):
        record = self._tests.setdefault(
            nodeid,
            _TestRecord(nodeid=nodeid, name=name, module=nodeid.split("::", 1)[0].replace("\\", "/")),
        )
        record.apply(markers, phase, outcome, duration, failure_message, screenshot)

    def write_results(self, exit_code, finished_at=None):
        finished = finished_at or datetime.now(timezone.utc)
        tests = [self._tests[nodeid].as_dict() for nodeid in sorted(self._tests)]
        summary = {"total": len(tests), "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
        summary_keys = {"passed": "passed", "failed": "failed", "error": "errors", "skipped": "skipped"}
        for test in tests:
            summary[summary_keys[test["outcome"]]] += 1
        payload = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.context.run_id,
            "started_at": format_utc(self.context.started_at),
            "finished_at": format_utc(finished),
            "duration_seconds": round((finished - self.context.started_at).total_seconds(), 6),
            "exit_code": int(exit_code),
            "summary": summary,
            "tests": tests,
        }
        write_json(self.context.results_path, payload)
        return payload
```

- [ ] **Step 4: Verify GREEN**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_result_writer.py -q -o addopts=`

Expected: `4 passed`.

### Task 3: Pytest Reporting Integration

**Files:**
- Modify: `conftest.py`
- Test: `tests/unit/test_run_context.py`
- Test: `tests/unit/test_result_writer.py`

**Interfaces:**
- Consumes: `RunContext`, `TestResultCollector`
- Produces: `pytest_configure`, `pytest_runtest_makereport`, `pytest_sessionfinish`

- [ ] **Step 1: Add a failing metadata contract test**

```python
from reporting.result_writer import build_metadata


def test_build_metadata_has_stable_environment_and_git_fields(tmp_path):
    context = make_context(tmp_path)
    metadata = build_metadata(
        context,
        {"base_url": "https://example.test/", "browser": "edge", "headless": True, "selenium_timeout": 10},
        {"commit": None, "branch": None},
        {"python": "3.12.13", "platform": "Windows", "pytest": "9.0.2", "selenium": "4.41.0"},
    )
    assert metadata["schema_version"] == "1.0"
    assert metadata["run_id"] == context.run_id
    assert metadata["environment"]["browser"] == "edge"
    assert metadata["environment"]["python"] == "3.12.13"
    assert metadata["git"] == {"commit": None, "branch": None}
```

- [ ] **Step 2: Verify RED**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_result_writer.py -q -o addopts=`

Expected: import failure for `build_metadata`.

- [ ] **Step 3: Implement metadata and hooks**

Add these imports and helpers to `conftest.py`, remove the module-level `SCREENSHOT_DIR` and `FAILURE_LOG`, and pass `context.failure_log` into `_append_failure_log`:

```python
import platform
import subprocess

import selenium

from reporting.result_writer import TestResultCollector, build_metadata, write_json
from reporting.run_context import RunContext
from settings import get_base_url, get_browser_name, get_timeout, is_headless


def _git_value(project_root, *args):
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={project_root.as_posix()}", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    value = completed.stdout.strip()
    return value or None if completed.returncode == 0 else None


def pytest_configure(config):
    context = RunContext.create(Path(str(config.rootpath)))
    collector = TestResultCollector(context)
    config._test_run_context = context
    config._test_result_collector = collector
    metadata = build_metadata(
        context,
        {
            "base_url": get_base_url(),
            "browser": get_browser_name(),
            "headless": is_headless(),
            "selenium_timeout": get_timeout(),
        },
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


def pytest_sessionfinish(session, exitstatus):
    session.config._test_result_collector.write_results(exitstatus)
```

Replace the report hook body with this path-aware version while retaining the existing driver lookup and browser-log helpers:

```python
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
            screenshot_path = context.screenshots_dir / f"{_safe_file_name(item.name)}_{timestamp}.png"
            try:
                web_driver.save_screenshot(str(screenshot_path))
                _attach_html_screenshot(report, str(screenshot_path))
                screenshot_reference = screenshot_path.relative_to(context.run_dir).as_posix()
            except Exception as exc:
                screenshot_reference = f"<capture failed: {exc}>"
        _append_failure_log(report, screenshot_reference, web_driver, context.failure_log)

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
```

- [ ] **Step 4: Verify GREEN and regression unit tests**

Run: `.venv\Scripts\python.exe -m pytest tests/unit -q -o addopts=`

Expected: all unit tests pass.

### Task 4: Canonical Test Runner

**Files:**
- Create: `scripts/run_tests.py`
- Create: `tests/unit/test_run_tests.py`
- Modify: `pytest.ini`

**Interfaces:**
- Consumes: `RunContext`
- Produces: `build_pytest_args(context, user_args)` and `main(argv=None)`

- [ ] **Step 1: Write failing runner tests**

```python
from scripts.run_tests import build_pytest_args
from reporting.run_context import RunContext


def test_build_pytest_args_routes_reports_to_run_directory(tmp_path):
    context = RunContext.create(tmp_path, {}, suffix="abc12345")
    args = build_pytest_args(context, ["tests/test_login.py", "-q"])
    assert f"--html={context.report_path}" in args
    assert f"--junitxml={context.junit_path}" in args
    assert "--self-contained-html" in args
    assert "tests/test_login.py" in args
```

- [ ] **Step 2: Verify RED**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_run_tests.py -q -o addopts=`

Expected: collection error because `scripts.run_tests` does not exist.

- [ ] **Step 3: Implement runner and simplify default addopts**

```python
# scripts/run_tests.py
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
```

Update `pytest.ini`:

```ini
[pytest]
addopts = -vs
norecursedirs = .git .venv .pytest_cache .understand-anything artifacts
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)s] %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S
```

- [ ] **Step 4: Verify GREEN**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_run_tests.py -q -o addopts=`

Expected: runner unit test passes.

### Task 5: CI, Documentation, and End-to-End Contract

**Files:**
- Modify: `.github/workflows/ui-tests.yml`
- Modify: `.gitignore`
- Modify: `readme.md`
- Create: `tests/unit/test_reporting_contract.py`

**Interfaces:**
- Consumes: `scripts/run_tests.py`
- Produces: documented local/CI command and complete artifact upload

- [ ] **Step 1: Write failing standard-run contract test**

```python
# tests/unit/test_reporting_contract.py
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
    for name in ("metadata.json", "results.json", "junit.xml", "report.html", "failures.txt"):
        assert (run_dir / name).exists(), name
    assert (run_dir / "screenshots").is_dir()
    assert not (run_dir / "tmp").exists()
    assert json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))["schema_version"] == "1.0"
    assert json.loads((run_dir / "results.json").read_text(encoding="utf-8"))["summary"]["total"] == 1
```

- [ ] **Step 2: Verify RED**

Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_reporting_contract.py -q -o addopts=`

Expected: failure until runner and hooks produce the full contract.

- [ ] **Step 3: Update CI and documentation**

Change only the existing CI run and upload steps:

```yaml
      - name: Run pytest
        run: python scripts/run_tests.py

      - name: Upload test artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ui-test-artifacts
          path: artifacts/
          if-no-files-found: ignore
```

Append `artifacts/` to `.gitignore`. In `readme.md`, replace direct `pytest` examples with `python scripts/run_tests.py [pytest arguments]`, document the run-directory layout exactly as defined in the design, and state that direct `pytest` writes JSON but the runner is required for the complete HTML/JUnit contract.

- [ ] **Step 4: Verify all unit tests**

Run: `.venv\Scripts\python.exe -m pytest tests/unit -q -o addopts=`

Expected: all unit tests pass without opening a browser.

- [ ] **Step 5: Verify complete UI run**

Run: `$env:HEADLESS='true'; $env:BROWSER='edge'; .venv\Scripts\python.exe scripts\run_tests.py`

Expected: `4 passed`; newest run directory contains all six artifact types; `results.json` summary is 4 passed, 0 failed, 0 errors.

- [ ] **Step 6: Review scope and diff**

Run: `git diff --check` and `git status --short`.

Expected: no whitespace errors; no changes under `base/`, `pages/`, existing business tests, or `.understand-anything/`.

## Review Hardening Addendum

独立审查后在同一阶段内补充以下已验证边界：

- [x] 无效 `BROWSER` 不再中断 `pytest_configure`；标准入口仍生成 metadata、results、JUnit、HTML 和失败日志。
- [x] 新运行拒绝复用已有内容的产物目录，runner 导出的完整上下文允许 conftest 附着。
- [x] HTML 失败截图改为 base64 data URI，下载 CI 产物后仍可查看。
- [x] `failures.txt` 使用 UTC `Z` 时间。
- [x] Pytest 临时目录清理重试三次，失败时告警但保留原测试退出码。

对应回归测试位于 `tests/unit/test_reporting_contract.py`、`tests/unit/test_run_context.py`、`tests/unit/test_failure_artifacts.py` 和 `tests/unit/test_run_tests.py`。
