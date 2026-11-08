# Source Validation: SRC-METAR-IEM

## Source identity

| Field | Value |
|---|---|
| Source | Iowa Environmental Mesonet (IEM) ASOS/METAR archive |
| URL | `https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py`; download interface: `https://mesonet.agron.iastate.edu/request/download.phtml` |
| License | Public domain. IEM states that the materials on its website are in the public domain and may be used freely for any lawful purpose; attribution to the Iowa Environmental Mesonet of Iowa State University is appreciated. The observations originate from NWS ASOS/AWOS. |
| Attribution | Iowa Environmental Mesonet, Iowa State University; NWS ASOS/AWOS |
| Fetch time (UTC) | 2026-11-07T09:41Z |
| File name(s) | `iem_KBTP_2022-01-01.csv`; `iem_KAGC_2022-01-01.csv`; `iem_KAVP_2026-08-04.csv`; `iem_KAPA_2024-08-03.csv`; `iem_KTOA_2025-02-18.csv`; `iem_KSFO_2024-06-29.csv` |
| Size | KBTP 6,151; KAGC 6,110; KAVP 5,200; KAPA 6,157; KTOA 2,747; KSFO 5,584; total 31,949 bytes |
| SHA-256 | KBTP `24c7b26d76a70325f92e3cb9d2580db0a18f867d39c3401f453020ec5fb24102`; KAGC `da3c9d12d22314df71540ae2041fabb0b439fd090a37d9b54407510a99334b7d`; KAVP `32a73a85ce522874fe9832ae9d421692be7eccde309ce4517061eda0af27a817`; KAPA `e554ac4bd555079f8ba1d1917912df31da159c2b04a5c2a7b4bded6840a33f90`; KTOA `416da0ae941be8711a2262c3fb4c883cee15246ae0b3d6e83eb6a52a0396588c`; KSFO `c12912ffb4ad268ce61cfd0ce6ac8efd0553820d9ebea12bdea0fd7f8b998869` |
| Sample/archive | Six real one-day CSV samples; no full archive downloaded. Samples used `report_type=3` (routine hourly) only; production requests must include both `3` and `4` to include `SPECI`. |

The request used `tz=UTC`, `format=onlycomma`, `latlon=no`, `missing=M`,
`trace=T`, `direct=no`, and station-specific date windows. A follow-up check with
`report_type=3` and `report_type=4` returned KBTP 43 and KAGC 61 rows for
2022-01-01, while KTOA remained at 13 rows for 2025-02-18.

## Schema

| Source field | Meaning | Type | Unit | Required | Nulls | Notes |
|---|---|---|---|---|---|---|
| `station` | Station identifier | string | none | yes | 0 | Three characters in the CSV (`BTP`, `AGC`), even when the request uses `KBTP`/`KAGC` |
| `valid` | Observation time | string | UTC `YYYY-MM-DD HH:MM` | yes | 0 | No `Z` suffix; request `tz=UTC` |
| `lon`, `lat` | Station coordinates | number | deg | yes | 0 | WGS 84; station location, not aircraft position |
| `tmpf` | Air temperature | number | deg F | yes | 0 in samples | Convert to deg C for `dim_weather.temperature_c` |
| `dwpf` | Dew point | number | deg F | yes | 0 in samples | Convert to deg C for `dim_weather.dewpoint_c` |
| `relh` | Relative humidity | number | % | no | some | Not required by the current model |
| `drct` | Wind direction | number | deg true north | yes | a few | `0` with `sknt=0` means calm, not north wind |
| `sknt` | Wind speed | number | kt | yes | a few | Calm is `0` |
| `gust` | Wind gust | number | kt | no | often absent | Store null when `M` or blank |
| `p01i` | One-hour precipitation | number or `T` | inches | no | trace | `T` means trace, not zero |
| `alti` | Altimeter setting | number | inHg | yes | 0 in samples | Already matches `dim_weather.altimeter_inhg` |
| `mslp` | Sea-level pressure | number | hPa (millibar) | no | KTOA all missing | Store null when unavailable |
| `vsby` | Visibility | number | statute miles | yes | 0 in samples | May be `M` for missing |
| `skyc1`-`skyc4` | Sky cover layers | string | none | no | some | `CLR`, `FEW`, `SCT`, `BKN`, `OVC`, `VV `; trim trailing spaces |
| `skyl1`-`skyl4` | Cloud-layer heights | number | ft | no | some | METAR sky heights are AGL; `M` when not applicable |
| `wxcodes` | Present weather codes | string | none | no | often empty | Space-separated METAR weather groups |
| `ice_accretion_1hr`, `ice_accretion_3hr`, `ice_accretion_6hr` | Ice accretion | number | inches | no | often `M` | Optional |
| `peak_wind_gust`, `peak_wind_drct`, `peak_wind_time` | Peak wind remark | number, number, string | kt, deg, time | no | often `M` | Derived from `PK WND` remarks |
| `feel` | Apparent temperature | number | deg F | no | 0 in samples | Wind chill or heat index; not required by the current model |
| `metar` | Raw METAR text | string | none | yes | 0 | Contains the ICAO station and authoritative raw report |
| `snowdepth` | Snow depth | number | inches | no | often `M` | Optional |

