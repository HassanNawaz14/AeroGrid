# Member B — Source, Licensing & Staging Audit for Phase 3

**Author:** Member B (HarveyWebbs / Abdullah Zia)  
**Role:** Sources & Staging Engineer / Source & Licence Reviewer / Hardening Track Lead  
**Date:** 2026-11-21  
**Status:** COMPLETE — Formally Recorded Evidence

---

## 1. Executive Summary

As designated **Member B (Sources & Staging Engineer)**, this audit independently verifies
the provenance, licensing, data dictionary conformance, and staging integrity of all data
assets flowing into Phase 3 analytics, OLAP queries, and reporting views.

This audit confirms that:
1. All warehouse facts in `project_dw` derive strictly from real, approved public data sources.
2. Zero synthetic data or simulated records exist in the warehouse pipeline.
3. Every data source adheres to approved open data licenses.
4. The empty-means-missing-coverage invariant (`D-029`, `D3-009`) is maintained in all downstream queries.
5. External FAA ArcGIS quota vulnerabilities require hardening under **WP-P3-H2**.

---

## 2. Source Provenance & Licensing Verification

| Source ID | Source Name | Provider / Endpoint | Data License | Phase 3 Verification Status |
|---|---|---|---|---|
| `SRC-TARTAN-ADSB` | Tartan Aviation ADS-B | CMU Tartan Aviation repository | Open Data Commons / Research Public Domain | **VERIFIED PASS** — Real aircraft positions around KBTP study area. |
| `SRC-NOAA-METAR` | Aviation Weather Center METAR | NOAA / NWS Aviation Weather Center | U.S. Federal Government Open Data (Public Domain) | **VERIFIED PASS** — Temperature, wind speed, visibility surface observations. |
| `SRC-IEM-METAR` | Iowa Environmental Mesonet METAR | Iowa State University IEM Archive | Public Domain / CC0 equivalent | **VERIFIED PASS** — Secondary METAR archive fallback. |
| `SRC-FAA-UDDS` | FAA UAS Data Delivery System | FAA ArcGIS REST (`services6.arcgis.com`) | U.S. Federal Government Open Data (`D-020`) | **VERIFIED WITH RISK** — Airspace classes, SUAs, and TFR boundaries. Exposed to rate limiting. |

---

## 3. Staging and Warehouse Schema Integrity

### 3.1 Grains and Lineage Audit

Member B inspected the staging definitions (`project_staging`) and warehouse dimensions/facts (`project_dw`):
- `project_staging.stg_adsb_position`: Grain is one timestamped ADS-B message per vehicle. Reconciled with `fact_tracking_position` via deterministic surrogate keys (`SK`).
- `project_staging.stg_weather_metar`: Grain is one observation per station per valid UTC timestamp. Linked to `fact_tracking_position` via `dim_weather_condition` and spatial/temporal bounding.
- `project_staging.stg_airspace_zone`: Grain is one polygon feature from granular FAA services (`Class_Airspace`, `Special_Use_Airspace`, `Route_Airspace`). Validated against `D-020`.
- `project_staging.stg_restriction_snapshot`: Grain is one TFR feature query window snapshot from FAA UAS National Security restrictions.

### 3.2 Data Quality and Missing Coverage Semantics (`D3-009`)

Under `D3-009`, zero values in BI and analytical queries must distinguish between:
1. **Measured zero:** A source actively reported zero events during a valid observation window.
2. **Missing coverage:** The source had no sensor or query coverage for that timeframe/site.

Audit result:
- All Phase 3 analytical SQL queries (`Phase3/sql/analytical/`) and OLAP queries (`Phase3/sql/olap/`) use explicit `LEFT JOIN` operations against dimension tables (`dim_site`, `dim_vehicle`, `dim_source_system`) and classify null metrics as `NO_COVERAGE` or null-safe percentages, adhering to `DQ3-A-004`.

---

## 4. Hardening Track Justification (`WP-P3-H2`)

During source ingestion review, Member B identified that `SRC-FAA-UDDS` queries ArcGIS REST FeatureServices:
- FAA servers enforce request rate limits and occasionally return HTTP 429, HTTP 503, or JSON error payloads (`{"error": {"code": 400, "message": "..."}}`).
- Because airspace geometries (`Class_Airspace`, `Special_Use_Airspace`) change infrequently (published on standard 28-day aeronautical cycles), repeated querying of ArcGIS servers consumes unnecessary quota and risks pipeline failure.
- **Audit Decision:** Hardening work package **WP-P3-H2** is formally justified and triggered. Member B will implement:
  1. File-based caching for static airspace GeoJSON layers.
  2. Exponential backoff with jitter and retry budgets.
  3. Graceful degradation / optional-airspace run mode when quota is exhausted.

---

## 5. Audit Verdict

* **Provenance & Licensing:** **APPROVED (100% compliant)**
* **Staging Schemas & DQ Rules:** **APPROVED (100% compliant)**
* **External Reliability Trigger:** **WP-P3-H2 AUTHORIZED FOR IMPLEMENTATION**

*Signed,*  
**Abdullah Zia (HarveyWebbs)**  
Sources & Staging Engineer, AeroGrid Team
