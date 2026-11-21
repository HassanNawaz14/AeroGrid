#!/usr/bin/env python3
"""Package the Phase 3 release artifacts under the D3-008 size guard (WP-P3-09).

The script reads the committed Phase 3 deliverables, never the warehouse. It needs no
database connection and no secrets. For every expected deliverable it records the
path, size, SHA-256 and routing:

* ``bundle``   - smaller than 10 MiB; may be committed (D3-008).
* ``oversize`` - 10 MiB or larger; must not be committed and is published as a GitHub
  Actions artifact instead (D3-008).

Missing deliverables are reported as ``MISSING``. They only fail the run with
``--strict`` (the final release run). A secret-pattern hit or an oversized file that
is tracked by Git always fails the run. Nothing here creates, edits or fabricates a
deliverable: files are only read and, outside ``--dry-run``, copied into ``dist/``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIST = REPO_ROOT / "dist" / "phase3"
MAX_COMMITTED_BYTES = 10 * 1024 * 1024  # D3-008: commit only when < 10 MiB each
RULE_ID = "D3-008"

SECRET_PATTERNS: dict[str, re.Pattern[bytes]] = {
    "postgres-connection-string-with-password": re.compile(
        rb"postgres(?:ql)?://[^\s:/@]+:[^\s@]+@"
    ),
    "private-key-block": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github-token": re.compile(rb"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{36}\b"),
    "github-fine-grained-token": re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
}


@dataclass(frozen=True)
class Deliverable:
    key: str
    title: str
    wp: str
    owner: str
    patterns: tuple[str, ...]
    required: bool = True
    kind: str = "deliverable"


DELIVERABLES: tuple[Deliverable, ...] = (
    Deliverable(
        "indexing_report", "Indexing report (PDF)", "WP-P3-05", "D",
        ("Phase3/reports/Indexing_Report.pdf",),
    ),
    Deliverable(
        "dashboard_pbix", "Power BI dashboard (PBIX)", "WP-P3-06", "E",
        ("Phase3/deliverables/*.pbix", "Phase3/deliverables/*/*.pbix"),
    ),
    Deliverable(
        "dashboard_screenshots", "Dashboard screenshots (PDF)", "WP-P3-06", "E",
        ("Phase3/reports/Dashboard_Screenshots.pdf", "Phase3/deliverables/*/screenshots.pdf"),
    ),
    Deliverable(
        "business_insights", "Business insights report (PDF)", "WP-P3-07", "E",
        ("Phase3/reports/Business_Insights_Report.pdf",),
    ),
    Deliverable(
        "final_presentation", "Final presentation (PPTX)", "WP-P3-08", "E",
        ("Phase3/deliverables/Final_Presentation.pptx",),
    ),
    Deliverable(
        "release_notes", "Release notes", "WP-P3-09", "A",
        ("Phase3/RELEASE_NOTES.md",),
    ),
    Deliverable(
        "evidence_analytics", "Analytics run evidence", "WP-P3-02/03", "E",
        ("Phase3/evidence/analytics_run_*.md",), required=False, kind="evidence",
    ),
    Deliverable(
        "evidence_gold_views", "Gold-view evidence", "WP-P3-04", "E",
        ("Phase3/evidence/gold_views_*.md",), required=False, kind="evidence",
    ),
    Deliverable(
        "evidence_indexes", "Index measurement evidence", "WP-P3-05", "D",
        ("Phase3/evidence/index_optimization_*.json", "Phase3/evidence/index_optimization_*.md"),
        required=False, kind="evidence",
    ),
)


def route_for_size(size_bytes: int) -> str:
    """D3-008: strictly under 10 MiB is committable; 10 MiB or more is an Actions artifact."""
    return "bundle" if size_bytes < MAX_COMMITTED_BYTES else "oversize"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_for_secrets(path: Path) -> list[str]:
    """Return the names of secret patterns found. Matched text is never returned.

    Only uncompressed bytes are inspected; compressed PDF streams are not decoded.
    """
    hits: set[str] = set()
    overlap = 256
    tail = b""
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            window = tail + chunk
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(window):
                    hits.add(name)
            tail = window[-overlap:]
    return sorted(hits)


def resolve_files(repo_root: Path, spec: Deliverable) -> list[Path]:
    found: dict[str, Path] = {}
    for pattern in spec.patterns:
        for path in repo_root.glob(pattern):
            if path.is_file():
                found[path.relative_to(repo_root).as_posix()] = path
    return [found[key] for key in sorted(found)]


def tracked_paths(repo_root: Path) -> set[str] | None:
    """Repo-relative paths tracked by Git, or None when Git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z"],
            capture_output=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {item for item in result.stdout.decode("utf-8", "replace").split("\0") if item}


