# AeroGrid Data Sources and Ingestion Strategy

## Status

This document describes the Phase 2 real-data plan. Implementation is authorized
(`H-007`); source validation occurs in `WP-03`. The canonical source list, licenses,
and validation status remain
[`../Phase2/docs/03_data_sources_and_licensing.md`](../Phase2/docs/03_data_sources_and_licensing.md).

## Principles

- **Real public data only.** Never generate synthetic flights, weather, vehicles,
  restrictions, or encounters.
- Raw data is immutable, archived in cloud object storage, and recorded in a
  provenance manifest.
- PostgreSQL contains cleaned staging rows and the curated warehouse, not raw video or
  bulk archives.
- No local PostgreSQL, Docker, or dev containers.
- Refresh is **weekly or manual**, not five-minute polling.
- All five team members read one shared cloud warehouse.
- Free tiers only; no card-gated source or storage.

## Source inventory

| Source | Real data provided | License | Accepted role |
|---|---|---|---|
| TartanAviation KBTP ADS-B | Manned aircraft positions and trajectories | CC BY 4.0 | Primary historical manned source |
| Nightjar PA flights | 10 Hz UAS telemetry | CC BY 4.0 | Real low-altitude UAS source |
| Nominal-io DJI | Three real DJI flight telemetry files | MIT | Real UAS source and parser variety |
| FAA UDDS | Airspace, UAS facility maps, restrictions | Public data | Spatial and restriction context |
| NOAA AWC | Current METAR observations | Public data | Weather context |
| IEM ASOS | Historical METAR observations | Public data | Weather context for historical flights |
| OpenSky REST | Current state vectors | Public data; terms apply | Optional only |

### TartanAviation KBTP

- Source: `https://github.com/castacks/TartanAviation`
- Airport: KBTP, Pittsburgh-Butler Regional.
- Known 2022 archive size: approximately 733 MB raw, 345 MB processed.
- Raw positions use a local/range-bearing frame and require WGS84 georeferencing
  validation before loading.
- Full-archive loading may exceed the 1 GB database budget; use a documented load
  window and archive the full raw file separately.
- Do not assume coordinates are already WGS84.

### Nightjar

- Sources:
  - `https://huggingface.co/datasets/joshruby/nightjar-flight-20260804`
  - `https://huggingface.co/datasets/joshruby/nightjar-flight-20260813`
- Format: CSV and GeoJSON under the `dji/` path.
- `20260804`: 12,447 valid GPS fixes, approximately 20.9 minutes, 10 Hz, site near
  `41.5347, -75.5953`.
- `20260813`: two additional real flights, approximately 7.09 MB and 10.31 MB CSV.
- Do not download audio or video.
- Validate whether timestamps are absolute or relative; do not invent a UTC start.

### Nominal-io DJI

- Source: `https://huggingface.co/datasets/nominal-io/dji-drone-telemetry`
- License: MIT.
- Files: three real flight CSV files.
- Known CSV sizes: Colorado approximately 3,010,195 bytes; Palos Verdes approximately
  4,874,707 bytes.
- Do not download MP4 media.
- Validate timestamp base, altitude datum, units, and serial identity.

### FAA UDDS

- ArcGIS services:
  `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services`
- Layers:
  - `FAA_UAS_FacilityMap_Data_V5`
  - `Part_Time_National_Security_UAS_Flight_Restrictions`
  - `Airspace`
- Format: GeoJSON from ArcGIS REST.
- Query limits are reported around 6,000 request units per minute; paginate and
  cache responsibly.
- A standing UAS facility map ceiling is **not** a TFR.
- Historical TFR coverage is uncertain; if only forward snapshots exist, the reports
  must state that limitation.

### NOAA AWC and IEM ASOS

- Current METAR: `https://aviationweather.gov/api/data/metar`
- Historical ASOS/METAR: IEM ASOS archive.
- No API key is required for the public endpoints used.
- Weather is context, not a substitute for missing flight data.
- Match stations to sites; do not create an observation that does not exist.

### OpenSky

- Current state vectors: `https://opensky-network.org/api/states/all`
- Anonymous access is rate-limited to roughly 400 credits/day.
- Historical Trino access requires a separate application and human acceptance of
  terms.
- OpenSky is optional. Do not make a required deliverable depend on historical access
  that has not been approved.

## Ingestion strategy

### Initial load

1. Human approves the source set and licenses.
2. Fetch or use the archived real source.
3. Record URL, license, fetch time, size, and SHA-256 in the source manifest.
4. Archive the raw file in object storage.
5. Parse a validated sample and estimate capacity.
6. Load only the approved Tartan window and the real UAS/weather/airspace rows.
7. Clean, reject, and stage.
8. Upsert dimensions and map surrogate keys.
9. Load core facts, then derived facts.
10. Run DQ and generate reports.

### Weekly/manual refresh

- Fetch current METAR and FAA snapshots.
- Fetch a new optional OpenSky snapshot only if permitted.
- Add any new UAS flights only if the source is approved and the file is archived.
- Do not poll every five minutes.
- Rebuild affected occupancy/restriction intervals.
- Run DQ and publish reports.

## Storage layers

| Layer | Location | Content |
|---|---|---|
| Raw | Cloud object storage | Original zip/CSV/GeoJSON with manifest |
| Staging | `project_staging` | Cleaned, typed, source-shaped rows; rejects; run log |
| Warehouse | `project_dw` | Dimensions and facts with surrogate keys |
| Reporting | `project_reporting` | Views for team analysis |
| Reports | `Phase2/reports/` or CI artifacts | Data Cleaning and Data Quality PDFs |

## Provenance manifest

Each used source file must record:

- Source name and URL.
- License and attribution.
- Fetch timestamp in UTC.
- Original file name and size.
- SHA-256.
- Storage object key.
- Parser/schema version.
- ETL run ID.

## Capacity assumptions

- PostgreSQL: 1 GB free/project; warn at 700 MB.
- Object storage: 5 GB free/project; warn at 3.5 GB.
- Keep raw JSON/video out of the warehouse.
- Use a documented Tartan load window.
- Precompute occupancy hourly.
- If the budget is at risk, stop and ask the human.

## Data quality expectations

- Reconcile staging read/accepted/rejected/duplicate counts exactly.
- Keep natural keys unique.
- Seed `-1` unknown members.
- Validate coordinates, units, time bases, and altitude datums.
- Never lower a threshold to pass a check.
- Report critical failures instead of hiding them.

## Synthetic legacy files

The files in [`sample/`](sample/README.md) are legacy synthetic demo artifacts
retained intentionally for offline user/evaluator viewing. They are excluded from
Phase 2, are never loaded, cited, or used as extraction evidence, and are not a source.
`.gitignore` intentionally keeps these files tracked; other files under `data/sample/`
remain ignored. See [`../Phase2/DECISIONS.md`](../Phase2/DECISIONS.md) `D-017`.

## Related documents

- [Phase 2 source and licensing plan](../Phase2/docs/03_data_sources_and_licensing.md)
- [Phase 2 architecture](../Phase2/docs/02_architecture_and_platform.md)
- [Phase 2 logical model](../Phase2/docs/04_data_model.md)
- [Phase 2 ETL plan](../Phase2/docs/05_etl_pipeline.md)
- [Phase 2 data dictionary](data_dictionary.md)
- [Phase 2 schema overview](dw_schema.md)
