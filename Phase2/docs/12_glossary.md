# Glossary

## Project and delivery terms

| Term | Meaning |
|---|---|
| Phase 1 | Frozen historical design submission; do not edit |
| Phase 2 | Implementation and evidence phase for the lab |
| Staging | Temporary, source-shaped cleaned data before dimensional loading |
| Data warehouse (DW) | Curated dimensional model used for analysis |
| Reporting layer | Views and metrics built on the warehouse for consumers |
| Star schema | Facts surrounded by denormalized dimensions |
| Fact | Measurable event or snapshot at a defined grain |
| Dimension | Descriptive context for facts |
| Grain | What one fact row represents |
| Work package (WP) | Small, independently reviewable unit of work |
| Gate | Human-approved checkpoint before dependent work |
| `G1` | Human prerequisites gate; closed 2026-11-04 (`H-007`) |
| `H-###` | Stable human action queue identifier |
| Definition of Done | Evidence required to mark a work package complete |
| Handoff | Written state transfer between agents/members |
| RACI | Responsible, accountable, consulted, informed roles |

## Data modeling terms

| Term | Meaning |
|---|---|
| Natural key | Real-world/source identifier used to match a dimension row |
| Surrogate key | Generated integer key used by facts |
| Unknown member | Dimension row `-1` used when an optional key cannot be resolved |
| Role-playing dimension | One dimension referenced multiple times with different meanings (e.g., two vehicles) |
| SCD Type 1 | Update in place; no history |
| SCD Type 2 | Preserve history with versioned rows; not required in Phase 2 |
| Orphan | Fact foreign key with no matching dimension row |
| Idempotent | Rerunning the same input produces the same result without duplicates |
| Reconciliation | Proving source, staging, and fact counts agree |
| Provenance | Traceability from a fact back to source and ETL run |
| Manifest | Record of source URL, license, hash, size, and fetch time |
| Raw archive | Immutable source copy in object storage |
| Schema drift | A source's columns or types change unexpectedly |
| Event timestamp | Exact UTC time of the observation or event |
| Time key | Surrogate key for the hourly `dim_time` row |
| Altitude MSL | Height above mean sea level |
| Altitude AGL | Height above ground level |
| Altitude datum | Reference surface for an altitude value |
| WGS84 | Standard geographic coordinate system used for latitude/longitude |
| Local frame | Source-specific coordinate frame requiring georeferencing |
| Georeferencing | Converting source coordinates to WGS84 |
| Grid cell | Horizontal/vertical spatial bucket used for density and occupancy |
| Altitude band | Vertical bucket within a grid cell |

## Aviation and source terms

| Term | Meaning |
|---|---|
| ADS-B | Automatic Dependent Surveillance-Broadcast position/telemetry |
| UAS | Unmanned aircraft system |
| ICAO24 | 24-bit aircraft transponder address |
| Callsign | Flight/operator identifier broadcast by an aircraft |
| METAR | Routine aviation weather observation |
| ASOS | Automated Surface Observing System |
| AWC | NOAA Aviation Weather Center |
| IEM | Iowa Environmental Mesonet; historical ASOS/METAR archive |
| TFR | Temporary Flight Restriction |
| UDDS | FAA UAS Data Delivery System |
| Facility map | FAA UAS facility map with grid ceilings and authorization data |
| Flight category | VFR/MVFR/IFR/LIFR classification |
| Ceiling | Lowest broken/overcast layer or vertical visibility |
| Close encounter | Two airborne vehicles below approved separation thresholds |
| Proximity | A broader, less severe separation threshold |
| Restriction activation | Whether a zone/TFR is active at a time |
| Occupancy | Vehicle-minutes/count within a grid cell and altitude band |
| Corridor | Candidate low-risk route/path derived from density and encounters |
| Capacity | Ability of a corridor/airspace to absorb additional traffic |
| TartanAviation | Carnegie Mellon ADS-B dataset/source used for manned traffic |
| Nightjar | Real UAS flight datasets used for low-altitude operations |
| Nominal-io DJI | Real DJI flight telemetry dataset used for UAS operations |
| OpenSky | Optional public ADS-B API/source |

## Platform and operations terms

| Term | Meaning |
|---|---|
| Neon | Accepted free-tier cloud PostgreSQL and object storage |
| Object storage | S3-compatible store for raw archives |
| GitHub Actions | CI/CD service used for scheduled/manual ETL |
| Workflow | Automated Actions definition |
| Artifact | File produced by a workflow run |
| Environment secret | Secret stored in a protected GitHub environment |
| Read-only role | Database role with `SELECT` only |
| Scale-to-zero | Neon behavior that suspends idle compute |
| CU-hour | Neon compute usage unit |
| Egress | Outbound data transfer |
| Branch protection | GitHub rule preventing direct/unsafe changes to `main` |
| Feature branch | Short-lived branch for one work package |
| Pull request (PR) | Review and merge request |
| Critical DQ | A failing check that blocks trusted publication |
| Warning DQ | A check that requires review but does not block the load |
| Trusted data | Data that passed required checks for the current run |

## Acronyms

| Acronym | Meaning |
|---|---|
| CI | Continuous integration |
| CSV | Comma-separated values |
| DDL | Data definition language |
| DQ | Data quality |
| ERD | Entity-relationship diagram |
| ETL | Extract, transform, load |
| FK | Foreign key |
| JSON | JavaScript Object Notation |
| PDF | Portable Document Format |
| PK | Primary key |
| SQL | Structured Query Language |
| UTC | Coordinated Universal Time |
