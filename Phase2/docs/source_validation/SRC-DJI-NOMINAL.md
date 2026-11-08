# Source Validation: SRC-DJI-NOMINAL

## Source identity

| Field | Value |
|---|---|
| Source | Nominal-io DJI FlightRecord telemetry |
| URL | `https://huggingface.co/datasets/nominal-io/dji-drone-telemetry` |
| License | MIT (dataset card metadata) |
| Attribution | Cite the `nominal-io/dji-drone-telemetry` dataset card and preserve the MIT notice in the source manifest and reports |
| Fetch time (UTC) | 2026-11-06T20:12Z |
| File name(s) | `colorado-drone-data/FlightRecord_2024-08-02.csv`; `Palos Verdes/DJIFlightRecord_2025-02-17_[17-46-47].csv`; `drone_ocean/FlightRecord_2024-06-29.csv` |
| Size | 3,010,195 bytes; 4,874,707 bytes; 3,606,664 bytes (total 11,491,566 bytes) |
| SHA-256 | Colorado: `ba9cfc0783ff871c7099e243153dd8f23543cf531bf1dfe8ebaddc777c02e39d`; Palos Verdes: `b25b5618fc13506f38f319cd6c779f6871539f2c14f71ab4e46d890f0db7492f`; Offshore: `b64a8ea456da8d97b42e4faa54b083345df799aab2614f478383e927c2cd8abf` |
| Sample/archive | All three CSVs downloaded; no MP4 or other media downloaded. Repository revision `f291777517f3178979f32fa42cb27d0270950500` (last modified 2025-03-25T21:57:50Z). |

The dataset card is minimal and contains only the MIT license declaration. The CSV
schema and units are carried in the column names and were verified against the values.

## Schema

All three files have **189 columns** in the same order except for the timestamp
header: Colorado uses `timestamps`; Palos Verdes and Offshore use `timestamps_ns`.
The latter header is misleading: all three files store Unix epoch **seconds**.

| Source field | Meaning | Type | Unit | Required | Nulls | Notes |
|---|---|---|---|---|---|---|
| `timestamps` / `timestamps_ns` | Observation time | decimal | Unix epoch seconds | yes | 0 | Values around 1.7e9, not nanoseconds. Colorado/Offshore have integer-second resolution; Palos Verdes has 0.1 s resolution |
| `OSD.flyTime [s]` | Flight elapsed time | decimal | s | yes | 0 | 0.1 s increments; reliable sub-second time base |
| `OSD.latitude`, `OSD.longitude` | Position, WGS 84 | decimal | deg | yes | 0 | Colorado has 159 zero-coordinate rows before GPS lock |
| `OSD.height [ft]` | Height above home/takeoff | decimal | ft AGL | yes | 0 | -4.2 to 394.3 ft (Colorado), -0.3 to 393.0 ft (Palos), -8.2 to 202.0 ft (Offshore) |
| `OSD.altitude [ft]` | Altitude above mean sea level | decimal | ft MSL | yes | 0 | 0-5,768 ft (Colorado), 824-1,217 ft (Palos), 26-237 ft (Offshore); Colorado has pre-GPS zeros |
| `OSD.hSpeed [MPH]` | Ground speed | decimal | mph | yes | 0 | Maximum 26.89-27.08 mph; matches `hypot(xSpeed, ySpeed)` within 1e-6 |
| `OSD.xSpeed`, `OSD.ySpeed`, `OSD.zSpeed` | Speed components | decimal | mph | yes | 0 | Horizontal and vertical components |
| `OSD.pitch`, `OSD.roll`, `OSD.yaw` | Attitude | decimal | deg | yes | 0 | Attitude telemetry |
| `OSD.flycState` | Flight state | enum | none | yes | 0 | `Starting Motors`, `Auto Takeoff`, `P-GPS`, `P-GPS (Brake)`, `Go Home`, `Auto Landing`, `Confirm Landing` |
| `OSD.isGPSUsed`, `OSD.isOnGround` | State flags | boolean | none | yes | 0 | Case varies (`TRUE`/`FALSE`, `True`/`False`); normalize |
| `OSD.gpsNum`, `OSD.gpsLevel` | GPS satellite count/level | integer | count | yes | 0 | GPS quality fields |
| `HOME.latitude`, `HOME.longitude` | Home point | decimal | deg | yes | 174 Colorado; 4 others | First valid home row is 174 (Colorado) and 4 (Palos/Offshore) |
| `HOME.height [ft]` | Home/site elevation | decimal | ft MSL | yes | Same as home coordinates | Constant 5,348.2 ft (Colorado), 816.1 ft (Palos), 47.9 ft (Offshore) |
| `RECOVER.aircraftSerial` | Aircraft serial | string | none | yes | 0 | `1581F6Z9C241P003` in all three files; `DETAILS.aircraftSerial` matches |
| `RECOVER.aircraftName` | Aircraft model name | string | none | yes | 0 | `DJI Mini 4 Pro` in all three files |
| `DETAILS.totalTime [s]` | Flight duration | decimal | s | yes | 0 | 278.0, 448.4, and 327.2 s; matches `OSD.flyTime` maximum |
| `DETAILS.totalDistance [ft]` | Flight distance summary | decimal | thousands of feet (kft) | yes | 0 | Header says ft, but the numeric value is scaled by 1,000: 4.4, 13.0, 4.9 mean 4,400, 13,000, 4,900 ft. See caveat below |
| `DETAILS.maxHeight [ft]` | Maximum height | decimal | ft AGL | yes | 0 | 393.7 ft (Colorado), 390.4 ft (Palos), 200.1 ft (Offshore); close to observed maxima |
| `DETAILS.maxHorizontalSpeed [MPH]` | Maximum horizontal speed | decimal | mph | yes | 0 | Matches observed `OSD.hSpeed` maxima |
| `DETAILS.maxVerticalSpeed [MPH]` | Maximum vertical speed | decimal | mph | yes | 0 | 11.18, 12.08, and 10.96 mph |

