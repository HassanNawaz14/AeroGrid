# Source Validation: SRC-FAA-UDDS

## Source identity

| Field | Value |
|---|---|
| Source | FAA UAS Data Delivery System (UDDS) ArcGIS layers |
| URL | Facility map: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/FAA_UAS_FacilityMap_Data_V5/FeatureServer`; TFRs: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Part_Time_National_Security_UAS_Flight_Restrictions/FeatureServer`; Class: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Class_Airspace/FeatureServer`; Special use: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Special_Use_Airspace/FeatureServer`; Route: `https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Route_Airspace/FeatureServer` |
| License | U.S. government open data. Facility map and TFR items carry FAA attribution/disclaimers. The granular airspace items state “The data provided is for public use” and identify the FAA Aeronautical Information Services as the source. The `Airspace (DEMO)` item is **not** approved for load; `D-020` selects the granular services. |
| Attribution | Facility: FAA/ATO/Aeronautical Information Services. TFR: FAA/ATO/System Operation Security, AJR-2. Airspace: Federal Aviation Administration, Air Traffic Organization, Mission Support Services, Aeronautical Information Services. Preserve FAA attribution and service item IDs. |
| Fetch time (UTC) | 2026-11-06T20:37Z |
| File name(s) | Facility/TFR service, layer, and sample metadata; granular airspace service/layer metadata, one-feature samples, and `faa_granular_study_counts.json` |
| Size | Facility/TFR metadata 6.7 KB and 25.9 KB; samples 8.5 KB and 6.7 KB. Granular layers 15.9 KB, 15.0 KB, 11.0 KB; metadata 12.1 KB, 10.8 KB, 5.3 KB; samples 116.6 KB, 1.1 KB, 9.6 KB; study counts 1.5 KB. |
| SHA-256 | Facility sample `d25d8f9fe33399c0af31e4e6a3128f6299c379af7a00a37e491f16532ea89431`; TFR sample `7f30c6cc95ca50ae0e581dfc0d3f7f9955d4e71b74b3f694afb3a833eb450092`; Class sample `1000305e0418326ab6b2d09811ab58e2195a257fdd43a7d8f0582d58db74e8e5`; Special Use sample `66d3b0ce29e6a7936bae08a0e8211c10e5262e16d1fa32ae51aa3ccd59f7975e`; Route sample `8abbd2e2a13407754bc0ea0e22b1f1302c6d37726f8c26d5dce4342e97a033a0`; study counts `97ee6b8afb793665d3b595eef3ad3075b279dfe661b46c9ad33cf30a283c76d7` |
| Sample/archive | Live ArcGIS REST metadata plus small real query samples and counts. No full national extract was downloaded. |

Service item IDs: facility `ee469d2965014d978d1973c440119152`; TFR
`3a4a808aec634e4e8e4b0ee0d5366da6`; Class_Airspace
`c6a62360338e408cb1512366ad61559e`; Special_Use_Airspace
`dd0d1b726e504137ab3c41b21835d05b`; Route_Airspace
`8bf861bb9b414f4ea9f0ff2ca0f1a851`. All five layers expose `Query` only
(no editing), and support `json`, `geoJSON`, and `PBF`.

## Schema

### Facility map (`FAA_UAS_FacilityMap_Data_V5/0`)

- Geometry: `esriGeometryPolygon`, WGS 84 (EPSG:4326).
- Extent: national; `maxRecordCount` 1000.
- Total features: **370,441**; 370,436 have `APT1_ICAO` populated.
- Fields: `OBJECTID`, `CEILING` (integer), `UNIT` (string, `Feet`), `MAP_EFF`
  and `LAST_EDIT` (M/D/YYYY strings), `LATITUDE`, `LONGITUDE` (grid cell center),
  `GLOBALID`, `ARPT_COUNT`, `APT1_*` through `APT5_*` (`FAAID`, `ICAO`, `NAME`,
  `LAANC`, `Enabled`), `AIRS_COUNT`, `AIRSPACE_1`-`5`, `REGION`,
  `Shape__Area`, `Shape__Length`.
- Sample: KAGC cells have `CEILING=300`, `UNIT=Feet`, `MAP_EFF=10/6/2022`,
  `LAST_EDIT=5/27/2022`, `APT1_ICAO=KAGC`, `APT1_LAANC=1`,
  `AIRSPACE_1=D`, and a simple one-ring polygon. The 1,000-feature sample had no
  multipart geometries.

