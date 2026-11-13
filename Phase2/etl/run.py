"""WP-11: recurring ingestion for the approved weather, UAS, and airspace sources.

``validate`` fetches and parses real sources with no database access and prints
per-source coverage. ``apply`` is restricted to the protected warehouse GitHub
Actions job and requires the typed confirmation string. Every write (manifests,
staging, dimension refresh, DQ audit) happens in one transaction; a CRITICAL DQ
failure rolls the ingestion back and records the failure as its own run.
"""
from __future__ import annotations

import argparse
import os
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from etl.config import (
    DEFAULT_SOURCES,
    DEFAULT_STATIONS,
    DEFAULT_WINDOW_DAYS,
    KNOWN_SOURCES,
    LIMITATIONS,
    SOURCE_LICENSES,
)
from etl.dimension_loaders import refresh_dimensions
from etl.dq import evaluate, summary as dq_summary
from etl.errors import RowRejected
from etl.fetch import FetchedFile, fetch_sources, recent_window
from etl.loaders import (
    iter_awc_json,
    iter_faa_geojson,
    iter_iem_csv,
    iter_nightjar_csv,
    iter_nominal_csv,
    load_awc,
    load_faa,
    load_iem,
    load_nightjar,
    load_nominal,
)
from etl.sources.dji_nominal import normalize_nominal_row
from etl.sources.faa import normalize_airspace_feature
from etl.sources.metar import normalize_awc_observation, normalize_iem_row
from etl.sources.nightjar import normalize_nightjar_row
from etl.staging_writer import (
    LoadCounts,
    finish_etl_run,
    record_source_manifest,
    start_etl_run,
)

CODE_VERSION = "wp11-v1"
APPLY_CONFIRMATION = "APPROVE_WP11_APPLY"
PREVIEW_RUN_ID = "wp11-preview"
BATCH_SIZE = 500


@dataclass
class PreviewCounts:
    rows_read: int = 0
    rows_accepted: int = 0
    rows_rejected: int = 0
    rejects_by_reason: dict[str, int] = field(default_factory=dict)

    def add(self, other: "PreviewCounts") -> None:
        self.rows_read += other.rows_read
        self.rows_accepted += other.rows_accepted
        self.rows_rejected += other.rows_rejected
        for reason, count in other.rejects_by_reason.items():
            self.rejects_by_reason[reason] = (
                self.rejects_by_reason.get(reason, 0) + count
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows_read": self.rows_read,
            "rows_accepted": self.rows_accepted,
            "rows_rejected": self.rows_rejected,
            "rejects_by_reason": dict(sorted(self.rejects_by_reason.items())),
        }


def _preview_rows(f: FetchedFile) -> Iterable[Callable[[], Mapping[str, Any]]]:
    """Yield one zero-argument normalizer call per parsed source row."""
    logical = f.path.name
    if f.system == "IEM":
        station = (f.station_icao or "").strip().upper()
        for raw in iter_iem_csv(f.path):
            valid = str(raw.get("valid") or "").strip()

            def normalize(raw=raw, valid=valid):
                return normalize_iem_row(
                    raw,
                    station_icao=station,
                    source_record_id=f"iem:{station}:{valid}",
                    etl_run_id=PREVIEW_RUN_ID,
                    source_manifest_id=None,
                )

            yield normalize
    elif f.system == "AWC":
        for raw in iter_awc_json(f.path):
            station = str(raw.get("icaoId") or "").strip().upper()
            obs_time = raw.get("obsTime")

            def normalize(raw=raw, station=station, obs_time=obs_time):
                return normalize_awc_observation(
                    raw,
                    source_record_id=f"awc:{station}:{obs_time}",
                    etl_run_id=PREVIEW_RUN_ID,
                    source_manifest_id=None,
                )

            yield normalize
    elif f.system == "Nightjar":
        for raw in iter_nightjar_csv(f.path):
            number = int(raw["_source_row_number"])

            def normalize(raw=raw, number=number):
                return normalize_nightjar_row(
                    raw,
                    source_file=logical,
                    row_number=number,
                    etl_run_id=PREVIEW_RUN_ID,
                    source_manifest_id=None,
                )

            yield normalize
    elif f.system == "Nominal-DJI":
        for raw in iter_nominal_csv(f.path):
            number = int(raw["_source_row_number"])

            def normalize(raw=raw, number=number):
                return normalize_nominal_row(
                    raw,
                    source_file=logical,
                    row_number=number,
                    etl_run_id=PREVIEW_RUN_ID,
                    source_manifest_id=None,
                    site_code=f.site_code,
                )

            yield normalize
    elif f.system == "FAA-Airspace":
        for raw in iter_faa_geojson(f.path):

            def normalize(raw=raw):
                return normalize_airspace_feature(
                    raw,
                    service_name=f.service_name or "",
                    feature_type=f.feature_type or "AIRSPACE",
                    etl_run_id=PREVIEW_RUN_ID,
                    source_manifest_id=None,
                )

            yield normalize
    else:
        raise ValueError(f"Unsupported fetched source: {f.system}")


