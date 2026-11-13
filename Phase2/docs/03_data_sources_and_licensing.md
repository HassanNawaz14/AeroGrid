# Data Sources and Licensing

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Source policy

- Use real, public data only.
- Every source must have a documented URL, license or terms, access method, fetch
  cadence, expected schema, and provenance hash.
- Never substitute synthetic data for a missing source.
- Never commit raw source archives to Git.
- Record attribution in the source manifest and the generated reports.
- If a license or redistribution term is unclear, stop and ask the human.
- Source decisions were confirmed at `G1` (`H-006`, `D-011`-`D-013`); a source is not
  final until the `WP-03` validation spike passes at `G2`.

## Source inventory

| ID | Source | Role | Access | Cadence | License/terms | Status |
|---|---|---|---|---|---|---|
| `SRC-TARTAN` | TartanAviation ADS-B | Primary historical manned tracking, journeys, encounters, occupancy | Public HTTPS/Swift download | Initial bulk; static | CC BY 4.0 | Validated 2026-11-07; see `source_validation/SRC-TARTAN.md` |
| `SRC-NIGHTJAR` | Nightjar DJI flight telemetry | Real UAS tracking and journeys, 10 Hz | Public Hugging Face files | Initial bulk | CC BY 4.0 | Validated 2026-11-07; see `source_validation/SRC-NIGHTJAR.md` |
| `SRC-DJI-NOMINAL` | Nominal-io DJI telemetry | Additional real UAS tracking and journeys | Public Hugging Face files | Initial bulk | MIT | Validated 2026-11-07; see `source_validation/SRC-DJI-NOMINAL.md` |
| `SRC-METAR-AWC` | NOAA Aviation Weather Center METAR | Current and recent weather observations | Public HTTP JSON | Weekly | U.S. government open data; NOAA/NWS attribution | Validated 2026-11-07; recent/weekly only; see `source_validation/SRC-METAR-AWC.md` |
| `SRC-METAR-IEM` | Iowa Environmental Mesonet ASOS | Historical METAR for source dates | Public HTTP CSV | Initial + weekly backfill | Public domain; IEM attribution appreciated | Validated 2026-11-07; see `source_validation/SRC-METAR-IEM.md` |
| `SRC-FAA-UDDS` | FAA UDDS ArcGIS layers | UAS facility map, TFRs, airspace zones | Public ArcGIS REST GeoJSON | Initial + weekly | U.S. government open data | Validated 2026-11-07; granular airspace services approved (`D-020`); see `source_validation/SRC-FAA-UDDS.md` |
| `SRC-OPENSKY` | OpenSky Network REST | Optional recent manned snapshots | Public API; optional account | Weekly/manual | OpenSky terms; no raw redistribution | Optional |
| `SRC-OPENSKY-TRINO` | OpenSky historical database | Optional historical enrichment | Application required | Optional | Separate data-use terms | Not assumed |

## SRC-TARTAN: TartanAviation ADS-B

### What it provides

Real ADS-B aircraft trajectories recorded at two Pittsburgh-area airports:

- KAGC: Allegheny County Airport.
- KBTP: Pittsburgh-Butler Regional Airport.

The dataset covers 661 days, with raw and processed ADS-B archives. It is the primary
source for manned tracking, journey segmentation, close-encounter detection, and
occupancy.

### Access

- Repository: <https://github.com/castacks/TartanAviation>
- ADS-B download script: `adsb/download.py`
- Public Swift endpoint:
  `https://airlab-cloud.andrew.cmu.edu:8080/swift/v1/AUTH_ac8533a83cff4d48bc8c608ad222d330/tartanaviation-adsb`
- Bucket: `tartanaviation-adsb`
- Sample option: `kbtp/raw/2022` (one year of raw KBTP data)
- KBTP raw 2022 archive: approximately **733 MB**
- KBTP processed archive: approximately **345 MB**
- Full ADS-B archive: approximately **2 GB compressed / 12 GB uncompressed**

### Fields and caveats

- Raw records have 13 fields: `ID` (ICAO 24-bit address as an integer), `Time` and
  `Date` (Python 2 list representations), `Altitude` (ft), `Speed` (kt), `Heading`
  (deg), `Lat`/`Lon` (WGS 84), `Age` (s), `Range` (km from the receiver), `Bearing`
  (deg, signed), `Tail` (broadcast callsign), and `AltisGNSS` (altitude-source flag).