## Time

- Time base: Unix epoch seconds in the timestamp column, plus `OSD.flyTime [s]` for
  relative elapsed time.
- Absolute or relative: absolute UTC epoch; `OSD.flyTime` is relative.
- Time zone: UTC. File names use the local flight date, so the UTC date can differ:
  - Colorado: `2024-08-03T01:30:54Z` to `2024-08-03T01:35:32Z` (file name
    2024-08-02, local MDT).
  - Palos Verdes: `2025-02-18T01:46:47.52Z` to `2025-02-18T01:54:15.92Z` (file name
    2025-02-17, local PST).
  - Offshore: `2024-06-29T23:44:03Z` to `2024-06-29T23:49:30Z` (file name
    2024-06-29, local PDT).
- Monotonic: Colorado and Offshore are non-decreasing at 1 s resolution; Palos
  Verdes is monotonic at 0.1 s resolution.
- Gaps: Colorado and Offshore maximum 1.0 s; Palos Verdes maximum 22.6 s, with p95
  0.11 s. The Palos gap is a real recording gap, not a timezone jump.
- Duplicate timestamps: Colorado 2,502 rows share a timestamp; Offshore 2,945;
  Palos 0. These are caused by integer-second timestamp resolution, not duplicate
  rows. Exact duplicate rows are **0** in all three files.
- Sampling: Colorado and Offshore are about 10 Hz but only 1 Hz timestamp resolution;
  Palos Verdes is about 9.5 Hz at 0.1 s resolution. Use `OSD.flyTime [s]` to order
  rows within a shared second.
- Invalid time: 0 rows; no 1970 initialization timestamps.
- Flight boundaries:
  - Colorado: `Starting Motors` 01:30:54Z, `Auto Takeoff` 01:30:56Z,
    `Auto Landing` 01:34:57Z, `Confirm Landing` 01:35:29-32Z.
  - Palos Verdes: `Starting Motors` 01:46:47.64Z, `Auto Takeoff` 01:46:49.26Z,
    `Go Home` 01:52:46.02Z, `Auto Landing` 01:53:52.52-01:54:15.92Z.
  - Offshore: `Starting Motors` 23:44:03Z, `Auto Takeoff` 23:44:05Z,
    `Go Home` 23:48:29Z, `Auto Landing` 23:49:00-30Z.

## Coordinates and altitude

- Coordinate system: WGS 84 latitude/longitude.
- Georeferencing method: direct `OSD.latitude`/`OSD.longitude`; no receiver-range
  transform is required.
- Reference check:
  - Colorado home point `39.62655794, -105.0007319`; all valid positions stay
    within **0.269 nm** (about 498 m) of home; median **0.025 nm**.
  - Palos Verdes home point `33.7332532, -118.3346817`; positions stay within
    **0.414 nm** (about 767 m); median **0.247 nm**.
  - Offshore home point `37.62066361, -122.49619`; positions stay within
    **0.168 nm** (about 311 m); median **0.069 nm**.
  - All three tracks are compact local flights with no global jumps.
- Altitude datum: `OSD.height` is feet AGL; `OSD.altitude` is feet MSL;
  `HOME.height` is the home/site elevation. They are not exactly additive:
  `OSD.altitude - OSD.height` has a median of 5,373.6 ft (Colorado), 824.4 ft
  (Palos), and 34.7 ft (Offshore), while `HOME.height` is 5,348.2, 816.1, and
  47.9 ft. Use the recorded field and datum; do not derive AGL by subtracting
  `HOME.height`.
- Altitude unit: feet.
- Plausibility range: all maximum heights are below the 400 ft AGL Part 107 limit
  (394.3, 393.0, and 202.0 ft). Colorado's maximum MSL altitude (5,768 ft) reflects
  the high-elevation site. Minor negative heights (-4.2, -0.3, -8.2 ft) are sensor
  noise near the ground.
- Outliers: Colorado has 159 rows with `OSD.latitude = 0`, `OSD.longitude = 0`,
  `OSD.altitude = 0`, and `OSD.isGPSUsed = FALSE` before GPS lock. Filter those rows
  for spatial and altitude facts. No impossible coordinates or altitude values were
  found.

