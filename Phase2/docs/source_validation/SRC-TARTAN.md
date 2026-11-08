# Source Validation: SRC-TARTAN

## Source identity

| Field | Value |
|---|---|
| Source | TartanAviation ADS-B (KBTP raw) |
| URL | `https://airlab-cloud.andrew.cmu.edu:8080/swift/v1/AUTH_ac8533a83cff4d48bc8c608ad222d330/tartanaviation-adsb/kbtp/raw/2022.zip` |
| License | CC BY 4.0 (data); BSD-3-Clause (code) |
| Attribution | Cite Patrikar et al., *Scientific Data* 12:468 (2025), DOI `10.1038/s41597-025-04775-6`; cite the TartanAviation dataset |
| Fetch time (UTC) | 2026-11-07T01:04Z |
| File name(s) | `kbtp/raw/2022.zip`; sampled members `01-01-22/1.csv`, `07-31-22/1.csv` |
| Size | Archive 733,388,340 bytes; uncompressed 3,423,961,942 bytes (246 members) |
| SHA-256 | Publisher archive: `668d753a7f105f3026f07faef8ca5426a357256701b387fa970cd4ef6ca63354`; sample `01-01-22/1.csv`: `86342d09e5004102d765b82d04d16b43b6f15f2e7d829bfbde7909187d08a762`; sample `07-31-22/1.csv`: `801c2ef2b6840daae4589c645e228c8a61417fd7bf5d0eee334d72dc293fd326` |
| Sample/archive | Archive metadata inspected by HTTP range reads; two real CSV members extracted. Full archive was not downloaded. |

