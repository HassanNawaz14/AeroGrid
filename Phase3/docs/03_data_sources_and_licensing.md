# Phase 3 Data Sources and Licensing

**Status:** Phase 3 adds **no new data sources**. Analytics run on the data Phase 2
already ingests. The authoritative source catalogue remains
`Phase2/docs/03_data_sources_and_licensing.md`; this page records only what Phase 3
changes or must respect.

## Sources used (unchanged)

| Source | Phase 3 use | Licence note |
|---|---|---|
| TartanAviation ADS-B | Traffic, journey, occupancy, encounter analytics | CC BY 4.0 attribution required in artifacts |
| Nightjar / nominal-io DJI | UAS analytics where loaded | CC BY 4.0 / MIT notices preserved |
| NOAA AWC + IEM METAR | Weather-linked analytics where loaded | NOAA/NWS and IEM attribution |
| FAA airspace / UDDS | Zone and restriction context | FAA/AIS attribution; fetch date in evidence |
| OpenSky | Optional; not loaded (`D-013`) | Must not appear in any artifact as if measured |

## Phase 3-specific rules

1. **Attribution travels with artifacts.** Every PDF/PPTX dashboard artifact that
   shows source-derived numbers carries the attribution lines from
   `Phase2/docs/03_data_sources_and_licensing.md`.
2. **Screenshots are evidence, not data.** Dashboard screenshots are derivative
   renderings of query results; they never replace the underlying query citation.
3. **No redistribution of raw data.** BI artifacts contain aggregates only; raw rows
   stay out of Git and out of the `.pbix` shared file where feasible.
4. **Licence changes stop the work.** If a source changes its terms, stop, record in
   `Phase3/DECISIONS.md`, and ask the human before building on it.

## What Phase 3 must not claim

- Any metric about sources that never loaded (OpenSky; UAS/airspace where staging
  is empty) — these are coverage gaps, and BI must label them as such (`D3-009`).
- Certified capacity, operator identity, or regulatory compliance — the warehouse
  measures observed traffic, nothing more.