- Units and meanings are confirmed by the publisher `croissant.json` metadata and
  the official `adsb/utils.py` implementation. `Range` is computed as
  `g['s12'] / 1000.0` and `Bearing` as `g['azi1']` from the receiver reference.
- Processed records use a local runway frame: `Frame`, `ID`, `x`, `y`, `z`,
  `Headwind`, and `Crosswind`.
- Raw positions are already WGS 84 latitude/longitude; `Range` and `Bearing` are
  derived from the KBTP receiver reference `40.777888, -79.949864`. Validation in
  `WP-03` reconstructed the destination from range/bearing and matched the recorded
  latitude/longitude within about 50 m median.
- `ID` is the stable vehicle key. `Tail` is a mutable broadcast callsign and must
  not be used as a unique vehicle key.
- Raw `Date`/`Time` are interpreted as UTC by the official processing code; the raw
  header does not state a timezone. Preserve the raw timestamp and validate the UTC
  assumption during staging.
- `Time` repeats across messages and exact duplicate rows occur. Deduplicate and
  resample before deriving speed or trajectories.
- `Altitude` is feet and is not AGL. `AltisGNSS` selects the altitude source; the
  publisher metadata does not define the flag's semantics, so preserve it and
  record the source. Range-check altitude and reject impossible outliers.
- Processed local coordinates must not be presented as latitude/longitude.
- KAGC georeferencing is not yet validated; use KAGC for weather/airspace context
  unless `WP-03` proves the coordinate transform.
- Archive the raw source and preserve the download timestamp and SHA-256.
- `WP-03` recommends a documented initial load window of 2022-01-01 through
  2022-01-07 UTC (about 609,000 rows, 95 MB uncompressed). The full 2022 archive is
  about 22 million rows and must not be loaded wholesale. See
  [source_validation/SRC-TARTAN.md](source_validation/SRC-TARTAN.md).

### License and attribution

Data is CC BY 4.0. Cite the TartanAviation paper and dataset in the repository
documentation and generated reports. Code is BSD-3-Clause; do not copy code without
preserving its license notice.

## SRC-NIGHTJAR: Nightjar DJI flight telemetry

### What it provides

Real DJI FlightRecord data from instrumented field flights at a Pennsylvania site:

- Primary candidate: `joshruby/nightjar-flight-20260804`
- Additional candidate: `joshruby/nightjar-flight-20260813`
- `20260804`: 12,448 CSV rows, 12,447 valid timestamps, 12,448 valid coordinate
  rows, about 9.94 Hz, 20.87 minutes.
- Site coordinates: approximately `41.5347, -75.5953`; home altitude 429.43 ft MSL.
- Useful fields: `CUSTOM.dateTime` (UTC), `OSD.latitude`, `OSD.longitude`,
  `OSD.height` (feet AGL), `OSD.altitude` (feet MSL after home initialization),
  `OSD.xSpeed`/`OSD.ySpeed`/`OSD.zSpeed` (m/s), battery, flight state, and
  `RECOVER.aircraftSerial`.
- `WP-03` validated the 20260804 CSV: coordinates stay within 0.231 nm of the site,
  altitude datums are confirmed, speeds are m/s, and the serial is consistent. See
  [source_validation/SRC-NIGHTJAR.md](source_validation/SRC-NIGHTJAR.md).

### Access

- Dataset card:
  <https://huggingface.co/datasets/joshruby/nightjar-flight-20260804>
- Additional flight:
  <https://huggingface.co/datasets/joshruby/nightjar-flight-20260813>
- Download only `dji/*.csv` and `dji/*.geojson`. Do not download audio or video.
- No token or card is required.

### Fields and caveats

- CSV column names vary across DJI firmware and exports. The 20260804 file has 119
  columns.
- The first row has `CUSTOM.dateTime = 1970-01-01T00:00:00Z`; reject it.
- `OSD.altitude` is 0 until `HOME.altitude` is initialized. After initialization it
  is MSL and equals `OSD.height + HOME.altitude`. Do not interpret the initial zero
  as MSL.
- Duplicate timestamps occur (758 in the 20260804 sample) even though no exact
  duplicate rows were found. Sort deterministically and deduplicate.
- The repository contains `dji/*.csv` and `dji/*.txt` but no `dji/*.geojson`; the
  CSV is the authoritative telemetry.
- The site is not KBTP. It is a separate `dim_site`.
- Do not pair this UAS with unrelated OpenSky/Tartan traffic for close encounters.

