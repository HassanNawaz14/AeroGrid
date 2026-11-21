# Phase 3 deliverables

Final binary deliverables for Phase 3 live here and in [`../reports/`](../reports/README.md).
They are owned by the work package named below; Member A owns only the packaging
and size guard (`WP-P3-09`), never the content of a BI artifact (`D3-002`).

## Layout

| Path | Contents | Owner |
|---|---|---|
| `AeroGrid_PBIP/` | Power BI project (PBIP) source folder for the dashboard | E (`WP-P3-06`) |
| `AeroGrid_Report/AeroGrid.pbix` or `AeroGrid_Dashboard.pbix` | Power BI dashboard file | E (`WP-P3-06`) |
| `Final_Presentation.pptx` | Final presentation deck | E (`WP-P3-08`) |

The packaging script looks for the `.pbix` in either of the two locations above, so
the final path can be settled by Member E without changing the workflow.

## Size guard (`D3-008`)

- A `.pbix`, PDF or PPTX smaller than 10 MiB is committed.
- A file of 10 MiB or more is **not** committed. It is published as a GitHub Actions
  artifact by the `WP-P3-09 package` workflow (the `oversize` artifact).
- `python Phase3/scripts/package_artifacts.py --dry-run` reports every file, its
  size, its SHA-256 and its route without copying anything.

## Rules

- No secrets, connection strings, raw data or member PII in any file or screenshot.
- Do not hand-edit a generated report. Rebuild it from its evidence.