def preview_file(f: FetchedFile) -> PreviewCounts:
    counts = PreviewCounts()
    for normalize in _preview_rows(f):
        counts.rows_read += 1
        try:
            normalize()
        except RowRejected as exc:
            counts.rows_rejected += 1
            counts.rejects_by_reason[exc.reason_code] = (
                counts.rejects_by_reason.get(exc.reason_code, 0) + 1
            )
        except Exception:
            counts.rows_rejected += 1
            counts.rejects_by_reason["UNEXPECTED_ERROR"] = (
                counts.rejects_by_reason.get("UNEXPECTED_ERROR", 0) + 1
            )
        else:
            counts.rows_accepted += 1
    return counts


def preview_sources(
    files: Iterable[FetchedFile],
) -> tuple[dict[str, dict[str, Any]], dict[str, PreviewCounts]]:
    per_file: dict[str, dict[str, Any]] = {}
    totals: dict[str, PreviewCounts] = {}
    for f in files:
        counts = preview_file(f)
        per_file[f"{f.source}:{f.path.name}"] = counts.to_dict()
        totals.setdefault(f.source, PreviewCounts()).add(counts)
    return per_file, totals


def check_preview_totals(totals: Mapping[str, PreviewCounts]) -> None:
    """Fail validate when a requested source produced nothing usable."""
    empty = sorted(
        source for source, counts in totals.items() if counts.rows_accepted == 0
    )
    if empty:
        raise RuntimeError(
            "No accepted rows for: " + ", ".join(empty)
            + ". This is missing coverage, not a measured zero."
        )


def _content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "text/csv"
    if suffix == ".geojson":
        return "application/geo+json"
    return "application/json"


def check_licenses(files: Iterable[FetchedFile]) -> None:
    """Fail readably instead of a KeyError when a fetched system has no licence."""
    missing = sorted({f.system for f in files} - set(SOURCE_LICENSES))
    if missing:
        raise ValueError(
            "No licence recorded for fetched systems: " + ", ".join(missing)
        )