### License and attribution

CC BY 4.0. Cite the dataset card and preserve attribution in the source manifest and
reports.

## SRC-DJI-NOMINAL: Nominal-io DJI telemetry

### What it provides

Real DJI FlightRecord CSVs from three flights:

- Colorado: `colorado-drone-data/FlightRecord_2024-08-02.csv` (approximately 3 MB).
- Palos Verdes: `Palos Verdes/DJIFlightRecord_2025-02-17_[17-46-47].csv`
  (approximately 4.9 MB).
- Offshore: `drone_ocean/FlightRecord_2024-06-29.csv` (approximately 3.6 MB).

Use CSV files only. Do not download the large MP4 files.

### Access

- Dataset card: <https://huggingface.co/datasets/nominal-io/dji-drone-telemetry>
- No token or card is required.

### Fields and caveats

- All three files have 189 columns in the same order except the timestamp header:
  Colorado uses `timestamps`; Palos Verdes and Offshore use `timestamps_ns`.
- The `timestamps_ns` header is misleading. All three files store Unix epoch
  **seconds** (values around 1.7e9), not nanoseconds. Colorado and Offshore have
  integer-second resolution; Palos Verdes has 0.1 s resolution.
- Use `OSD.flyTime [s]` for sub-second ordering, especially on Colorado and Offshore
  where about ten rows share each integer timestamp.
- File names use the local flight date, not the UTC date. Use the epoch timestamp
  for `dim_time`.
- `OSD.latitude`/`OSD.longitude` can be zero before GPS lock. Colorado has 159 such
  rows; filter them from spatial and altitude facts.
- `OSD.height` is feet AGL; `OSD.altitude` is feet MSL; `HOME.height` is the home
  site elevation. Do not derive AGL by subtracting `HOME.height`; the offset is not
  exact.
- Speed fields are explicit: `OSD.hSpeed` and `OSD.xSpeed`/`ySpeed`/`zSpeed` are
  mph. `OSD.hSpeed` matches the horizontal components, so position-derived speed is
  not required.
- `DETAILS.totalDistance [ft]` is scaled by 1,000 (thousands of feet); the raw 4.4,
  13.0, and 4.9 values mean 4,400, 13,000, and 4,900 ft.
- All three flights use serial `1581F6Z9C241P003` and name `DJI Mini 4 Pro`; this is
  one vehicle and three flights.
- The three home points are distinct: Colorado, Palos Verdes, and Offshore San
  Francisco. The current `dim_site` seed lists only `DJI_CO` and `DJI_CA`; the
  unresolved mapping stays null and keys to `dim_site(-1)`. Member C can add real
  site members in `WP-06` once a source-grounded mapping exists.

### Validation

Source validation is recorded in
[`source_validation/SRC-DJI-NOMINAL.md`](source_validation/SRC-DJI-NOMINAL.md).
The three CSVs pass with documented cleaning rules; no video is used.

### License and attribution

MIT. Preserve the dataset card and license notice in
[`../../data/all_data_summary.md`](../../data/all_data_summary.md) and the source
manifest.

## SRC-METAR-AWC: NOAA Aviation Weather Center

### What it provides

Current and recent METAR observations for site-adjacent stations.

- Endpoint: <https://aviationweather.gov/api/data/metar>
- Example: `?ids=KBTP,KAGC&format=json&hours=24`
- API documentation: <https://aviationweather.gov/data/api/>
- No API key is required.
- Use for weekly incremental weather and recent cross-checks. AWC retains only the
  previous 30 days, so it is not the historical source.

### Fields

`icaoId`, `name`, `metarType`, `obsTime`, `reportTime`, `receiptTime`, `temp`,
`dewp`, `wdir`, `wspd`, `wgst`, `visib`, `altim`, `slp`, `presTend`, `cover`,
`clouds`, `fltCat`, `rawOb`, `qcField`, `lat`, `lon`, `elev`.

Units: `temp`/`dewp` deg C; `wdir` deg true north or `VRB`; `wspd`/`wgst` kt;
`visib` statute miles (string `10+` occurs); `altim`/`slp`/`presTend` hPa;
`elev` m MSL; `clouds[].base` ft AGL.

### Access and limits

- `obsTime` is the actual observation time in Unix epoch seconds; `reportTime` is a
  rounded/scheduled ISO time and must not be used as the observation timestamp.
