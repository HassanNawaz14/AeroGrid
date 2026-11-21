from __future__ import annotations

import json
from pathlib import Path

import pytest

import package_artifacts as pkg

PHASE3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PHASE3_ROOT.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wp-p3-09-package.yml"
TEMPLATE = PHASE3_ROOT / "templates" / "RELEASE_NOTES.md"


def _write(root: Path, rel: str, data: bytes = b"x") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _manifest(root: Path, **kwargs):
    kwargs.setdefault("strict", False)
    kwargs.setdefault("dry_run", True)
    kwargs.setdefault("check_tracked", False)
    return pkg.build_manifest(root, **kwargs)


def test_d3_008_limit_is_ten_mebibytes() -> None:
    assert pkg.MAX_COMMITTED_BYTES == 10 * 1024 * 1024


def test_route_follows_d3_008_boundary() -> None:
    assert pkg.route_for_size(0) == "bundle"
    assert pkg.route_for_size(pkg.MAX_COMMITTED_BYTES - 1) == "bundle"
    assert pkg.route_for_size(pkg.MAX_COMMITTED_BYTES) == "oversize"
    assert pkg.route_for_size(pkg.MAX_COMMITTED_BYTES + 1) == "oversize"


def test_registry_keys_are_unique_and_cover_course_deliverables() -> None:
    keys = [item.key for item in pkg.DELIVERABLES]
    assert len(keys) == len(set(keys))
    for expected in (
        "indexing_report", "dashboard_pbix", "dashboard_screenshots",
        "business_insights", "final_presentation", "release_notes",
    ):
        assert expected in keys


def test_empty_repo_reports_missing_and_passes_with_pending(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    assert manifest["result"] == "PASS_WITH_PENDING"
    assert manifest["files"] == []
    assert "indexing_report" in manifest["missing_required"]


def test_strict_fails_when_required_deliverable_is_missing(tmp_path: Path) -> None:
    _write(tmp_path, "Phase3/reports/Indexing_Report.pdf")
    assert _manifest(tmp_path, strict=True)["result"] == "FAIL"


def test_strict_passes_when_every_required_deliverable_exists(tmp_path: Path) -> None:
    for spec in pkg.DELIVERABLES:
        if spec.required:
            _write(tmp_path, spec.patterns[0].replace("*", "AeroGrid"))
    manifest = _manifest(tmp_path, strict=True)
    assert manifest["missing_required"] == []
    assert manifest["result"] == "PASS"


def test_pbix_is_found_in_either_deliverable_layout(tmp_path: Path) -> None:
    _write(tmp_path, "Phase3/deliverables/AeroGrid_Report/AeroGrid.pbix")
    _write(tmp_path, "Phase3/deliverables/AeroGrid_Dashboard.pbix")
    paths = {item["path"] for item in _manifest(tmp_path)["files"] if item["key"] == "dashboard_pbix"}
    assert paths == {
        "Phase3/deliverables/AeroGrid_Report/AeroGrid.pbix",
        "Phase3/deliverables/AeroGrid_Dashboard.pbix",
    }


def test_oversize_file_is_routed_to_actions_artifacts(tmp_path: Path) -> None:
    big = _write(tmp_path, "Phase3/deliverables/AeroGrid.pbix")
    with big.open("wb") as handle:
        handle.truncate(pkg.MAX_COMMITTED_BYTES)
    entry = _manifest(tmp_path)["files"][0]
    assert entry["route"] == "oversize"


def test_oversize_file_tracked_by_git_is_a_violation(tmp_path: Path, monkeypatch) -> None:
    big = _write(tmp_path, "Phase3/deliverables/AeroGrid.pbix")
    with big.open("wb") as handle:
        handle.truncate(pkg.MAX_COMMITTED_BYTES)
    monkeypatch.setattr(pkg, "tracked_paths", lambda _root: {"Phase3/deliverables/AeroGrid.pbix"})
    manifest = pkg.build_manifest(tmp_path, strict=False, dry_run=True, check_tracked=True)
    assert manifest["result"] == "FAIL"
    assert any("D3-008" in item for item in manifest["violations"])


def test_secret_scan_flags_connection_string_without_echoing_it(tmp_path: Path) -> None:
    _write(tmp_path, "Phase3/reports/Indexing_Report.pdf", b"postgresql://user:hunter2@host/db")
    manifest = _manifest(tmp_path)
    assert manifest["result"] == "FAIL"
    rendered = pkg.render_markdown(manifest)
    assert "hunter2" not in rendered
    assert "postgres-connection-string-with-password" in rendered


def test_secret_scan_ignores_a_password_free_url(tmp_path: Path) -> None:
    path = _write(tmp_path, "Phase3/reports/Indexing_Report.pdf", b"postgresql://host/db")
    assert pkg.scan_for_secrets(path) == []


def test_manifest_records_sha256_for_each_file(tmp_path: Path) -> None:
    path = _write(tmp_path, "Phase3/reports/Indexing_Report.pdf", b"abc")
    entry = _manifest(tmp_path)["files"][0]
    assert entry["sha256"] == pkg.sha256_of(path)
    assert len(entry["sha256"]) == 64


def test_stage_files_copies_by_route_and_writes_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo, "Phase3/reports/Indexing_Report.pdf", b"pdf")
    dist = tmp_path / "dist"
    manifest = _manifest(repo, dry_run=False)
    pkg.stage_files(repo, dist, manifest)
    assert (dist / "bundle" / "Phase3" / "reports" / "Indexing_Report.pdf").read_bytes() == b"pdf"
    assert json.loads((dist / "MANIFEST.json").read_text())["result"] == "PASS_WITH_PENDING"


def test_dry_run_creates_no_dist_folder(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo, "Phase3/reports/Indexing_Report.pdf")
    dist = tmp_path / "dist"
    code = pkg.main(["--repo-root", str(repo), "--dist", str(dist), "--dry-run", "--no-git-check"])
    assert code == 0
    assert not dist.exists()


def test_main_returns_nonzero_in_strict_mode_with_gaps(tmp_path: Path) -> None:
    code = pkg.main(["--repo-root", str(tmp_path), "--dry-run", "--strict", "--no-git-check"])
    assert code == 1


def test_workflow_is_manual_and_uses_no_secrets_or_environment() -> None:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    text = "\n".join(line for line in lines if not line.lstrip().startswith("#"))
    assert "workflow_dispatch" in text
    assert "schedule:" not in text
    assert "secrets." not in text
    assert "environment:" not in text
    assert "contents: read" in text
    assert "timeout-minutes" in text
    assert "concurrency:" in text
    assert "package_artifacts.py" in text


@pytest.mark.parametrize(
    "heading",
    [
        "## Release identity", "## Deliverables", "## Size guard (D3-008)",
        "## Evidence and checks", "## Known limitations", "## Human acceptance",
    ],
)
def test_release_notes_template_has_required_sections(heading: str) -> None:
    assert heading in TEMPLATE.read_text(encoding="utf-8")


def test_release_notes_template_holds_no_secret_pattern() -> None:
    assert pkg.scan_for_secrets(TEMPLATE) == []