def apply_files(
    conn: Any,
    files: Iterable[FetchedFile],
    *,
    etl_run_id: int,
    fetched_at: datetime,
) -> tuple[dict[str, dict[str, Any]], LoadCounts, int]:
    per_file: dict[str, dict[str, Any]] = {}
    totals = LoadCounts()
    manifests = 0
    for f in files:
        license_name, attribution = SOURCE_LICENSES[f.system]
        manifest_id = record_source_manifest(
            conn,
            source_name=f.system,
            source_url=f.url,
            license_name=license_name,
            attribution=attribution,
            fetched_at=fetched_at,
            file_path=f.path,
            content_type=_content_type(f.path),
        )
        manifests += 1
        if f.system == "IEM":
            counts = load_iem(
                conn,
                f.path,
                station_icao=f.station_icao,
                etl_run_id=etl_run_id,
                source_manifest_id=manifest_id,
                batch_size=BATCH_SIZE,
            )
        elif f.system == "AWC":
            counts = load_awc(
                conn,
                f.path,
                etl_run_id=etl_run_id,
                source_manifest_id=manifest_id,
                batch_size=BATCH_SIZE,
            )
        elif f.system == "Nightjar":
            counts = load_nightjar(
                conn,
                f.path,
                etl_run_id=etl_run_id,
                source_manifest_id=manifest_id,
                batch_size=BATCH_SIZE,
            )
        elif f.system == "Nominal-DJI":
            counts = load_nominal(
                conn,
                f.path,
                etl_run_id=etl_run_id,
                site_code=f.site_code,
                source_manifest_id=manifest_id,
                batch_size=BATCH_SIZE,
            )
        elif f.system == "FAA-Airspace":
            counts = load_faa(
                conn,
                f.path,
                kind="airspace",
                service_name=f.service_name,
                feature_type=f.feature_type,
                etl_run_id=etl_run_id,
                source_manifest_id=manifest_id,
                batch_size=BATCH_SIZE,
            )
        else:
            raise ValueError(f"Unsupported fetched source: {f.system}")

        per_file[f"{f.source}:{f.path.name}"] = counts.to_dict()
        totals.rows_read += counts.rows_read
        totals.rows_accepted += counts.rows_accepted
        totals.rows_rejected += counts.rows_rejected
        totals.rows_duplicate += counts.rows_duplicate
        for reason, count in counts.rejects_by_reason.items():
            totals.rejects_by_reason[reason] = (
                totals.rejects_by_reason.get(reason, 0) + count
            )
    return per_file, totals, manifests