### TFRs (`Part_Time_National_Security_UAS_Flight_Restrictions/0`)

- Geometry: `esriGeometryPolygon`, WGS 84 (EPSG:4326).
- `maxRecordCount` 2000.
- Total features at validation time: **5**.
- Fields: `OBJECTID`, `Proponent`, `Branch`, `Base`, `Facility`, `Airspace`,
  `Reason`, `State`, `FAA_ID`, `POC`, `Floor`, `Ceiling`, `County`, `ALERTYPE`,
  `ADVISEINST`, `ADVISEAUTH`, `ADVISENOTE`, `ALERTTIME`, `ACTIVETIME`, `ENDTIME`,
  `Shape__Area`, `Shape__Length`.
- `Floor` and `Ceiling` are strings (for example `Surface`, `400' AGL`).
  `ALERTTIME`, `ACTIVETIME`, and `ENDTIME` are epoch milliseconds; 3 of 5 rows
  have null times because they are intermittent. The two timed rows cover
  `2026-11-02T13:00Z` to `2026-11-05T05:00Z`.

### Airspace granular layers (`Class_Airspace/0`, `Special_Use_Airspace/0`, `Route_Airspace/0`)

- Geometry: `esriGeometryPolygon`; native spatial reference is NAD 83
  (EPSG:4269). Request `outSR=4326` for WGS 84.
- Each service has `maxRecordCount` 2000 and exposes `Query` only.
- Total national features: Class **6,041**; Special Use **1,545**; Route
  **5,263**; combined **12,849**.
- Class fields (39): `OBJECTID`, `GLOBAL_ID`, `IDENT`, `ICAO_ID`, `NAME`,
  `UPPER_DESC`, `UPPER_VAL`, `UPPER_UOM`, `UPPER_CODE`, `LOWER_DESC`,
  `LOWER_VAL`, `LOWER_UOM`, `LOWER_CODE`, `TYPE_CODE`, `LOCAL_TYPE`, `CLASS`,
  `MIL_CODE`, `COMM_NAME`, `LEVEL_`, `SECTOR`, `ONSHORE`, `EXCLUSION`,
  `WKHR_CODE`, `WKHR_RMK`, `DST`, `GMTOFFSET`, `CONT_AGENT`, `CITY`, `STATE`,
  `COUNTRY`, `ADHP_ID`, `US_HIGH`, `AK_HIGH`, `AK_LOW`, `US_LOW`, `US_AREA`,
  `PACIFIC`, `Shape__Area`, `Shape__Length`.
- Special Use fields (34): `OBJECTID`, `GLOBAL_ID`, `NAME`, `TYPE_CODE`,
  `CLASS`, `UPPER_DESC`, `UPPER_VAL`, `UPPER_UOM`, `UPPER_CODE`, `LOWER_DESC`,
  `LOWER_VAL`, `LOWER_UOM`, `LOWER_CODE`, `LEVEL_CODE`, `CITY`, `STATE`,
  `COUNTRY`, `CONT_AGENT`, `COMM_NAME`, `SECTOR`, `ONSHORE`, `EXCLUSION`,
  `TIMESOFUSE`, `GMTOFFSET`, `DST_CODE`, `REMARKS`, `AK_LOW`, `AK_HIGH`,
  `US_LOW`, `US_HIGH`, `US_AREA`, `PACIFIC`, `Shape__Area`, `Shape__Length`.
- Route fields (15): `OBJECTID`, `GLOBAL_ID`, `TYPE_CODE`, `LOCAL_TYPE`,
  `CLASS`, `REF_CLASS`, `REF_ID`, `AK_LOW`, `AK_HIGH`, `US_LOW`, `US_HIGH`,
  `US_AREA`, `PACIFIC`, `Shape__Area`, `Shape__Length`.
- Samples:
  - Class: `GLOBAL_ID=A89A815A-B9A8-496E-95F9-7B30216287A5`, `IDENT=ATL`,
    `NAME=HARTSFIELD-JACKSON ATLANTA INTL MODE C`, `TYPE_CODE=MODE-C`,
    `CLASS=Other`, `UPPER_VAL=10000` (integer, FT MSL), `LOWER_VAL=0` (SFC).
  - Special Use: `GLOBAL_ID=5F02297F-7DF5-478E-B876-C758B6E4B910`, `NAME=A-220`,
    `TYPE_CODE=A`, `CLASS=null`, `UPPER_VAL="4500"` (string, FT MSL),
    `LOWER_VAL="0"` (string, SFC), `TIMESOFUSE="0800 - 2200, DAILY"`.
  - Route: `GLOBAL_ID=4B6A3AB2-7E56-4CF3-89FC-38C4A6E2F876`, `TYPE_CODE=CLASS`,
    `LOCAL_TYPE=CORRIDOR`, `CLASS=E`, `REF_CLASS=1`, and a linked `REF_ID`.
