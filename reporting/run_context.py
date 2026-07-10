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
        if env.get("TEST_RUN_STARTED_AT"):
            started_at = _parse_utc(env["TEST_RUN_STARTED_AT"])
        else:
            started_at = _as_utc(now or datetime.now(timezone.utc))

        run_id = env.get("TEST_RUN_ID") or generate_run_id(started_at, suffix)
        if not _RUN_ID_PATTERN.fullmatch(run_id):
            raise ValueError("TEST_RUN_ID contains unsafe characters")

        configured_dir = env.get("TEST_ARTIFACT_DIR")
        if configured_dir:
            run_dir = Path(configured_dir)
            if not run_dir.is_absolute():
                run_dir = root / run_dir
        else:
            artifact_root = Path(env.get("TEST_ARTIFACTS_ROOT", "artifacts"))
            if not artifact_root.is_absolute():
                artifact_root = root / artifact_root
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