The official archive checksum is from the publisher
[`croissant.json`](https://raw.githubusercontent.com/castacks/TartanAviation/main/croissant.json)
(SHA-256 `2205ff39d5c970c29ddff799cadda353f96dfb8428b5afff82182641814001bf`).
It was not independently recomputed because the 733 MB archive was inspected by
range requests, not downloaded. The member hashes above were computed from the
extracted real samples.

## Schema

The raw CSV has 13 fields. Units and meanings are confirmed by the publisher
Croissant metadata and by the official `adsb/utils.py` implementation.

| Source field | Meaning | Type | Unit | Required | Nulls | Notes |
|---|---|---|---|---|---|---|
| `ID` | ICAO 24-bit address as an integer | integer | none | yes | 0 in samples | Stable vehicle key for this source |
| `Time` | Python 2 list repr, `[HH, MM, SS.sss]` | string repr | UTC time-of-day (inferred) | yes | 0 in samples | Parse with `ast.literal_eval`; fractional seconds; repeated across messages |
| `Date` | Python 2 list repr, `[YYYY, MM, DD]` | string repr | UTC date (inferred) | yes | 0 in samples | Combine with `Time`; archive folder is the local recording day |
| `Altitude` | Barometric or GNSS altitude, selected by `AltisGNSS` | integer | ft | yes | 0 in samples | Do not assume AGL; 106,600 ft outlier in July sample |
| `Speed` | ADS-B ground speed | integer | kt | no | 752 (2.7%) Jan; 22 (0.2%) July | Missing when not broadcast; values 1-620 kt |
| `Heading` | ADS-B track/heading | integer | deg | no | 752 (2.7%) Jan; 22 (0.2%) July | Missing with `Speed`; values 0-359 deg |
| `Lat` | Latitude, WGS 84 | decimal | deg | yes | 0 in samples | 39.61-41.72 in Jan sample |
| `Lon` | Longitude, WGS 84 | decimal | deg | yes | 0 in samples | -81.61 to -77.78 in Jan sample |
| `Age` | Source-defined message/position age | decimal | s | yes | 0 in samples | 0.62-59.98 s; not an event timestamp |
| `Range` | Geodesic distance from receiver | decimal | km | yes | 0 in samples | Confirmed: `g['s12']/1000.0` in `adsb/utils.py` |
| `Bearing` | Initial bearing from receiver | decimal | deg | yes | 0 in samples | Signed -180..180; confirmed: `g['azi1']` |
| `Tail` | Broadcast callsign: N-number for most GA, flight number for airlines | string | none | no | 79 (0.3%) Jan; 396 (3.9%) July | 249 unique values in Jan; not a stable vehicle key |
| `AltisGNSS` | Altitude-source flag | boolean | none | yes | 0 in samples | 27,479 `False` in Jan; 10,233 `False` + 2 `True` in July; publisher metadata does not define the flag |

## Time

- Time base: `Date` + `Time`, parsed as a naive datetime.
- Absolute or relative: absolute.
- Time zone: UTC (inferred). The publisher metadata does not state a timezone. The
  official `adsb/process.py` labels the parsed timestamp `utc` and compares it with
  IEM METAR `valid` times, which are UTC.
- Range: sample Jan file `2022-01-01T08:09:40.645667Z` to
  `2022-01-02T03:59:47.443000Z`; sample July file
  `2022-07-31T06:00:04Z` to `2022-07-31T07:50:45Z`.
- Monotonic: not guaranteed per file. Sort by `ID` and parsed timestamp before use.
- Gaps: tracks contain gaps of tens of seconds; long gaps separate flights. The
  official processing resamples to 1 Hz and interpolates up to 60 s, then segments
  on gaps greater than 1 s.
- Duplicate timestamps: severe. The Jan sample has 27,479 parsed rows but only 11,168
  unique timestamps; the July sample has 10,235 parsed rows and 4,259 unique
  timestamps. `Time` repeats across multiple messages, sometimes with different
  positions. Do not treat every raw row as a unique event.
- Exact duplicates: 5,536 rows in Jan (same `ID`, timestamp, lat, lon, altitude);
  2,981 in July. Remove exact duplicates before staging.

## Coordinates and altitude

- Coordinate system: WGS 84 latitude/longitude.
- Georeferencing method: the publisher computes `Range` and `Bearing` from the
  receiver reference `(40.777888, -79.949864)` using GeographicLib WGS 84. The raw
  `Range` is kilometres and `Bearing` is the signed initial azimuth.
- Reference check: reconstructing a destination from KBTP using
  `Range / 1.852` nm and `(Bearing + 360) % 360` matches the recorded `Lat`/`Lon`
  with median error **0.027 nm** (about 50 m), p95 **0.062 nm** (about 115 m), and
  maximum **0.268 nm** (about 496 m) in the Jan sample. July: median **0.029 nm**,
  p95 **0.090 nm**, maximum **0.126 nm**. Bearing error is median **0.080 deg**,
  p95 **0.110 deg** (Jan) and median **0.076 deg**, p95 **0.110 deg** (July).
- Altitude datum: `Altitude` is in feet. `AltisGNSS` selects the altitude source;
  the publisher metadata does not define which value means barometric versus GNSS.
  The sample is overwhelmingly `False`, so treat it as barometric/pressure altitude
  until the flag is confirmed. Never label it AGL.
- Altitude unit: feet.
- Plausibility range: Jan 1,375-43,025 ft; July 997-106,600 ft. The 106,600 ft value
  is an outlier and must be rejected or flagged by a documented range rule.
- Outliers: the 106,600 ft altitude is outside a plausible conventional-aircraft
  range. Speed is 1-620 kt and heading 0-359 deg. Do not infer a clean trajectory
  from raw rows without deduplication and time ordering.

## Identity

- Vehicle key: `ID` (ICAO 24-bit address as an integer). It is stable within the
  sample and is the only suitable natural vehicle key.
- Callsign/serial: `Tail` is the broadcast callsign. For general aviation it is
  usually the N-number; for airlines it is the flight number.
- Site mapping: archive prefix `kbtp`; receiver reference
  `(40.777888, -79.949864)`. KAGC is not validated by this record.
- Duplicate identity risks: the Jan sample has 155 `ID` values and 249 `Tail`
  values; 84 `ID` values carry more than one `Tail`, while no `Tail` maps to more
  than one `ID`. `Tail` is mutable and must not be used as the vehicle key. Map
  `ID` to `dim_vehicle` with `source_system = 'SRC-TARTAN'`; keep `Tail` as a
  callsign/attribute and preserve the last observed value with its timestamp.

## Volume and capacity

- Rows sampled: 27,688 in `01-01-22/1.csv`; 10,287 in `07-31-22/1.csv`.
- Valid rows: 27,479 parsed in Jan; 10,235 in July. Blank rows: 208 Jan (0.75%),
  52 July (0.51%). Wrong-field/truncated rows: 1 Jan, 0 July.
- Rejected rows: 209 Jan (208 blank + 1 truncated); 52 July.
- Bytes per row: 156.2 bytes/row (Jan); 143.6 bytes/row (July). Use ~156 bytes/row
  for raw-size estimates.
- Full 2022 archive: 3,423,961,942 uncompressed bytes; estimated **~22.0 million**
  raw rows. The archive covers months 01-10 and 246 members; the full year is too
  large for the 1 GiB database.
- Proposed load window: **2022-01-01 through 2022-01-07 UTC** (7 daily files;
  95,055,872 uncompressed bytes; estimated **~609,000 rows**). This is the
  recommended initial load window.
- One-month reference: January 2022 is 394,731,800 uncompressed bytes and
  ~2,530,000 rows. At a conservative 200 bytes/row including indexes, that is
  ~506 MB, at the 500 MiB target and too close to the 1 GiB limit. Use the
  one-week window for the initial load.
- Estimated database cost: one week at 200 bytes/row is ~122 MB; one month is
  ~506 MB; the full year is ~4.4 GB and exceeds the 1 GiB database limit.
- Object-storage estimate: 733,388,340 bytes compressed (~699 MiB) for the full
  KBTP 2022 archive. This is below the 2 GiB target and the 5 GiB bucket limit.
  Archive the full source archive; load only the documented window.
- Full-load recommendation: archive `kbtp/raw/2022.zip` in `aerogrid-raw`; load
  only the one-week window above. The estimate is below the 500 MiB target and
  leaves room for the other sources.

## Quality findings

- Completeness: 99.2% of Jan rows are parseable after removing blank rows; 99.5%
  in July. `Speed` and `Heading` are missing together in 2.7% of Jan rows and 0.2%
  of July rows. `Tail` is missing in 0.3% of Jan rows and 3.9% of July rows.
- Accuracy: georeferencing passes against the KBTP receiver reference; median
  error is about 50 m and p95 is about 115 m. Range is kilometres; bearing is
  signed degrees. Altitude is feet and includes at least one impossible outlier.
- Uniqueness: exact duplicate rows are 20.1% of parsed Jan rows and 29.1% of parsed
  July rows. Repeated timestamps make naive speed derivation unreliable. Dedupe
  exact rows, resample to 1 Hz per `ID`, and do not use `Speed`/`Heading` as
  authoritative unless they survive the documented cleaning rules.
- Known limitations:
  - UTC is inferred from the official processing code, not stated in the raw
    header. Preserve the raw `Date`/`Time` strings and validate the UTC assumption
    against IEM METAR during staging.
  - `Time` repeats across messages; raw row order is not a reliable event order.
  - `AltisGNSS` semantics are not documented by the publisher. Preserve the flag
    and record `altitude_source`; do not claim AGL.
  - Full-year volume exceeds the database budget. The one-week window is required.
  - The 106,600 ft altitude outlier must be rejected or flagged.

## Decision

- [x] PASS
- [ ] FAIL
- [ ] PASS WITH LIMITATION

Reason: TartanAviation is accepted. Georeferencing is validated against the KBTP
receiver reference; units and schema are confirmed by the publisher metadata and
official code; the source is real, public, and CC BY 4.0. The documented
limitations are handled by deduplication, a one-week load window, altitude range
checks, and preserving the raw timestamp and `AltisGNSS` flag.

Fallback or human action: none for validation. The one-week load window is
recommended for approval before `WP-04`.

## Review

- Reviewer: Member D and Member E (pending)
- Date: 2026-11-07
- Evidence links: this record; `Phase2/docs/03_data_sources_and_licensing.md`;
  `Phase2/docs/06_data_quality_and_reports.md`; `Phase2/PROGRESS.md`.