def _persist_results(conn: Any, etl_run_id: int, results: list[dict[str, Any]]) -> None:
    """Store DQ evidence after a rollback discarded the original audit rows."""
    for item in results:
        conn.execute(
            """
            INSERT INTO project_staging.dq_result
              (etl_run_id,check_id,check_name,severity,table_name,status,observed_value,expected_value,details)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                etl_run_id,
                item["check_id"],
                item["name"],
                item["severity"],
                item["table_name"],
                item["status"],
                str(item["observed_value"]),
                item["expected_value"],
                item["details"],
            ),
        )


def parse_sources(value: str) -> tuple[str, ...]:
    items = [item.strip().lower() for item in value.split(",") if item.strip()]
    if not items:
        raise ValueError("at least one source is required")
    unknown = sorted(set(items) - KNOWN_SOURCES)
    if unknown:
        raise ValueError(f"Unknown sources: {', '.join(unknown)}")
    return tuple(dict.fromkeys(items))


def parse_stations(value: str) -> tuple[str, ...]:
    items = [item.strip().upper() for item in value.split(",") if item.strip()]
    if not items:
        raise ValueError("at least one METAR station is required")
    for station in items:
        if len(station) != 4 or not station.isalnum():
            raise ValueError(f"Invalid METAR station (expected 4-letter ICAO): {station}")
    return tuple(dict.fromkeys(items))


def resolve_window(start: str | None, end: str | None) -> tuple[date, date]:
    if start is None and end is None:
        return recent_window(DEFAULT_WINDOW_DAYS)
    if start is None or end is None:
        raise ValueError("--start and --end must be supplied together")
    try:
        first, last = date.fromisoformat(start), date.fromisoformat(end)
    except ValueError as exc:
        raise ValueError("--start and --end must be ISO dates (YYYY-MM-DD)") from exc
    if last < first:
        raise ValueError("--end must not be before --start")
    return first, last


def check_apply_guard(environ: Mapping[str, str], confirm: str) -> None:
    if (
        environ.get("GITHUB_ACTIONS") != "true"
        or environ.get("WAREHOUSE_CI_APPROVED") != "true"
    ):
        raise ValueError("--apply requires the approved warehouse GitHub Actions job")
    if confirm != APPLY_CONFIRMATION:
        raise ValueError(f"--apply requires --confirm {APPLY_CONFIRMATION}")


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers: Iterable[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    headers = list(headers)
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_cell(value) for value in row) + " |")
    return lines


def _reject_text(counts: Mapping[str, Any]) -> str:
    reasons = counts.get("rejects_by_reason") or {}
    if not reasons:
        return "-"
    return ", ".join(f"{reason}={count}" for reason, count in reasons.items())


def _sum_counts(items: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    total = {"rows_read": 0, "rows_accepted": 0, "rows_rejected": 0,
             "rows_duplicate": 0, "rejects_by_reason": {}}
    for item in items:
        for key in ("rows_read", "rows_accepted", "rows_rejected", "rows_duplicate"):
            total[key] += int(item.get(key, 0))
        for reason, count in (item.get("rejects_by_reason") or {}).items():
            total["rejects_by_reason"][reason] = (
                total["rejects_by_reason"].get(reason, 0) + count
            )
    return total


def render_summary(report: Mapping[str, Any]) -> str:
    window = report["window"]
    lines = [
        "# WP-11 ingestion summary",
        "",
        f"- Status: **{report['status']}**",
        f"- Mode: `{'apply' if report['mode'] == 'apply' else 'validate'}`"
        f" (run_mode `{report['run_mode']}`)",
        f"- Window (UTC): {window[0].isoformat()} to {window[1].isoformat()}",
        f"- Sources requested: {', '.join(report['sources'])}",
        f"- METAR stations: {', '.join(report['stations'])}",
        f"- Code version: {report['code_version']}",
        f"- Generated: {report['generated_at']}",
    ]
    if report.get("run_id") is not None:
        lines.append(f"- ETL run id: {report['run_id']}")
    if report.get("failure_run_id") is not None:
        lines.append(f"- Rollback evidence run id: {report['failure_run_id']}")
    if report.get("note"):
        lines.extend(["", f"> {report['note']}"])
    lines.append("")

    lines.extend(["## Fetched files", ""])
    lines.extend(
        _table(
            ("Source", "System", "File", "Bytes", "URL"),
            [
                (item["source"], item["system"], item["file"], item["bytes"], item["url"])
                for item in report["fetched"]
            ],
        )
    )
    lines.append("")

    if report["mode"] == "validate":
        lines.extend(["## Preview (no database writes)", ""])
        rows = [
            (
                label,
                counts["rows_read"],
                counts["rows_accepted"],
                counts["rows_rejected"],
                _reject_text(counts),
            )
            for label, counts in report["preview"].items()
        ]
        total = _sum_counts(report["preview"].values())
        rows.append(
            (
                "**TOTAL**",
                total["rows_read"],
                total["rows_accepted"],
                total["rows_rejected"],
                _reject_text(total),
            )
        )
        lines.extend(
            _table(("Source file", "Rows read", "Accepted", "Rejected", "Reject reasons"), rows)
        )
        lines.append("")
        lines.append("Validate mode writes nothing. Run the apply job to load these rows.")
    else:
        lines.extend(["## Load results", ""])
        rows = [
            (
                label,
                counts["rows_read"],
                counts["rows_accepted"],
                counts["rows_rejected"],
                counts["rows_duplicate"],
                _reject_text(counts),
            )
            for label, counts in report["loads"].items()
        ]
        total = _sum_counts(report["loads"].values())
        rows.append(
            (
                "**TOTAL**",
                total["rows_read"],
                total["rows_accepted"],
                total["rows_rejected"],
                total["rows_duplicate"],
                _reject_text(total),
            )
        )
        lines.extend(
            _table(
                (
                    "Source file",
                    "Rows read",
                    "Accepted",
                    "Rejected",
                    "Duplicate",
                    "Reject reasons",
                ),
                rows,
            )
        )
        lines.append("")
        lines.append(f"Source manifests recorded: {report['manifests']}")
        lines.append("")
        lines.append(
            "Duplicates are rows already present from an earlier run; they are the"
            " idempotent re-run path, not errors."
        )
        lines.append("")

        lines.extend(["## Dimensions refreshed", ""])
        lines.extend(
            _table(
                ("Dimension", "Rows inserted"),
                sorted(report["dimensions"].items()),
            )
        )
        lines.append("")

        lines.extend(["## Data quality", ""])
        counts = report["dq_summary"]
        lines.append(
            f"PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}"
            f" SKIP={counts['SKIP']}"
        )
        lines.append("")
        lines.extend(
            _table(
                ("Check", "Severity", "Status", "Observed"),
                [
                    (
                        item["check_id"],
                        item["severity"],
                        item["status"],
                        item["observed_value"],
                    )
                    for item in report["dq"]
                ],
            )
        )
        lines.append("")

    lines.extend(["## Accepted limitations after this run", ""])
    dq_status = {item["check_id"]: item["status"] for item in report.get("dq") or []}
    limitation_rows = []
    for lim_id, description, check_id in LIMITATIONS:
        if check_id == "NONE":
            status = "no DQ check"
        else:
            status = dq_status.get(check_id, "not evaluated")
        limitation_rows.append((lim_id, description, check_id, status))
    lines.extend(
        _table(("ID", "Limitation", "Linked check", "Check status"), limitation_rows)
    )
    lines.append("")
    lines.append(
        "A PASS on a linked check proves staging coverage for this run only. It does"
        " not close the limitation while the required work in the accepted-limitations"
        " register is unfinished."
    )
    lines.append("")
    lines.append(
        "Rows accepted = 0 means this run loaded no data for that source. It is"
        " missing coverage, not evidence that the source recorded zero events."
    )
    lines.append("")
    lines.append(
        "Fetched raw files are transient; no object-storage archive is written"
        " (L-010). No raw data is committed to Git."
    )
    return "\n".join(lines) + "\n"


def _safe_message(exc: BaseException) -> str:
    return str(exc).replace("\n", " ").replace("\r", " ")[:300]


def _fetched_rows(files: Iterable[FetchedFile]) -> list[dict[str, Any]]:
    rows = []
    for f in files:
        rows.append(
            {
                "source": f.source,
                "system": f.system,
                "file": f.path.name,
                "bytes": f.path.stat().st_size,
                "url": f.url,
            }
        )
    return rows


def _finish(report: dict[str, Any], args: argparse.Namespace, exit_code: int) -> int:
    text = render_summary(report)
    print(text)
    _emit(text, args)
    return exit_code


def _emit(text: str, args: argparse.Namespace) -> None:
    if args.summary_path:
        Path(args.summary_path).write_text(text, encoding="utf-8")
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as handle:
            handle.write(text + "\n")


def _failure_summary(args: argparse.Namespace, exc: BaseException) -> str:
    return (
        "# WP-11 ingestion failed\n\n"
        f"- Mode: {'apply' if args.apply else 'validate'}\n"
        f"- Sources: {args.sources}\n"
        f"- Stations: {args.stations}\n"
        f"- Error: {type(exc).__name__}: {_safe_message(exc)}\n\n"
        "Nothing partial was kept: an apply transaction is rolled back as a whole,"
        " and validate never writes to the warehouse.\n"
    )


def run(
    args: argparse.Namespace,
    *,
    environ: Mapping[str, str] | None = None,
    fetch: Callable[..., list[FetchedFile]] = fetch_sources,
    connect: Callable[..., Any] | None = None,
) -> int:
    environ = os.environ if environ is None else environ
    sources = parse_sources(args.sources)
    stations = parse_stations(args.stations)
    window = resolve_window(args.start, args.end)
    if args.apply:
        check_apply_guard(environ, args.confirm)

    work = Path(args.work_dir) if args.work_dir else Path(tempfile.mkdtemp(prefix="wp11-"))
    work.mkdir(parents=True, exist_ok=True)
    fetched = fetch(sources, window[0], window[1], work, stations=stations)
    if not fetched:
        raise RuntimeError("No source files were fetched")
    check_licenses(fetched)

    report: dict[str, Any] = {
        "mode": "apply" if args.apply else "validate",
        "run_mode": args.run_mode,
        "status": "VALIDATED",
        "window": window,
        "sources": sources,
        "stations": stations,
        "code_version": CODE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fetched": _fetched_rows(fetched),
        "run_id": None,
        "failure_run_id": None,
        "note": None,
    }

    if not args.apply:
        per_file, totals = preview_sources(fetched)
        check_preview_totals(totals)
        report.update(
            preview=per_file,
            preview_totals={k: v.to_dict() for k, v in totals.items()},
        )
        return _finish(report, args, 0)

    # The persisted DQ coverage checks are table-wide, so historical rows would keep
    # them green after a run that loaded nothing. Fail before the first write instead.
    _pre_file, pre_totals = preview_sources(fetched)
    check_preview_totals(pre_totals)

    database_url = environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from the approved CI environment")
    if connect is None:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Install psycopg[binary] inside CI") from exc
        connect = psycopg.connect

    conn = connect(database_url, connect_timeout=15)
    try:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '20min'")
        run_id = start_etl_run(conn, run_mode=args.run_mode, code_version=CODE_VERSION)
        loads, totals, manifests = apply_files(
            conn,
            fetched,
            etl_run_id=run_id,
            fetched_at=datetime.now(timezone.utc),
        )
        dimensions = refresh_dimensions(conn)
        results = evaluate(conn, run_id, persist=True)
        report.update(
            run_id=run_id,
            loads=loads,
            load_totals=totals.to_dict(),
            manifests=manifests,
            dimensions=dimensions,
            dq=results,
            dq_summary=dq_summary(results),
        )
        failures = [item for item in results if item["status"] == "FAIL"]
        if failures:
            conn.rollback()
            failure_run = start_etl_run(
                conn, run_mode=args.run_mode, code_version=CODE_VERSION
            )
            _persist_results(conn, failure_run, results)
            finish_etl_run(
                conn,
                etl_run_id=failure_run,
                counts=LoadCounts(),
                status="FAILED",
                critical_dq_failures=len(failures),
                failure_reason=(
                    f"WP-11 {args.run_mode} apply rolled back after critical DQ failure"
                ),
            )
            conn.commit()
            report.update(
                status="ROLLED_BACK",
                failure_run_id=failure_run,
                note=(
                    "Critical DQ failure: all ingestion writes were rolled back."
                    " The failure run stores the DQ evidence only."
                ),
            )
            return _finish(report, args, 1)

        finish_etl_run(
            conn,
            etl_run_id=run_id,
            counts=totals,
            status="SUCCESS",
            critical_dq_failures=0,
        )
        conn.commit()
        report["status"] = "SUCCESS"
        return _finish(report, args, 0)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write manifests, staging, dimensions, and DQ from the approved CI job",
    )
    parser.add_argument(
        "--confirm",
        default="",
        help=f"Required with --apply: {APPLY_CONFIRMATION}",
    )
    parser.add_argument(
        "--sources",
        default=",".join(DEFAULT_SOURCES),
        help="Comma-separated: weather, uas, airspace",
    )
    parser.add_argument(
        "--stations",
        default=",".join(DEFAULT_STATIONS),
        help="Comma-separated METAR stations",
    )
    parser.add_argument("--start", help="UTC start date (YYYY-MM-DD); default: 7 days ago")
    parser.add_argument("--end", help="UTC end date (YYYY-MM-DD); default: today")
    parser.add_argument(
        "--run-mode", choices=("initial", "weekly"), default="weekly"
    )
    parser.add_argument("--work-dir", help="Directory for transient fetched files")
    parser.add_argument("--summary-path", help="Write the markdown summary here")
    args = parser.parse_args(argv)
    try:
        return run(args)
    except Exception as exc:
        print(f"WP-11 FAILED: {type(exc).__name__}: {_safe_message(exc)}")
        try:
            _emit(_failure_summary(args, exc), args)
        except OSError:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
