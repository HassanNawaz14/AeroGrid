# Source Validation: SRC-NIGHTJAR

## Source identity

| Field | Value |
|---|---|
| Source | Nightjar DJI FlightRecord telemetry |
| URL | `https://huggingface.co/datasets/joshruby/nightjar-flight-20260804` |
| License | CC BY 4.0 |
| Attribution | Cite the `joshruby/nightjar-flight-20260804` dataset card and preserve attribution in the source manifest and reports |
| Fetch time (UTC) | 2026-11-07T01:07Z |
| File name(s) | `dji/FlightRecord_2026-08-04_[12-46-25].csv` |
| Size | 9,855,064 bytes |
| SHA-256 | `6ef49014ee85104c06f1b7fee743c71a0a06a4ba76b06e84fcde15f5091004d2` |
| Sample/archive | Full CSV downloaded; no audio, video, blackbox, or media downloaded. Repository revision `f19296dbd17b6eb454402ef6b8a05a6527648eb9` (last modified 2026-08-16T16:49:13Z). |

The repository has `dji/*.csv` and `dji/*.txt`, but no `dji/*.geojson`. The CSV is
sufficient for validation; the absence of GeoJSON is a source-fact discrepancy to
carry into staging.

## Schema

The CSV has **119 columns**. Key fields for the warehouse are listed below; the full
column set is preserved in the raw file.

| Source field | Meaning | Type | Unit | Required | Nulls | Notes |
|---|---|---|---|---|---|---|
| `CUSTOM.dateTime` | UTC observation time | ISO 8601 string | UTC | yes | 0 | One row is `1970-01-01T00:00:00Z`; filter it |
| `OSD.flyTime` | Flight elapsed time | decimal | s | yes | 0 | 0.1 s increments |
| `OSD.latitude` | Latitude, WGS 84 | decimal | deg | yes | 0 | 12,448 valid coordinate rows |
| `OSD.longitude` | Longitude, WGS 84 | decimal | deg | yes | 0 | Same |
| `OSD.height` | Height above home/takeoff | decimal | ft AGL | yes | 0 | -0.5 to 276.3 ft; matches `DETAILS.maxHeight` 276.0 |
| `OSD.heightMax` | Maximum height | decimal | ft AGL | yes | 0 | Summary field |
| `OSD.vpsHeight` | Vision-positioning height | decimal | ft | yes | 0 | 0.1-13.1 ft; low-altitude aid only |
| `OSD.altitude` | Altitude above mean sea level | decimal | ft MSL | yes | 0 | 0-705.73 ft; equals `OSD.height + HOME.altitude` after home initialization |
| `OSD.xSpeed`, `OSD.ySpeed`, `OSD.zSpeed` | Ground/vertical speed components | decimal | m/s | yes | 0 | Horizontal max 10.52 m/s; vertical max 3.3 m/s |
| `OSD.pitch`, `OSD.roll`, `OSD.yaw` | Attitude | decimal | deg | yes | 0 | Attitude telemetry |
| `OSD.flycState` | Flight state | enum | none | yes | 0 | `EngineStart`, `AutoTakeoff`, `GPSAtti`, `GoHome`, `AutoLanding`, `ConfirmLanding` |
| `OSD.isOnGround`, `OSD.isMotorOn`, `OSD.isGPSUsed` | State flags | boolean | none | yes | 0 | `isGPSUsed` true for all rows |
| `OSD.gpsNum`, `OSD.gpsLevel` | GPS satellite count/level | integer | count | yes | 0 | GPS quality fields |
| `BATTERY.chargeLevel`, `BATTERY.voltage`, `BATTERY.current` | Battery telemetry | decimal | %, V, A | yes | 0 | Preserve if battery facts are added |
| `HOME.latitude`, `HOME.longitude`, `HOME.altitude` | Home point and site elevation | decimal | deg, deg, ft MSL | yes | 7 zero rows during initialization | Home altitude 429.43 ft MSL |
| `RECOVER.aircraftSerial` | Aircraft serial | string | none | yes | 0 | `5FSCK1601121D7` |
| `RECOVER.aircraftName` | Aircraft name | string | none | yes | 0 | `Amanda` |
| `DETAILS.totalTime` | Flight duration | decimal | s | yes | 0 | 1,252.1 s |
| `DETAILS.totalDistance` | Flight distance | decimal | km | yes | 0 | 3.021 km; consistent with speed integral |
| `DETAILS.maxHeight` | Maximum height | decimal | ft AGL | yes | 0 | 276.0 ft |
| `DETAILS.maxHorizontalSpeed` | Maximum horizontal speed | decimal | m/s | yes | 0 | 10.520931 m/s |
| `DETAILS.maxVerticalSpeed` | Maximum vertical speed | decimal | m/s | yes | 0 | 3.3 m/s |

## Time

- Time base: `CUSTOM.dateTime` ISO 8601, absolute UTC.
- Absolute or relative: absolute.
- Time zone: UTC (`Z` suffix).
- Range: `2026-08-04T16:46:25.242Z` to `2026-08-04T17:07:17.257Z`.
- Duration: 20.87 min (1,252.1 s), matching `DETAILS.totalTime`.
- Monotonic: mostly monotonic; 758 duplicate timestamps occur. No exact duplicate
  rows were found.
- Sampling: median 0.106 s, p95 0.11 s, maximum 0.23 s; 12,448 rows over 20.87 min
  is about 9.94 Hz. The 10 Hz claim is confirmed.
