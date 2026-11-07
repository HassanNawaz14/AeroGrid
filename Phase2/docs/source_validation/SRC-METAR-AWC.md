# Source Validation: SRC-METAR-AWC

## Source identity

| Field | Value |
|---|---|
| Source | NOAA Aviation Weather Center (AWC) METAR |
| URL | `https://aviationweather.gov/api/data/metar`; API documentation: `https://aviationweather.gov/data/api/` |
| License | U.S. government open data (NOAA/NWS). Attribution to NOAA/NWS Aviation Weather Center is required in the source manifest and reports. |
| Attribution | NOAA/NWS Aviation Weather Center |
| Fetch time (UTC) | 2026-11-07T09:39Z |
| File name(s) | `awc_kbtp_kagc_24h.json` |
| Size | 43,913 bytes |
| SHA-256 | `8c6b99426281eb6c5de7f9ee32cabbf839cd81f183ded494d7c77a201c62c73e` |
| Sample/archive | Live JSON query `ids=KBTP,KAGC&format=json&hours=24`; 85 records; no full archive downloaded |

The query used a custom `User-Agent` identifying the AeroGrid source-validation
work. AWC returned `application/json; charset=utf-8`. All six study-site stations
were also checked with a one-hour live query and returned data.

## Schema

| Source field | Meaning | Type | Unit | Required | Nulls | Notes |
|---|---|---|---|---|---|---|
| `icaoId` | Station ICAO identifier | string | none | yes | 0 | `KBTP`, `KAGC`, etc. |
| `name` | Station name | string | none | no | 0 | Display metadata; not a key |
| `metarType` | Report type | string | none | yes | 0 | 48 `METAR`, 37 `SPECI` in the sample |
| `obsTime` | Actual observation time | integer | Unix epoch seconds | yes | 0 | Use this for `observation_ts` |
| `reportTime` | Scheduled/report time | string | ISO 8601 UTC | yes | 0 | Rounded to the hour for routine reports; do not use as the observation timestamp |
| `receiptTime` | AWC receipt time | string | ISO 8601 UTC | no | 0 | Ingestion metadata, not observation time |
| `lat`, `lon` | Station coordinates | number | deg | yes | 0 | WGS 84 |
| `elev` | Station elevation | integer | m MSL | yes | 0 | Not AGL |
| `temp` | Air temperature | number | deg C | yes | 0 | May be integer or decimal |
| `dewp` | Dew point | number | deg C | yes | 0 | May be integer or decimal |
| `wdir` | Wind direction | integer or string | deg true north | yes | 0 | `VRB` occurs (1 record in sample); calm is `0` with `wspd=0` |
| `wspd` | Wind speed | integer | kt | yes | 0 | Calm is `0` |
| `wgst` | Wind gust | integer | kt | no | 75 | Usually absent when no gust |
| `visib` | Prevailing visibility | number or string | statute miles | yes | 0 | `10+` occurs (49 records in sample); cap or flag explicitly |
| `altim` | Altimeter setting | number | hPa | yes | 0 | Convert to inHg for `dim_weather.altimeter_inhg` |
| `slp` | Sea-level pressure | number | hPa | no | 37 | Sparse; preserve null |
| `presTend` | Pressure tendency | number | hPa | no | 69 | Sparse; not needed by the current model |
| `cover` | Summary sky cover | string | none | yes | 0 | `CLR`, `FEW`, `SCT`, `BKN`, `OVC` |
| `clouds` | Cloud layers | array of objects | `base` in ft AGL | no | 3 empty lists | Each layer has `cover` and `base`; empty list means no detected layers, not a missing row |
| `fltCat` | Flight category | string | none | yes | 0 | `VFR`, `MVFR`, `IFR`, `LIFR` |
| `rawOb` | Raw METAR/SPECI text | string | none | yes | 0 | Preserve for audit and ICAO identity |
| `qcField` | AWC quality-control flag | integer | none | yes | 0 | Preserve; do not treat as a validation result by itself |

## Time

- Time base: `obsTime` is the actual observation time in Unix epoch seconds.
- Absolute or relative: absolute.
- Time zone: UTC. `reportTime` and `receiptTime` are ISO 8601 UTC strings.
- Range: `2026-11-06T09:53:00Z` to `2026-11-07T08:56:00Z`.
- Monotonic: not in file order. Sort by `icaoId` and `obsTime`.
- Gaps: routine reports are about hourly; `SPECI` reports are irregular. The sample
  has 45 KBTP and 40 KAGC records across 24 hours.