The IEM download page documents the variables and units directly. `M` means a
missing value or a value removed by quality control; `T` means trace. Neither value
may be silently converted to zero.

## Time

- Time base: `valid` is a naive UTC timestamp with minute resolution.
- Absolute or relative: absolute.
- Time zone: UTC, requested with `tz=UTC`. The CSV has no `Z` suffix.
- Range:
  - KBTP and KAGC: `2022-01-01 00:53`-`00:56` to `23:53`-`23:56`.
  - KAVP: `2026-08-04 00:54` to `23:54`.
  - KAPA: `2024-08-03 00:53` to `23:53`.
  - KTOA: `2025-02-18 00:47` to `22:49`.
  - KSFO: `2024-06-29 00:56` to `23:56`.
- Monotonic: ascending within every sample file.
- Gaps: routine observations are roughly hourly. KTOA returned only 13 rows over
  22 hours, so its coverage is sparse. AWC may receive `SPECI` reports that are
  absent when only `report_type=3` is requested.
- Duplicate timestamps: 0 duplicate `(station, valid)` pairs in the six samples.
- Report types: request both `report_type=3` (routine/once hourly) and
  `report_type=4` (specials) for parity with AWC.

## Coordinates and altitude

- Coordinate system: WGS 84 station coordinates.
- Georeferencing method: direct station `lat`/`lon` from the response; no aircraft
  track reconstruction.
- Reference check: station coordinates are coherent and match the requested sites.
- Altitude datum: the CSV does not include station elevation. Use station metadata
  or the AWC `elev` field; cloud-layer heights are AGL.
- Altitude unit: feet for `skyl1`-`skyl4`; station elevation is not in this file.
- Plausibility range: all sampled coordinates fall in the expected station areas.
- Outliers: none observed.
- Nearest-station mapping (great-circle distance from the site to the station):
  - KBTP: KBTP 0.3 nm.
  - KAGC: KAGC 0.4 nm.
  - Nightjar PA: KAVP 13.4 nm (KMPO 25.8 nm).
  - DJI Colorado: KAPA 7.8 nm (KBKF 12.4 nm, KDEN 20.7 nm).
  - DJI Palos Verdes: KTOA 4.2 nm (KLGB 10.4 nm, KLAX 13.1 nm).
  - DJI Offshore San Francisco: KSFO 5.8 nm (KSQL 13.4 nm).

## Identity

- Vehicle key: not applicable; this is a station observation source.
- Callsign/serial: not applicable.
- Site mapping: use the nearest station table above. A station can be associated
  with more than one site; preserve the station identity and the site association
  separately.
- Duplicate identity risks: the natural key is `(station, valid)`. `station` is
  three characters in the CSV; use the requested ICAO or parse the raw `metar` to
  recover it. Do not use the station name as a key.
- Coverage caveats: KTOA is sparse; Nightjar's nearest station KAVP is 13.4 nm away,
  so weather representativeness is limited. Do not fabricate an observation for a
  missing hour.