- Most endpoints return at most 400 entries. Query per station with `hours=168` for
  weekly increments; six requests/week stay small.
- Rate limit is 100 requests/minute. Set a custom `User-Agent` and back off on HTTP
  `429`.
- AWC also publishes minute-updated cache files for all current METARs; they are not
  required for the weekly incremental load.

### Caveats

- `wdir` may be `VRB`; store null or a documented sentinel, not zero.
- `visib='10+'` is a floor; preserve the raw text and cap the numeric value at 10.
- `clouds` can be an empty list; derive `cloud_ceiling_ft` from the lowest `BKN`,
  `OVC`, or `VV` layer, not from `cover` alone.
- `wgst`, `slp`, and `presTend` are often missing; store null, not zero.
- `SPECI` records are included; preserve `metarType` and deduplicate on
  `(icaoId, obsTime)`.
- AWC `altim` is hPa, while `dim_weather.altimeter_inhg` is inHg; convert explicitly.
- Use IEM for historical dates; AWC is a rolling 30-day source.

### Validation

Source validation is recorded in
[`source_validation/SRC-METAR-AWC.md`](source_validation/SRC-METAR-AWC.md). The
24-hour KBTP/KAGC sample returned 85 records (43,913 bytes; SHA-256
`8c6b99426281eb6c5de7f9ee32cabbf839cd81f183ded494d7c77a201c62c73e`). A live
AWC/IEM cross-check matched 48 common routine observations with zero numeric
differences after unit conversion. The decision is `PASS`; AWC is used for weekly
increments and recent cross-checks, with IEM as the historical source.

### License

U.S. government open data. Attribute NOAA/NWS Aviation Weather Center in the source
manifest and generated reports.

## SRC-METAR-IEM: Iowa Environmental Mesonet ASOS

### What it provides

Historical METAR/ASOS data for the source dates and nearest stations.

- Service: <https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py>
- Download interface: <https://mesonet.agron.iastate.edu/request/download.phtml>
- Use station-specific requests for KBTP, KAGC, and the nearest stations for the
  Nightjar and DJI sites.
- No API key is required.

### Fields

`station`, `valid`, `lon`, `lat`, `tmpf`, `dwpf`, `relh`, `drct`, `sknt`, `gust`,
`p01i`, `alti`, `mslp`, `vsby`, `skyc1`-`skyc4`, `skyl1`-`skyl4`, `wxcodes`,
`ice_accretion_1hr`/`3hr`/`6hr`, `peak_wind_gust`, `peak_wind_drct`,
`peak_wind_time`, `feel`, `metar`, `snowdepth`.

Units: `valid` UTC; `tmpf`/`dwpf`/`feel` deg F; `drct` deg true north; `sknt`/`gust`
kt; `p01i` inches; `alti` inHg; `mslp` hPa; `vsby` statute miles; `skyl1`-`skyl4` ft
(AGL cloud-layer heights); `ice_accretion_*` inches; `snowdepth` inches.

### Access and limits

- Request `tz=UTC`, `format=onlycomma`, `latlon=no`, `missing=M`, `trace=T`,
  `direct=no`.
- Request both `report_type=3` (routine hourly) and `report_type=4` (specials) for
  parity with AWC. Requesting only `3` omits `SPECI`.
- The CSV `station` column is three characters (`BTP`, `AGC`) even when the request
  uses `KBTP`/`KAGC`; recover the ICAO from the request or the raw `metar`.
- `valid` has no `Z` suffix; always request UTC.

### Caveats

- Record `M` as null and `T` as trace, not zero.
- `drct=0` with `sknt=0` is calm, not a north wind.
- `mslp` can be missing for every row at a station; `alti` is still available.
- `mslp` is hPa and `alti` is inHg; do not mix them.
- `skyc1='VV '` has a trailing space; trim it and treat `VV` as vertical visibility.
- IEM does not provide flight category; derive it from visibility and ceiling using
  documented thresholds, or store null and preserve the raw METAR.
- Derive `cloud_ceiling_ft` from the lowest `BKN`, `OVC`, or `VV` layer.
- Verify station coverage. KTOA is sparse; Nightjar's nearest station KAVP is
  13.4 nm away. Record the station-to-site distance and preserve missing hours.
- Do not fabricate a nearest-station observation if the station has no data. The
  documented fallback set is KMPO for Nightjar, KBKF/KDEN for Colorado, KLGB/KLAX
  for Palos Verdes, and KSQL for Offshore San Francisco.

