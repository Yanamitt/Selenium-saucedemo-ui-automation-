import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from reporting.run_context import format_utc


SCHEMA_VERSION = "1.0"
_OUTCOME_PRIORITY = {"passed": 0, "skipped": 1, "failed": 2, "error": 3}


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(content, encoding="utf-8")


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

    def apply(
        self,
        markers,
        phase,
        outcome,
        duration,
        failure_message=None,
        screenshot=None,
    ):
        self.markers.update(markers)
        self.phases[phase] = outcome
        self.duration_seconds += duration
        candidate = _final_outcome(phase, outcome)

        if _OUTCOME_PRIORITY[candidate] >= _OUTCOME_PRIORITY[self.outcome]:
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
    __test__ = False

    def __init__(self, context):
        self.context = context
        self._tests = {}

    def record_phase(
        self,
        nodeid,
        name,
        markers,
        phase,
        outcome,
        duration,
        failure_message=None,
        screenshot=None,
    ):
        record = self._tests.setdefault(
            nodeid,
            _TestRecord(
                nodeid=nodeid,
                name=name,
                module=nodeid.split("::", 1)[0].replace("\\", "/"),
            ),
        )
        record.apply(
            markers,
            phase,
            outcome,
            duration,
            failure_message,
            screenshot,
        )

    def write_results(self, exit_code, finished_at=None):
        finished = finished_at or datetime.now(timezone.utc)
        tests = [self._tests[nodeid].as_dict() for nodeid in sorted(self._tests)]
        summary = {
            "total": len(tests),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
        }
        summary_keys = {
            "passed": "passed",
            "failed": "failed",
            "error": "errors",
            "skipped": "skipped",
        }
        for test in tests:
            summary[summary_keys[test["outcome"]]] += 1

        payload = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.context.run_id,
            "started_at": format_utc(self.context.started_at),
            "finished_at": format_utc(finished),
            "duration_seconds": round(
                (finished - self.context.started_at).total_seconds(), 6
            ),
            "exit_code": int(exit_code),
            "summary": summary,
            "tests": tests,
        }
        write_json(self.context.results_path, payload)
        return payload