## Volume and capacity

- Rows sampled: 133 routine observations across six station-days.
- Valid rows: 133.
- Rejected rows: 0.
- Bytes per row: 240.2 bytes/row for the raw CSV samples.
- Estimated full load: the initial study windows need fewer than about 1,000 rows
  (Tartan's one-week KBTP/KAGC window plus the DJI/Nightjar flight dates).
- Weekly incremental: six stations at a conservative 60 observations/day is about
  2,520 rows/week; 131,400 rows/year; 657,000 rows over five years.
- Database estimate: at 300-500 bytes/row including indexes, about 0.8-1.3 MB/week
  and 197-329 MB over five years. This is below the 500 MiB target and the 1 GiB
  limit.
- Object-storage estimate: store small station-day CSV snapshots and their hashes;
  the six validation samples total 31,949 bytes. Full-load raw storage is negligible
  compared with the flight archives.
- Full-load recommendation: use IEM for historical source dates and weekly
  backfill; use AWC for recent/weekly cross-checks.

## Quality findings

- Completeness: `station`, `valid`, `lon`, `lat`, `tmpf`, `dwpf`, `drct`, `sknt`,
  `alti`, `vsby`, and `metar` were complete in the six samples. `gust`, `wxcodes`,
  ice accretion, `snowdepth`, and `mslp` are frequently missing. KTOA had no `mslp`
  values at all. `skyl1` is missing when the sky is clear or when only a few layers
  are reported.
- Accuracy: a live cross-check against AWC for 48 common routine observations had
  **0 numeric differences** after converting AWC `temp`/`dewp` from deg C to deg F,
  AWC `altim` from hPa to inHg, and capping AWC `visib='10+'` at 10 statute miles.
  IEM's `valid` matched AWC's actual `obsTime` to the minute.
- Uniqueness: no duplicate `(station, valid)` pairs in the samples.
- Known limitations:
  - `report_type=3` alone omits `SPECI`; request both `3` and `4`.
  - `station` is three characters in the CSV; recover the ICAO from the request or
    the raw `metar`.
  - `valid` has no `Z` suffix; always request `tz=UTC`.
  - `M` is missing and `T` is trace; never coerce either to zero.
  - `drct=0` with `sknt=0` is calm; do not treat it as a north wind.
  - `mslp` can be absent for all rows at a station; use `alti` for altimeter.
  - `skyc1='VV '` includes a trailing space; trim it and treat `VV` as vertical
    visibility.
  - IEM does not provide flight category; derive it from visibility and ceiling
    using documented thresholds, or store null and preserve the raw METAR.
  - Derive `cloud_ceiling_ft` from the lowest `BKN`, `OVC`, or `VV` layer; do not
    copy an arbitrary cloud height.
  - KTOA coverage is sparse; KAVP is 13.4 nm from the Nightjar site. Preserve gaps
    and record the station-to-site distance.
  - The nearest-station fallback set is KMPO for Nightjar, KBKF/KDEN for Colorado,
    KLGB/KLAX for Palos Verdes, and KSQL for Offshore San Francisco; do not use a
    fallback without recording it.

## Decision

- [ ] PASS
- [ ] FAIL
- [x] PASS WITH LIMITATION

Reason: IEM provides real, public-domain historical ASOS/METAR observations for all
source dates, including the Tartan 2022 window. The schema and units are documented,
the samples are internally consistent, and the AWC/IEM cross-check matched 48 common
routine observations with zero numeric differences after unit conversion. The
limitations are station coverage and optional fields: KTOA is sparse, Nightjar's
nearest station is 13.4 nm away, and `report_type` must include both routine and
special reports.

Fallback or human action: none for validation. Record station-to-site distances,
preserve missing/trace values, and use the documented fallback stations only when
needed. Do not invent observations for missing hours.

## Review

- Reviewer: Member D and Member E (pending)
- Date: 2026-11-07
- Evidence links: this record; `Phase2/docs/03_data_sources_and_licensing.md`;
  `Phase2/docs/source_validation/SRC-METAR-AWC.md`; `Phase2/PROGRESS.md`.