def git_commit(repo_root: Path) -> str:
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True, check=True, text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def build_manifest(
    repo_root: Path,
    *,
    strict: bool,
    dry_run: bool,
    check_tracked: bool = True,
    now: datetime | None = None,
) -> dict:
    captured = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    tracked = tracked_paths(repo_root) if check_tracked else None
    entries: list[dict] = []
    summary: list[dict] = []
    violations: list[str] = []

    for spec in DELIVERABLES:
        files = resolve_files(repo_root, spec)
        summary.append(
            {
                "key": spec.key, "title": spec.title, "wp": spec.wp, "owner": spec.owner,
                "kind": spec.kind, "required": spec.required,
                "status": "PRESENT" if files else "MISSING",
                "file_count": len(files),
            }
        )
        for path in files:
            rel = path.relative_to(repo_root).as_posix()
            size = path.stat().st_size
            route = route_for_size(size)
            secrets = scan_for_secrets(path)
            is_tracked = None if tracked is None else rel in tracked
            if secrets:
                violations.append(f"{rel}: secret pattern(s) {', '.join(secrets)}")
            if route == "oversize" and is_tracked:
                violations.append(f"{rel}: {size} bytes is tracked by Git but violates {RULE_ID}")
            entries.append(
                {
                    "key": spec.key, "wp": spec.wp, "path": rel, "bytes": size,
                    "mib": round(size / (1024 * 1024), 3), "sha256": sha256_of(path),
                    "route": route, "tracked_by_git": is_tracked,
                    "secret_scan": "FAIL" if secrets else "PASS",
                }
            )

    missing_required = [item["key"] for item in summary if item["required"] and item["status"] == "MISSING"]
    if violations:
        result = "FAIL"
    elif missing_required and strict:
        result = "FAIL"
    elif missing_required:
        result = "PASS_WITH_PENDING"
    else:
        result = "PASS"

    return {
        "captured_utc": captured,
        "mode": "dry-run" if dry_run else "package",
        "strict": strict,
        "rule": RULE_ID,
        "limit_bytes": MAX_COMMITTED_BYTES,
        "commit": git_commit(repo_root),
        "environment": "github-actions" if os.environ.get("GITHUB_ACTIONS") else "local",
        "result": result,
        "missing_required": missing_required,
        "violations": violations,
        "deliverables": summary,
        "files": entries,
    }


def stage_files(repo_root: Path, dist: Path, manifest: dict) -> None:
    for sub in ("bundle", "oversize"):
        target = dist / sub
        if target.exists():
            shutil.rmtree(target)
    dist.mkdir(parents=True, exist_ok=True)
    for entry in manifest["files"]:
        destination = dist / entry["route"] / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_root / entry["path"], destination)
    (dist / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def render_markdown(manifest: dict) -> str:
    lines = [
        "# Phase 3 artifact packaging record",
        "",
        f"- Captured (UTC): `{manifest['captured_utc']}`",
        f"- Mode: `{manifest['mode']}`; strict: `{str(manifest['strict']).lower()}`",
        f"- Environment: `{manifest['environment']}`; commit: `{manifest['commit']}`",
        f"- Rule: `{manifest['rule']}` - commit only when < "
        f"{manifest['limit_bytes'] // (1024 * 1024)} MiB each; larger files are Actions artifacts",
        f"- Result: **{manifest['result']}**",
        "",
        "## Deliverable coverage",
        "",
        "| Key | WP | Owner | Kind | Required | Status | Files |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in manifest["deliverables"]:
        lines.append(
            f"| `{item['key']}` | {item['wp']} | {item['owner']} | {item['kind']} | "
            f"{'yes' if item['required'] else 'no'} | {item['status']} | {item['file_count']} |"
        )
    lines += ["", "## Files", ""]
    if manifest["files"]:
        lines += [
            "| Path | Bytes | MiB | Route | Secret scan | SHA-256 |",
            "|---|---:|---:|---|---|---|",
        ]
        for entry in manifest["files"]:
            lines.append(
                f"| `{entry['path']}` | {entry['bytes']} | {entry['mib']} | {entry['route']} | "
                f"{entry['secret_scan']} | `{entry['sha256']}` |"
            )
    else:
        lines.append("No deliverable files were found.")
    lines += ["", "## Findings", ""]
    if manifest["violations"]:
        lines += [f"- VIOLATION: {item}" for item in manifest["violations"]]
    else:
        lines.append("- No secret-pattern hits and no oversized tracked files.")
    if manifest["missing_required"]:
        lines.append(
            "- Required deliverables not yet present: "
            + ", ".join(f"`{key}`" for key in manifest["missing_required"])
            + ". A missing file is reported, never created or simulated."
        )
    lines += [
        "",
        "Secret scan limits: only uncompressed bytes are inspected, so compressed PDF "
        "streams are not decoded. Review screenshots and PDFs by eye before release.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    parser.add_argument("--dry-run", action="store_true", help="Report only; copy nothing")
    parser.add_argument("--strict", action="store_true", help="Fail when a required deliverable is missing")
    parser.add_argument("--no-git-check", action="store_true", help="Skip the tracked-oversize check")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--md-output", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = build_manifest(
        args.repo_root.resolve(),
        strict=args.strict,
        dry_run=args.dry_run,
        check_tracked=not args.no_git_check,
    )
    if not args.dry_run:
        stage_files(args.repo_root.resolve(), args.dist, manifest)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_markdown(manifest)
    if args.md_output:
        args.md_output.parent.mkdir(parents=True, exist_ok=True)
        args.md_output.write_text(markdown, encoding="utf-8")
    print(markdown)
    return 1 if manifest["result"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
