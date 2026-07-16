import json
import re
import subprocess
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = PROJECT_ROOT / "docs" / "samples" / "edge-full-green"


def _is_ignored(path):
    completed = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", path],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return completed.returncode == 0


def test_runtime_and_sensitive_files_are_ignored_but_samples_are_publishable():
    ignored_paths = (
        ".understand-anything/knowledge-graph.json",
        ".env.local",
        "debug.log",
        "module.pyc",
        ".coverage",
        "htmlcov/index.html",
        "allure-results/result.json",
        "junit.xml",
        "results.json",
        "metadata.json",
        "failures.txt",
        "cookies.json",
        "session.json",
        "storage-state.json",
    )

    assert all(_is_ignored(path) for path in ignored_paths)
    assert not _is_ignored("docs/samples/edge-full-green/report.html")


def test_public_repository_documents_and_dependency_contract_are_complete():
    readme = (PROJECT_ROOT / "readme.md").read_text(encoding="utf-8")
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert (PROJECT_ROOT / "LICENSE").is_file()
    assert (PROJECT_ROOT / "SECURITY.md").is_file()
    assert "| 单元测试 | 85 | 85 Passed |" in readme
    assert "| Web UI Regression | 16 | 16 Passed |" in readme
    assert "| 完整测试集 | 101 | 101 Passed |" in readme
    assert "公开测试凭证" in readme
    assert "docs/samples/edge-full-green" in readme
    assert "webdriver-manager" not in requirements


def test_dependabot_updates_python_and_github_actions_dependencies():
    config = yaml.safe_load(
        (PROJECT_ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    )
    ecosystems = {entry["package-ecosystem"] for entry in config["updates"]}

    assert ecosystems == {"pip", "github-actions"}
    assert all(entry["schedule"]["interval"] == "weekly" for entry in config["updates"])


def test_curated_report_sample_is_green_and_contains_no_sensitive_values():
    expected_files = {"README.md", "metadata.json", "report.html", "results.json"}
    assert {path.name for path in SAMPLE_DIR.iterdir()} == expected_files

    results = json.loads((SAMPLE_DIR / "results.json").read_text(encoding="utf-8"))
    assert results["summary"] == {
        "total": 94,
        "passed": 94,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
    }

    content = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in SAMPLE_DIR.iterdir()
    )
    forbidden_patterns = (
        r"AKIA[0-9A-Z]{16}",
        r"gh[pousr]_[A-Za-z0-9_]{20,}",
        r"sk-[A-Za-z0-9_-]{20,}",
        r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
        r"[A-Za-z]:\\(?:Users|Documents|project|workspace)\\",
        r"/(?:Users|home)/[^/\s]+/",
        r"secret_sauce",
    )

    assert not any(re.search(pattern, content) for pattern in forbidden_patterns)


def test_legacy_root_failure_log_is_removed_and_ignored():
    assert not (PROJECT_ROOT / "failures.txt").exists()
    assert _is_ignored("failures.txt")
