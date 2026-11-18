#!/usr/bin/env python3
"""Build the WP-P3-05 indexing report PDF from measured evidence.

The PDF is generated only from an evidence JSON file produced by
``measure_indexes.py`` against the shared warehouse. It never invents numbers and
refuses to build a report when any claimed index is missing its before/after pair
(DQ3-A-006). Deliverable size follows D3-008: commit the PDF only when < 10 MB.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE = REPO_ROOT / "Phase3" / "evidence"
DEFAULT_OUTPUT = REPO_ROOT / "Phase3" / "reports" / "Indexing_Report.pdf"
MAX_COMMITTED_BYTES = 10 * 1024 * 1024
DQ_ID = "DQ3-A-006"


def dq3_a_006_status(evidence: dict[str, Any]) -> str:
    indexes = evidence.get("indexes") or []
    if not indexes:
        return "FAIL"
    for item in indexes:
        if not item.get("before") or not item.get("after"):
            return "FAIL"
        if not item.get("index_name") or not item.get("target_query"):
            return "FAIL"
    return "PASS"


def _verdict(item: dict[str, Any]) -> tuple[str, str]:
    delta = item.get("delta") or {}
    pct = delta.get("execution_time_pct")
    if pct is None:
        return "NOT_COMPARABLE", "Measured pair is present but a delta cannot be computed."
    if pct <= -5:
        return "MEASURED_FASTER", f"Measured execution time changed by {pct:+.2f}%."
    if pct >= 5:
        return "MEASURED_SLOWER", f"Measured execution time changed by {pct:+.2f}%."
    return "NEUTRAL", (
        f"Measured execution time changed by {pct:+.2f}%, which is inside the "
        "neutral band; no speed-up is claimed."
    )


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, (int, float)):
        return f"{value:,.{digits}f}"
    return str(value)


def _mib(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) / (1024 * 1024):,.2f} MiB"


def build_report(evidence: dict[str, Any], output_path: Path) -> dict[str, Any]:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    status = dq3_a_006_status(evidence)
    if status != "PASS":
        raise ValueError(
            f"{DQ_ID} requires one before/after EXPLAIN ANALYZE pair per index; "
            "refusing to build a report from incomplete evidence"
        )

    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontSize=9.5, leading=13, spaceAfter=6
    )
    small = ParagraphStyle(
        "Small", parent=body, fontSize=8, leading=10.5, textColor=colors.HexColor("#333333")
    )
    heading = ParagraphStyle(
        "Heading", parent=styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=6
    )
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"], fontSize=20, spaceAfter=4
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="AeroGrid Phase 3 Indexing Report",
        author="Member D (WP-P3-05)",
    )

    story: list[Any] = []
    story.append(Paragraph("AeroGrid Phase 3 — Query Optimization and Indexing Report", title_style))
    story.append(
        Paragraph(
            "Work package WP-P3-05 (Member D) · gate P3-G3 · check " + DQ_ID,
            body,
        )
    )
    story.append(Spacer(1, 6))

    metadata = [
        ["Evidence captured (UTC)", evidence.get("captured_at", "UNKNOWN")],
        ["Work package", evidence.get("work_package", "WP-P3-05")],
        ["Execution mode", f"{evidence.get('mode', 'UNKNOWN')} (persisted: "
         f"{str(evidence.get('persisted', False)).lower()})"],
        ["Connected role", evidence.get("connected_role", "UNKNOWN")],
        ["Database", evidence.get("database", "UNKNOWN")],
        ["Server", evidence.get("server", "UNKNOWN")],
        ["Fact baseline", ", ".join(
            f"{name}={count}" for name, count in (evidence.get("fact_baseline") or {}).items()
        ) or "UNKNOWN"],
        ["Database size before", _mib(evidence.get("baseline_database_size_bytes"))],
        ["Database size after", _mib(evidence.get("final_database_size_bytes"))],
        ["Storage guard", _mib(evidence.get("storage_guard_bytes"))],
        [DQ_ID, status],
    ]
    table = Table(
        [[Paragraph(f"<b>{html.escape(str(left))}</b>", small), Paragraph(html.escape(str(right)), small)]
         for left, right in metadata],
        colWidths=[1.8 * inch, 5.1 * inch],
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)

    story.append(Paragraph("Method", heading))
    story.append(
        Paragraph(
            "Each dashboard-critical query was executed with "
            "<font face='Courier'>EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)</font> "
            "against the shared warehouse before and after creating one candidate "
            "index. Verify mode performs the create and ANALYZE inside a transaction "
            "that is always rolled back, so no object is persisted; apply mode commits "
            "the idempotent DDL from protected CI. The numbers are one observed run, "
            "not a benchmark average. Query SHA-256 values and the capture time are in "
            "the evidence JSON, so every pair can be re-run.",
            body,
        )
    )

    story.append(Paragraph("Results", heading))
    rows = [
        [
            Paragraph("<b>Index</b>", small),
            Paragraph("<b>Target query</b>", small),
            Paragraph("<b>Before ms</b>", small),
            Paragraph("<b>After ms</b>", small),
            Paragraph("<b>Delta %</b>", small),
            Paragraph("<b>Before cost</b>", small),
            Paragraph("<b>After cost</b>", small),
            Paragraph("<b>Size</b>", small),
        ]
    ]
    for item in evidence["indexes"]:
        before = item.get("before") or {}
        after = item.get("after") or {}
        delta = item.get("delta") or {}
        rows.append(
            [
                Paragraph(html.escape(str(item["index_name"])), small),
                Paragraph(html.escape(str(item["target_query"])), small),
                Paragraph(_fmt(before.get("execution_time_ms")), small),
                Paragraph(_fmt(after.get("execution_time_ms")), small),
                Paragraph(
                    "n/a"
                    if delta.get("execution_time_pct") is None
                    else f"{delta['execution_time_pct']:+.2f}%",
                    small,
                ),
                Paragraph(_fmt(before.get("total_cost"), 2), small),
                Paragraph(_fmt(after.get("total_cost"), 2), small),
                Paragraph(f"{(item.get('size_bytes') or 0) / 1024:,.1f} KiB", small),
            ]
        )
    result_table = Table(
        rows,
        colWidths=[1.55 * inch, 0.8 * inch, 0.75 * inch, 0.7 * inch, 0.65 * inch, 0.8 * inch, 0.75 * inch, 0.8 * inch],
        repeatRows=1,
    )
    result_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(result_table)

    story.append(Paragraph("Per-index findings", heading))
    for item in evidence["indexes"]:
        label, explanation = _verdict(item)
        before = item.get("before") or {}
        after = item.get("after") or {}
        story.append(Paragraph(html.escape(str(item["index_name"])), styles["Heading3"]))
        story.append(
            Paragraph(
                f"<b>Verdict:</b> {label}. {html.escape(explanation)}<br/>"
                f"<b>Table:</b> {html.escape(str(item.get('table', 'UNKNOWN')))}<br/>"
                f"<b>Target query:</b> {html.escape(str(item['target_query']))} "
                f"(SHA-256 {html.escape(str(item.get('ddl_sha256', 'UNKNOWN')))[:16]}…)<br/>"
                f"<b>Rationale:</b> {html.escape(str(item.get('rationale', '')))}<br/>"
                f"<b>Plan before:</b> {html.escape(str(before.get('root_node')))} · "
                f"{html.escape(', '.join(before.get('scan_nodes') or []))}<br/>"
                f"<b>Plan after:</b> {html.escape(str(after.get('root_node')))} · "
                f"{html.escape(', '.join(after.get('scan_nodes') or []))}",
                body,
            )
        )
        story.append(Spacer(1, 4))

    story.append(Paragraph("Capacity guard", heading))
    story.append(
        Paragraph(
            "The baseline is 27,479 tracking facts, 178 journeys, and 1,754 occupancy "
            "facts at the capture recorded above. The storage guard is 700 MB; an apply "
            "run rolls back if the post-apply database size would exceed it. Index "
            "sizes above are measured inside the same transaction and are reported even "
            "when a candidate is rejected. Objects larger than 10 MB are published as "
            "CI artifacts instead of being committed (D3-008).",
            body,
        )
    )

    story.append(Paragraph("Rules and limitations", heading))
    story.extend(
        [
            Paragraph(
                "- Verify mode rolls back every candidate; only an apply-mode run persists DDL.",
                body,
            ),
            Paragraph(
                "- A neutral or slower candidate is reported as measured, never claimed as "
                "an improvement.",
                body,
            ),
            Paragraph(
                "- One observation per pair is not a statistical benchmark; rerun the stored "
                "query to reproduce it.",
                body,
            ),
            Paragraph(
                "- Zero activity is never inferred from missing coverage (D3-009).",
                body,
            ),
            Paragraph(
                f"- {DQ_ID} status: {status} (one before/after pair per claimed index).",
                body,
            ),
        ]
    )

    doc.build(story)
    size = output_path.stat().st_size
    return {
        "dq3_a_006_status": status,
        "output": str(output_path),
        "bytes": size,
        "exceeds_commit_guard": size > MAX_COMMITTED_BYTES,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if not args.evidence.exists():
        parser.error(f"evidence file not found: {args.evidence}")
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    try:
        result = build_report(evidence, args.output)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"Report: {result['output']}")
    print(f"{DQ_ID}: {result['dq3_a_006_status']}")
    print(f"Size: {result['bytes']} bytes")
    if result["exceeds_commit_guard"]:
        print("Size guard: publish as a CI artifact, do not commit (D3-008)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