### Validation

Source validation is recorded in
[`source_validation/SRC-METAR-IEM.md`](source_validation/SRC-METAR-IEM.md). Six real
station-day samples were validated (31,949 bytes total; 133 routine rows). The AWC
cross-check matched 48 common routine observations with zero numeric differences
after unit conversion. The decision is `PASS WITH LIMITATION` because KTOA coverage
is sparse, Nightjar's nearest station is 13.4 nm away, and `report_type` must include
both routine and special reports.

### License

IEM states that the materials on its website are in the public domain and may be used
freely for any lawful purpose; attribution to the Iowa Environmental Mesonet of Iowa
State University is appreciated. The underlying observations originate from NWS
ASOS/AWOS.

## SRC-FAA-UDDS: FAA UAS Data Delivery System

### What it provides

Real airspace and restriction polygons:

- FAA UAS Facility Map:
  `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/FAA_UAS_FacilityMap_Data_V5/FeatureServer`
- Part-Time National Security UAS Flight Restrictions:
  `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Part_Time_National_Security_UAS_Flight_Restrictions/FeatureServer`
- Airspace (granular services; `D-020`):
  - Class: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Class_Airspace/FeatureServer`
  - Special use: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Special_Use_Airspace/FeatureServer`
  - Route: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Route_Airspace/FeatureServer`

### Fields

- Facility map: `CEILING` (integer feet), `UNIT` (`Feet`), `MAP_EFF` and
  `LAST_EDIT` (M/D/YYYY strings), `LATITUDE`/`LONGITUDE` (grid cell center),
  `GLOBALID`, `APT1_*`-`APT5_*`, `AIRSPACE_1`-`5`, `REGION`, and polygon geometry.
- TFR: `FAA_ID`, `Proponent`, `Branch`, `Base`, `Facility`, `State`, `Floor`,
  `Ceiling`, `ALERTYPE`, `ALERTTIME`/`ACTIVETIME`/`ENDTIME` (epoch ms), and polygon
  geometry. `Floor`/`Ceiling` are strings, not numeric fields.
- Airspace: use `GLOBAL_ID` as the natural key and `OBJECTID` only as the
  service-local id.
  - Class: `IDENT`, `ICAO_ID`, `NAME`, `TYPE_CODE`, `LOCAL_TYPE`, `CLASS`,
    `UPPER_*`/`LOWER_*`, `MIL_CODE`, `COMM_NAME`, `WKHR_CODE`, `ADHP_ID`.
  - Special use: `NAME`, `TYPE_CODE`, `CLASS`, `UPPER_*`/`LOWER_*`, `LEVEL_CODE`,
    `TIMESOFUSE`, `REMARKS`.
  - Route: `TYPE_CODE`, `LOCAL_TYPE`, `CLASS`, `REF_CLASS`, `REF_ID`.
  - Native coordinates are EPSG:4269; request `outSR=4326`.

### Access and limits

- Query with `f=json` or `f=geojson`, `outFields=*`, `returnGeometry=true`.
- Paginate using `resultOffset` and `resultRecordCount`. `maxRecordCount` is 1,000
  for the facility map and 2,000 for TFR and each granular airspace service;
  `exceededTransferLimit=true` means more rows remain.
- The service reported a limit of approximately 6,000 request units per minute.
  Large airspace counts can consume the quota quickly; use conservative
  pagination, sleep/backoff, and a weekly cadence.
- Filter to study-site bounding boxes or relevant Pennsylvania areas. Do not load
  the full national facility map.

### Caveats

- Historical TFR availability is not guaranteed. The live layer had only 5 features
  at validation time and none in the study-site boxes. The warehouse will capture
  real TFR snapshots going forward and use static facility/airspace polygons as
  reference.
- Do not claim historical TFR coverage that the source does not provide.
- Geometry may be multipart; normalize to valid WKT/GeoJSON and store a bounding box.
- Facility map coverage is uneven: KBTP and Nightjar have **0** cells; KAGC has 317,
  Colorado 66, Palos Verdes 58, and Offshore San Francisco 50. Do not fabricate
  missing cells.
- Airspace is published on an eight-week effective cycle. The granular items
  validated here describe the cycle `0901Z 29 Oct 2026` to `0901Z 24 Dec 2026`.
  Keep the fetch date and effective cycle in the source manifest.
- Do not use the `Airspace (DEMO)` layer. Use the three approved granular services
  and deduplicate across them by `GLOBAL_ID`.
- `Boundary_Airspace`, `Airspace_Schedule`, and the DEMO layer remain unapproved
  unless a later decision adds them.

### Validation

Source validation is recorded in
[`source_validation/SRC-FAA-UDDS.md`](source_validation/SRC-FAA-UDDS.md). The
facility map and TFR layers are usable with the coverage caveats above. On
2026-11-07 the human approved the granular Class, Special Use, and Route services
(`D-020`); the DEMO layer is not used. National counts are Class 6,041, Special Use
1,545, and Route 5,263. In 0.25-degree study boxes, combined counts are KBTP 19,
KAGC 26, Nightjar 52, Colorado 42, Palos Verdes 90, and Offshore San Francisco 54.
The current decision is `PASS WITH LIMITATION` because of the facility-map coverage
gap and current-only TFR layer, not because of the airspace license.

### License

U.S. government open data. Facility and TFR items carry FAA attribution and
disclaimers. The approved granular airspace items identify
`AeronauticalInformationServices_FAA` as owner, state that the data is “for public
use,” and require FAA/Aeronautical Information Services attribution. Record the
service item IDs in the source manifest. The `Airspace (DEMO)` item is not
approved for load.

## SRC-OPENSKY: OpenSky Network

### Role

Optional recent manned aircraft snapshots for the study bounding boxes. Not a
dependency for the initial warehouse.

### Access

- Endpoint: <https://opensky-network.org/api/states/all>
- Bounding box example for KBTP/PA:
  `?lamin=40.3&lomin=-80.3&lamax=41.0&lomax=-79.5`
- Anonymous access: approximately 400 credits/day.
- Authenticated access: approximately 4,000 credits/day.
- Historical Trino access requires a separate application and credentials.

### Caveats

- REST state vectors are recent only; do not label them as historical.
- Anonymous availability and rate limits can vary.
- Do not apply for an account or accept terms on behalf of the human.
- Do not commit raw OpenSky payloads if the terms prohibit redistribution.
- If OpenSky fails, the required Tartan/UAS loads must still be valid.

## Excluded sources

| Source | Reason |
|---|---|
| Synthetic flight generators | Prohibited by project constraint |
| DroneLog or other restricted flight logs | Files/terms not available or unclear |
| Paid ADS-B history providers | Paid/card-gated |
| Large drone video archives | Not needed for the warehouse; adds storage and privacy risk |
| Kaggle datasets without clear licenses | License/provenance risk |

The legacy synthetic files under [`../../data/sample/`](../../data/sample/) are
retained only for offline demonstration and evaluator review. They are not a Phase 2
source, are excluded from every load, and must never be cited as real data or
extraction evidence. See [`../DECISIONS.md`](../DECISIONS.md) `D-017`.

## Attribution requirements

The final repository and reports must include:

- TartanAviation citation and CC BY 4.0 notice.
- Nightjar dataset card references and CC BY 4.0 notice.
- Nominal-io dataset card and MIT notice.
- FAA and NOAA source URLs and attribution.
- Iowa Environmental Mesonet/Iowa State University attribution for the ASOS
  historical archive.
- OpenSky terms and access note if OpenSky data is used.
- A statement that all derived metrics come from the cited real source records.

## Source validation checklist

`WP-03` must validate each source before it is frozen:

- URL is reachable without a card or private credential.
- License and attribution are recorded.
- File size and checksum are captured.
- Expected fields and types are documented.
- A real sample parses successfully.
- Timestamps are UTC and unambiguous.
- Coordinates are valid and in the expected site area.
- Units are identified and converted explicitly.
- Duplicate and invalid-row behavior is measured.
- Capacity impact is estimated.
- A fallback decision exists if the source is unavailable.

If any item fails and the business response is unclear, stop and ask the human.

## Cadence summary

| Source | Initial | Weekly | Manual |
|---|---|---|---|
| TartanAviation | Archive and load selected window | No change | Optional reload |
| Nightjar | Load selected flights | No change | Optional reload |
| Nominal-io DJI | Load selected flights | No change | Optional reload |
| NOAA AWC | Current snapshot | Fetch recent window | Optional |
| IEM ASOS | Backfill source dates | Fetch missing window | Optional |
| FAA UDDS | Fetch current polygons/TFRs | Fetch current snapshots | Optional |
| OpenSky | Optional snapshot | Optional snapshot | Optional |
