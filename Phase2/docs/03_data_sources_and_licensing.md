# Data Sources and Licensing

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
| `SRC-TARTAN` | TartanAviation ADS-B | Primary historical manned tracking, journeys, encounters, occupancy | Public HTTPS/Swift download | Initial bulk; static | CC BY 4.0 | Accepted; georeference validation required |
| `SRC-NIGHTJAR` | Nightjar DJI flight telemetry | Real UAS tracking and journeys, 10 Hz | Public Hugging Face files | Initial bulk | CC BY 4.0 | Accepted; parser validation required |
| `SRC-DJI-NOMINAL` | Nominal-io DJI telemetry | Additional real UAS tracking and journeys | Public Hugging Face files | Initial bulk | MIT | Accepted; parser validation required |
| `SRC-METAR-AWC` | NOAA Aviation Weather Center METAR | Current weather observations | Public HTTP JSON | Weekly | U.S. government open data | Accepted; validation required |
| `SRC-METAR-IEM` | Iowa Environmental Mesonet ASOS | Historical METAR for source dates | Public HTTP CSV | Initial + weekly backfill | Public academic archive; verify terms | Accepted; validation required |
| `SRC-FAA-UDDS` | FAA UDDS ArcGIS layers | UAS facility map, TFRs, airspace zones | Public ArcGIS REST GeoJSON | Initial + weekly | U.S. government open data | Accepted; validation required; query limits |
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

- Raw records include `ID`, `Range`, `Bearing`, `Altitude`, `Date`, and `Time`.
- Processed records use a local runway frame: `Frame`, `ID`, `x`, `y`, `z`,
  `Headwind`, and `Crosswind`.
- Raw positions must be georeferenced from KBTP camera reference
  `40.777888, -79.949864` using range and bearing. Validate against known airport
  geometry before use.
- Processed local coordinates must not be presented as latitude/longitude.
- KAGC georeferencing is not yet validated; use KAGC for weather/airspace context
  unless `WP-03` proves the coordinate transform.
- Archive the raw source and preserve the download timestamp and SHA-256.

### License and attribution

Data is CC BY 4.0. Cite the TartanAviation paper and dataset in the repository
documentation and generated reports. Code is BSD-3-Clause; do not copy code without
preserving its license notice.

## SRC-NIGHTJAR: Nightjar DJI flight telemetry

### What it provides

Real DJI FlightRecord data from instrumented field flights at a Pennsylvania site:

- Primary candidate: `joshruby/nightjar-flight-20260804`
- Additional candidate: `joshruby/nightjar-flight-20260813`
- `20260804`: 12,447 valid GPS fixes out of 12,448 rows, 10 Hz, 20.9 minutes.
- Site coordinates: approximately `41.5347, -75.5953`.
- Useful fields: `CUSTOM.dateTime`, `OSD.latitude`, `OSD.longitude`,
  `OSD.height` (feet AGL), `OSD.altitude` (feet MSL), speed components, battery,
  flight state, and vehicle serial.

### Access

- Dataset card:
  <https://huggingface.co/datasets/joshruby/nightjar-flight-20260804>
- Additional flight:
  <https://huggingface.co/datasets/joshruby/nightjar-flight-20260813>
- Download only `dji/*.csv` and `dji/*.geojson`. Do not download audio or video.
- No token or card is required.

### Fields and caveats

- CSV column names vary across DJI firmware and exports.
- The first row may have a zero `CUSTOM.dateTime`; filter invalid timestamps.
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

- Headers differ by export: `timestamps` vs `timestamps_ns`.
- Timestamp values may be seconds or nanoseconds; normalize safely.
- Latitude/longitude can be zero before takeoff or when GPS is unavailable.
- `OSD.height` is generally AGL; `OSD.altitude` is generally MSL. Record the datum.
- Speed fields differ across flights; derive speed from position when needed.
- The sites are separate `dim_site` records.

### License and attribution

MIT. Preserve the dataset card and license notice in
[`../../data/all_data_summary.md`](../../data/all_data_summary.md) and the source
manifest.

## SRC-METAR-AWC: NOAA Aviation Weather Center

### What it provides

Current and recent METAR observations for site-adjacent stations.

- Endpoint: <https://aviationweather.gov/api/data/metar>
- Example: `?ids=KBTP,KAGC&format=json&hours=3`
- No API key is required.
- Use for weekly incremental weather.

### Fields

`icaoId`, `obsTime`, `reportTime`, `temp`, `dewp`, `wdir`, `wspd`, `wgst`, `visib`,
`altim`, `slp`, `cover`, `clouds`, `fltCat`, `rawOb`, `lat`, `lon`, `elev`.

### Caveats

- Use UTC observation time, not receipt time.
- `wdir` may be `VRB`; store null or a documented sentinel.
- Cloud ceiling must be derived from the lowest broken/overcast layer, not simply
  copied from an arbitrary cloud entry.

## SRC-METAR-IEM: Iowa Environmental Mesonet ASOS

### What it provides

Historical METAR/ASOS data for the source dates and nearest stations.

- Service: <https://mesonet.agron.iastate.edu/request/download.phtml>
- Use station-specific requests for KBTP, KAGC, and the nearest stations for the
  Nightjar and DJI sites.
- No API key is required.

### Caveats

- Verify station coverage and time zone; request UTC.
- Record missing values as null, not zero.
- Do not fabricate a nearest-station observation if the station has no data.

## SRC-FAA-UDDS: FAA UAS Data Delivery System

### What it provides

Real airspace and restriction polygons:

- FAA UAS Facility Map:
  `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/FAA_UAS_FacilityMap_Data_V5/FeatureServer`
- Part-Time National Security UAS Flight Restrictions:
  `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Part_Time_National_Security_UAS_Flight_Restrictions/FeatureServer`
- Airspace:
  `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Airspace/FeatureServer`

### Fields

- Facility map: `CEILING`, `UNIT`, `MAP_EFF`, `LAST_EDIT`, `LATITUDE`, `LONGITUDE`,
  `GLOBALID`, airport identifiers, region, and polygon geometry.
- TFR/airspace layers: inspect field metadata in `WP-03`; do not assume names.

### Access and limits

- Query with `f=json` or `f=geojson`, `outFields=*`, `returnGeometry=true`.
- Paginate using `resultOffset` and `resultRecordCount`.
- The service reported a limit of approximately 6,000 request units per minute.
  Use conservative pagination, sleep/backoff, and a weekly cadence.
- Filter to study-site bounding boxes or relevant Pennsylvania areas.

### Caveats

- Historical TFR availability is not guaranteed. The warehouse will capture real TFR
  snapshots going forward and use static facility/airspace polygons as reference.
- Do not claim historical TFR coverage that the source does not provide.
- Geometry may be multipart; normalize to valid WKT/GeoJSON and store a bounding box.

### License

U.S. government open data. Verify the current FAA/ArcGIS terms before redistribution
and include attribution.

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