- The granular layers do not expose row-level effective/last-edit date fields.
  The item descriptions state the current eight-week cycle:
  `0901Z 29 Oct 2026` to `0901Z 24 Dec 2026`.

## Time

- Facility `MAP_EFF` and `LAST_EDIT` are `M/D/YYYY` strings, not ISO or epoch.
  Parse explicitly; do not rely on locale.
- TFR date fields are ArcGIS date fields in epoch milliseconds
  (`ALERTTIME`, `ACTIVETIME`, `ENDTIME`). Convert as UTC.
- TFR is a current/part-time layer, not a historical archive. At validation time
  it had 5 features; no feature intersected the study-site bounding boxes. Two
  timed features expired on 2026-11-05; the other three have null time windows.
  Do not claim historical TFR coverage.
- Granular airspace is a static/reference snapshot on an eight-week publication
  cycle. Store the fetch timestamp and effective-cycle text in the source
  manifest; do not infer a row-level effective date.

## Coordinates and geometry

- Facility and TFR services are already EPSG:4326. Granular airspace is
  EPSG:4269 and returns WGS 84 when queried with `outSR=4326`.
- `f=geojson` works for all five layers and returns a valid FeatureCollection
  with `crs` EPSG:4326 when `outSR=4326`. The HTTP content type is
  `application/json`, not `application/geo+json`, so parse by body, not header.
- Facility sample geometry is a one-ring polygon; no multipart geometry was seen
  in the 1,000-feature sample. TFR and airspace are also polygons; normalize rings
  and store a bounding box.
- The facility map covers the study area unevenly:
  - KBTP: **0** features by bbox and by `APT1_ICAO='KBTP'`/`APT1_FAAID='BTP'`.
  - KAGC: **317** features.
  - Colorado: **66** features.
  - Palos Verdes: **58** features.
  - Offshore San Francisco: **50** features.
  - Nightjar PA: **0** features.
  KBTP and Nightjar are not LAANC/facility-map sites; do not fabricate coverage.
- TFR: **0** features in every study-site bounding box at validation time.
- Airspace coverage using 0.25-degree boxes around each site:
  - KBTP: Class 14, Special Use 0, Route 5; combined **19**.
  - KAGC: Class 19, Special Use 0, Route 7; combined **26**.
  - Nightjar PA: Class 10, Special Use 0, Route 42; combined **52**.
  - Colorado: Class 15, Special Use 0, Route 27; combined **42**.
  - Palos Verdes: Class 24, Special Use 0, Route 66; combined **90**.
  - Offshore San Francisco: Class 24, Special Use 0, Route 30; combined **54**.
  The 0.25-degree boxes are validation windows, not the final `dim_site` bboxes.
- No impossible coordinates or geometry errors were observed in the samples.

## Identity

- Facility: natural key is `GLOBALID`; `OBJECTID` is service-local. The grid cell
  also has `LATITUDE`/`LONGITUDE`, but the authoritative identity is the FAA
  `GLOBALID`.
- TFR: natural key is `FAA_ID`; `OBJECTID` is service-local. Preserve `FAA_ID`,
  `Facility`, `Base`, and the time window.
- Airspace: natural key is `GLOBAL_ID`; `OBJECTID` is service-local. Preserve
  `GLOBAL_ID`, `NAME`/`IDENT`/`ICAO_ID`, `TYPE_CODE`, `CLASS`/`LOCAL_TYPE`, and
  vertical limits. Deduplicate across the three granular services by `GLOBAL_ID`.
- Route `REF_CLASS`/`REF_ID` can link a route airspace row to another airspace
  feature; preserve the pair even when the referenced feature is outside the
  loaded study boxes.
- Site mapping: facility and airspace records can be linked to `dim_site` by
  spatial intersection or by `APT1_ICAO`/`ICAO_ID`; TFRs overlap sites only when
  a real feature intersects the site bbox. Do not invent TFR rows for sites with
  no intersecting feature.