- Duplicate timestamps: 0 duplicate `(icaoId, obsTime)` pairs in the sample.
- Important distinction: `reportTime` is rounded (for example `09:00Z`) while
  `obsTime` is the actual observation (for example `08:56Z`). Use `obsTime` for the
  warehouse observation timestamp.

## Coordinates and altitude

- Coordinate system: WGS 84 latitude/longitude for the reporting station.
- Georeferencing method: direct station coordinates; AWC does not provide aircraft
  tracks.
- Reference check: the six study-site stations returned coherent coordinates and
  elevations in live queries.
- Altitude datum: `elev` is station elevation in metres MSL; it is not AGL.
- Altitude unit: metres.
- Plausibility range: observed elevations were 2 m (KSFO) to 1,791 m (KAPA), which
  are plausible for the study sites.
- Outliers: none observed.

## Identity

- Vehicle key: not applicable; this is a station observation source.
- Callsign/serial: not applicable.
- Site mapping: use the nearest reporting station. The station distances are
  documented in `SRC-METAR-IEM.md`; the AWC station set is the same.
- Duplicate identity risks: the natural key is `(icaoId, obsTime)`. `reportTime` is
  not unique and must not be used as the key. A `METAR` and a `SPECI` can describe
  the same station; preserve `metarType` and `rawOb`.

## Volume and capacity

- Rows sampled: 85.
- Valid rows: 85.
- Rejected rows: 0.
- Bytes per row: 516.6 bytes/row for the raw JSON sample.
- Estimated full load: AWC is for recent/weekly increments only. Query per station
  with `hours=168`; six requests per week stay below the 400-entry response limit
  and the 100-request/minute limit.
- Database estimate: roughly 1,800-2,500 weather rows per week across six stations;
  at 300-500 bytes/row including indexes this is about 1 MB/week and under 50 MB/year.
- Object-storage estimate: store small weekly JSON snapshots and their hashes; well
  under 1 MB/week.
- Historical backfill: use `SRC-METAR-IEM`; AWC retains only the previous 30 days.

## Quality findings

- Completeness: `icaoId`, `obsTime`, `temp`, `dewp`, `wdir`, `wspd`, `visib`,
  `altim`, `cover`, `fltCat`, `rawOb`, `lat`, `lon`, and `elev` were complete in the
  sample. `wgst` was missing in 75 of 85 records, `slp` in 37, and `presTend` in 69.
  Three records had an empty `clouds` list.
- Accuracy: a live cross-check against IEM for 48 common routine observations had
  **0 numeric differences** after converting AWC `temp`/`dewp` from deg C to deg F,
  AWC `altim` from hPa to inHg, and capping `visib='10+'` at 10 statute miles.
- Uniqueness: no duplicate `(icaoId, obsTime)` pairs.
- Known limitations:
  - AWC is a rolling 30-day API, not a historical archive. Use IEM for source dates.
  - Most endpoints return at most 400 entries; split weekly requests by station.
  - Rate limit is 100 requests/minute; set a custom `User-Agent` and back off on
    HTTP `429`.
  - `reportTime` is not the observation time; use `obsTime`.
  - `wdir='VRB'` requires a documented null/sentinel policy; do not coerce it to 0.
  - `visib='10+'` is a floor, not an exact measurement; preserve the raw text and
    store a capped numeric value.
  - `clouds` can be an empty list; `cloud_ceiling_ft` must be derived from the lowest
    `BKN`, `OVC`, or `VV` layer, not from `cover` alone.
  - `slp` and `wgst` are sparse; store null, not zero.
  - `SPECI` records are included; preserve `metarType` and deduplicate on
    `(icaoId, obsTime)`.

## Decision

- [x] PASS
- [ ] FAIL
- [ ] PASS WITH LIMITATION

Reason: AWC is real, public, key-free, and returns complete current/recent METAR
observations for all study-site stations. The schema and units are documented, the
sample is internally consistent, and a live AWC/IEM cross-check matched 48 routine
observations with zero numeric differences after unit conversion. The 30-day
retention and 400-entry cap are acceptable because IEM is the historical source and
weekly AWC requests are split per station.

Fallback or human action: none for validation. Use `SRC-METAR-IEM` for historical
backfill; use AWC for weekly increments and recent cross-checks. If AWC is
unavailable, IEM remains the fallback for current and historical weather.

## Review

- Reviewer: Member D and Member E (pending)
- Date: 2026-11-07
- Evidence links: this record; `Phase2/docs/03_data_sources_and_licensing.md`;
  `Phase2/docs/source_validation/SRC-METAR-IEM.md`; `Phase2/PROGRESS.md`.