## Identity

- Vehicle key: `RECOVER.aircraftSerial` (`1581F6Z9C241P003`) is consistent across
  all 10,314 rows and all three files. `DETAILS.aircraftSerial` carries the same
  value.
- Callsign/serial: aircraft name `DJI Mini 4 Pro` (model name), serial
  `1581F6Z9C241P003`.
- Site mapping: the three flights have three distinct home points:
  - Colorado: `39.62655794, -105.0007319`.
  - Palos Verdes: `33.7332532, -118.3346817`.
  - Offshore (San Francisco coast): `37.62066361, -122.49619`.
  The current `dim_site` seed lists only `DJI_CO` and `DJI_CA`; confirm before
  `WP-05` whether `DJI_CA` is a regional site covering both California flights or
  whether a third site code is required.
- Duplicate identity risks: one serial across three flights. Use the serial for
  `dim_vehicle`; use the source file or flight start time for flight-level identity.
  Do not infer three vehicles from three files.

## Volume and capacity

- Rows sampled: 2,781 (Colorado); 4,260 (Palos Verdes); 3,273 (Offshore); total
  **10,314**.
- Valid rows: all 10,314 have valid timestamps; 10,155 have valid non-zero
  coordinates. Colorado has 159 pre-GPS zero-coordinate rows.
- Rejected rows: 159 zero-coordinate rows for spatial/altitude facts; 0 exact
  duplicate rows. Timestamp collisions in Colorado and Offshore require
  deterministic ordering with `OSD.flyTime`.
- Bytes per row: 1,082 (Colorado), 1,144 (Palos), 1,102 (Offshore); about
  **1,100 bytes/row** raw. The warehouse only needs selected fields, so the
  database row is much smaller.
- Estimated full load: 10,314 rows; at 200 bytes/row including indexes, about
  **2.1 MB**; at 500 bytes/row, about **5.2 MB**. Well below the database budget.
- Database estimate: negligible against the 1 GiB limit.
- Object-storage estimate: 11,491,566 bytes (about 11.0 MiB) for the three CSVs.
  Do not download the MP4 files; they are hundreds of megabytes and are not needed.
- Full-load recommendation: load all three CSVs; no media. The same serial means
  the vehicle dimension has one DJI Mini 4 Pro entry and three flights.

## Quality findings

- Completeness: 100% of key fields (`timestamp`, `OSD.flyTime [s]`,
  `OSD.latitude`, `OSD.longitude`, `OSD.height [ft]`, `OSD.altitude [ft]`,
  `OSD.hSpeed [MPH]`, and serial) are populated. Colorado's 159 zero-coordinate
  rows are pre-GPS initialization, not missing columns.
- Accuracy: units are explicit in the headers and were verified from the values.
  `OSD.hSpeed` matches `hypot(xSpeed, ySpeed)` within 1e-6, confirming mph. The
  observed maximum heights and speeds match the `DETAILS` summary fields. The
  `DETAILS.totalDistance` values match the integral of `OSD.hSpeed` after applying
  the 1,000x scale.
- Uniqueness: one serial; no exact duplicate rows. Colorado and Offshore timestamp
  collisions are a resolution artifact; Palos Verdes has no collisions.
- Known limitations:
  - `timestamps_ns` is a misnomer in Palos Verdes and Offshore; values are epoch
    seconds, not nanoseconds. Do not multiply by 1e9 based on the header.
  - Colorado and Offshore timestamps have 1 s resolution; use `OSD.flyTime [s]` for
    sub-second ordering and deduplication.
  - File names use local flight dates; use the epoch timestamp for UTC `dim_time`.
  - Colorado's first 159 rows are pre-GPS zeros; filter them from spatial and
    altitude facts.
  - `DETAILS.totalDistance [ft]` is scaled by 1,000 (kft); do not load the raw
    value as feet.
  - `OSD.altitude - OSD.height` does not exactly equal `HOME.height`; preserve the
    datum and source instead of deriving one from the other.
  - Boolean text case varies (`TRUE/FALSE` vs `True/False`); normalize.
  - The same serial appears in all three flights; flight identity must include the
    source file or start time.
  - Site-code mapping for the two California home points is unresolved; confirm
    before `WP-05`.
  - No video is used or needed.

## Decision

- [x] PASS
- [ ] FAIL
- [ ] PASS WITH LIMITATION

Reason: Nominal-io provides three real DJI flights with absolute epoch-second time,
valid WGS 84 coordinates, explicit altitude and speed units, consistent serial
identity, and a small volume. The timestamp header, 1 s resolution on two flights,
pre-GPS zeros, and the scaled total-distance field are documented and manageable
cleaning rules.

Fallback or human action: none for source validation. Before `WP-05`, confirm the
`dim_site` mapping for the Colorado, Palos Verdes, and Offshore home points.

## Review

- Reviewer: Member D and Member E (pending)
- Date: 2026-11-07
- Evidence links: this record; `Phase2/docs/03_data_sources_and_licensing.md`;
  `Phase2/docs/06_data_quality_and_reports.md`; `Phase2/PROGRESS.md`.