- Gaps: no large gaps; the maximum observed gap is 0.23 s.
- Invalid time: 1 row at `1970-01-01T00:00:00Z` (pre-takeoff initialization).
- Duplicate timestamps: 758 rows share a timestamp with another row; sort and
  deduplicate on the source key and do not assume strict ordering within a timestamp.
- Flight boundaries: `EngineStart` 16:46:25.242Z; `AutoTakeoff` 16:46:26.289Z;
  `GPSAtti` 16:46:27.778Z; `GoHome` 17:03:04.481Z; `AutoLanding` 17:05:30.640Z;
  `ConfirmLanding` 17:07:14.705Z to 17:07:17.257Z.

## Coordinates and altitude

- Coordinate system: WGS 84 latitude/longitude.
- Georeferencing method: direct `OSD.latitude`/`OSD.longitude`; no receiver-range
  transform is required.
- Reference check: the documented site is approximately `41.5347, -75.5953`. The
  sample stays within **0.231 nm** (about 428 m) of that point; median distance is
  **0.0255 nm** (about 47 m). The home point is
  `41.534724580924255, -75.59528016176647`.
- Altitude datum: `OSD.height` is feet AGL; `OSD.altitude` is feet MSL once the home
  altitude is initialized. The difference is `429.43 ft`, matching
  `HOME.altitude` 429.42978 ft MSL (the site elevation). The first 7 rows have
  `HOME.altitude = 0` and `OSD.altitude = 0`; do not interpret those zeros as MSL.
- Altitude unit: feet.
- Plausibility range: `OSD.height` -0.5 to 276.3 ft AGL; `OSD.altitude` 0 to 705.73
  ft MSL. The maximum height is below the 400 ft AGL Part 107 limit.
- Outliers: the -0.5 ft height is minor sensor noise; the 1970 timestamp is the only
  invalid time. No impossible coordinates were found.

## Identity

- Vehicle key: `RECOVER.aircraftSerial` (`5FSCK1601121D7`), consistent across all
  12,448 rows. `DETAILS.aircraftSerial` carries the same value.
- Callsign/serial: aircraft name `Amanda`; serial `5FSCK1601121D7`.
- Site mapping: a separate `dim_site` near `41.5347, -75.5953`, not KBTP. Home point
  is `41.53472, -75.59528`.
- Duplicate identity risks: one flight and one serial in this file; the 20260813
  candidate dataset is a separate flight and is not validated by this record.

## Volume and capacity

- Rows sampled: 12,448.
- Valid rows: 12,447 with valid timestamps; 12,448 with valid coordinates. One row
  has the 1970 initialization timestamp.
- Rejected rows: 1 invalid timestamp; no exact duplicate rows.
- Bytes per row: 791.7 bytes/row raw (119 columns). The warehouse only needs the
  key fields, so the database row is much smaller.
- Estimated full load: 12,447 rows; at 200 bytes/row including indexes, about
  **2.5 MB**; at 500 bytes/row, about **6.2 MB**. Well below the database budget.
- Database estimate: negligible against the 1 GiB limit.
- Object-storage estimate: 9,855,064 bytes (about 9.4 MiB) for the CSV. Media files
  are much larger and are not required.
- Full-load recommendation: load the CSV only; do not download audio, video,
  blackbox, or media. The optional 20260813 flight is a separate small CSV if it is
  later approved.

## Quality findings

- Completeness: 100% of key fields (`CUSTOM.dateTime`, `OSD.latitude`,
  `OSD.longitude`, `OSD.height`, `OSD.altitude`, speeds, serial) are populated in
  every row. One timestamp is the 1970 initialization value.
- Accuracy: coordinates match the documented site; altitude datum and units are
  confirmed; speeds are m/s and are consistent with `DETAILS.totalDistance` 3.021 km
  and the integrated path. The maximum height and speeds match the summary fields.
- Uniqueness: one aircraft serial; no exact duplicate rows. 758 duplicate timestamps
  require deterministic ordering/deduplication.
- Known limitations:
  - One 1970 timestamp row must be rejected.
  - Duplicate timestamps exist; do not assume a unique timestamp key.
  - `OSD.altitude` is 0 before the home altitude is initialized; filter by
    `HOME.altitude > 0` or use `OSD.height` for AGL.
  - No GeoJSON is present in the repository; the CSV is the authoritative telemetry.
  - Only the 20260804 flight is validated; the 20260813 candidate is separate.
  - The dataset is a single UAS at a non-KBTP site; do not pair it with unrelated
    Tartan/OpenSky traffic for close encounters.

## Decision

- [x] PASS
- [ ] FAIL
- [ ] PASS WITH LIMITATION

Reason: Nightjar provides real, absolute UTC, 10 Hz DJI telemetry with valid WGS 84
coordinates, confirmed AGL/MSL altitude datums, consistent serial identity, and a
small volume. The only cleaning needs are the 1970 initialization row, duplicate
timestamp handling, and treating pre-initialization `OSD.altitude` zeros as missing.

Fallback or human action: none for validation. The 20260813 flight remains optional
and is not part of this PASS.

## Review

- Reviewer: Member D and Member E (pending)
- Date: 2026-11-07
- Evidence links: this record; `Phase2/docs/03_data_sources_and_licensing.md`;
  `Phase2/docs/06_data_quality_and_reports.md`; `Phase2/PROGRESS.md`.