## Volume and capacity

- Facility: 370,441 national features. Do **not** load the full national layer;
  query only the study-site bounding boxes. The five site boxes returned 491
  features total (KAGC 317 + Colorado 66 + Palos 58 + SF 50; KBTP and Nightjar 0).
  At about 1 KB/feature including geometry, the filtered set is well under 1 MB.
- TFR: 5 features nationally, 0 in study boxes. Negligible.
- Airspace: 12,849 national features across the three approved granular layers.
  The six 0.25-degree study boxes returned 283 features total. Filter to the
  boxes; the filtered set is well under 1 MB. A full national load would be
  roughly 13 MB at 1 KB/feature, still small but unnecessary.
- Object storage: store the small query snapshots and provenance metadata, not the
  full national facility map. The samples total well under 1 MB.
- Database estimate: negligible against the 1 GiB limit when filtered to the study
  sites.

## Quality findings

- Completeness: facility `APT1_ICAO` is populated in 370,436 of 370,441 rows;
  KBTP and Nightjar have no facility-map coverage. TFR has only 5 current features,
  3 with null time windows. Granular airspace has no Special Use features in the
  study boxes; record that as real coverage, not missing data. Class and Route
  cover every study site.
- Accuracy: facility `CEILING` is an integer in feet; `UNIT=Feet`; `MAP_EFF` and
  `LAST_EDIT` are M/D/YYYY strings. TFR date fields are epoch milliseconds.
  Airspace native coordinates are EPSG:4269; request `outSR=4326`. Class vertical
  values are numeric in the sample; Special Use vertical values are strings
  (`"4500"`, `"0"`), so parse explicitly. The sample attributes and geometry are
  coherent.
- Uniqueness: `GLOBALID` (facility), `FAA_ID` (TFR), and `GLOBAL_ID` (airspace) are
  the natural keys. `OBJECTID` is service-local and must not be used as a
  warehouse key. The same `GLOBAL_ID` can appear in more than one granular service;
  deduplicate on load.
- Pagination: facility `maxRecordCount=1000`; TFR and each granular airspace
  service `maxRecordCount=2000`. `exceededTransferLimit=true` when more rows
  remain. Pagination with `resultOffset`/`resultRecordCount` works; use
  `returnCountOnly=true` on the `/query` endpoint before paginating.
- Query quota: the service reports approximately 6,000 request units per minute.
  Large airspace count queries hit `429` during validation and required a
  60-second backoff. Use conservative query sizes, avoid polling, and retry after
  the reset window.
- Known limitations:
  - Facility map does not cover KBTP or Nightjar. Do not fabricate cells; record
    the absence as a coverage gap.
  - TFR is current/part-time only, with 5 features at validation time and no
    historical archive. Do not claim historical TFR coverage.
  - Airspace is a static eight-week snapshot; do not treat it as real-time.
  - Class `CLASS` can be `Other` when `TYPE_CODE` carries the meaningful type.
  - `Boundary_Airspace`, `Airspace_Schedule`, and the `Airspace (DEMO)` layer are
    not approved. A later need for them requires a new decision.
  - Facility `MAP_EFF`/`LAST_EDIT` are locale-sensitive strings; parse with an
    explicit `M/D/YYYY` format.
  - ArcGIS GeoJSON uses `application/json`, not `application/geo+json`.

## Decision

- [ ] PASS
- [ ] FAIL
- [x] PASS WITH LIMITATION

Reason: The five FAA layers are real, public, queryable, and have usable geometry
and attributes. The granular Class, Special Use, and Route services have explicit
public-use terms and FAA attribution, and `D-020` approves them instead of the
`Airspace (DEMO)` layer. The limitations are data coverage and cadence: the
facility map has no KBTP/Nightjar cells, TFR is current-only, and airspace is an
eight-week static snapshot.

Fallback or human action: none for the airspace license question; `D-020` resolves
it. Do not use the DEMO layer. If `Boundary_Airspace` or `Airspace_Schedule` is
required later, record a new decision before loading it. For now, use only real
query results and preserve the absence of KBTP/Nightjar facility cells and
historical TFRs.

## Review

- Reviewer: Member D and Member E (pending); human source/license decision recorded
  as `D-020`
- Date: 2026-11-07
- Evidence links: this record; `Phase2/docs/03_data_sources_and_licensing.md`;
  `Phase2/DECISIONS.md`; `Phase2/PROGRESS.md`.
