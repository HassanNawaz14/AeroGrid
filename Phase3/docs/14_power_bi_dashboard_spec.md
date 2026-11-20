# AeroGrid Phase 3 Power BI Dashboard Specification

**Document ID:** `P3-BI-SPEC-001`  
**Status:** Approved for build (2026-11-20). `D3-012`–`D3-014` are approved; WP-P3-06 remains `IN_PROGRESS` until the PBIX, screenshots PDF, and A/D review evidence are recorded.  
**Work package:** WP-P3-06 — Power BI dashboard  
**Owner:** Member E (`HassanNawaz14`)  
**Reviewers:** Member A, Member D  
**Gate:** P3-G4  
**Companion artifacts:** `.pbix`, dashboard screenshots PDF, business insights report (WP-P3-07), final presentation (WP-P3-08)  
**Canonical contracts:** [`AGENTS.md`](../../AGENTS.md), [`Phase3/AGENTS.md`](../AGENTS.md), [`Phase3/PROGRESS.md`](../PROGRESS.md), [`Phase3/DECISIONS.md`](../DECISIONS.md), [`Phase3/docs/04_data_model.md`](04_data_model.md), [`Phase3/docs/06_data_quality_and_reports.md`](06_data_quality_and_reports.md), [`Phase3/docs/13_accepted_data_limitations.md`](13_accepted_data_limitations.md)

> **Read this first.** AeroGrid has a small, real, single-site, single-source, single-month sample. The dashboard must make the pipeline and its coverage limits visible. It must never turn missing coverage into a zero-activity claim, a safety claim, a capacity claim, or a forecast.

---

## 1. Purpose

The dashboard is the decision-support surface for the Phase 3 warehouse. It must do four jobs:

1. **Describe what was observed** — traffic volume, time-of-day pattern, site/source coverage, vehicle concentration, observed 2D occupancy.
2. **Show whether the data can be trusted** — ETL reconciliation, DQ status, rejects, gold-view reconciliation, reader access, capacity, optimization evidence.
3. **Answer the ten Phase 1 business questions honestly** — with `ANSWERED`, `PARTIAL`, `SCREENING ONLY`, or `NOT ANSWERABLE` labels.
4. **Recommend the next decision** — what management can do now and what data must be acquired before operational decisions.

The audience is the course evaluator, the project team, and a management reader who needs a defensible decision. The dashboard is **not** an operational air-traffic, safety, or compliance system.

### 1.1 What “represent the whole project” means

The report must show the full lineage:

```text
Phase 1 business questions
    -> Phase 2 public sources and provenance
    -> staging, rejects, manifests, ETL run log
    -> dimensions and facts (star schema)
    -> Phase 2 reporting views
    -> Phase 3 analytical SQL + ROLLUP/CUBE
    -> Phase 3 gold views
    -> query optimization / indexing evidence
    -> Power BI semantic model
    -> decision brief and business-question scorecard
```

That lineage is represented by:

- Page 1: executive view of observed traffic and coverage.
- Page 2: detailed traffic, time, space, vehicle, and source analysis.
- Page 3: management decision and recommended actions.
- Page 4: coverage, limitations, and the full business-question scorecard.
- Page 5: ETL, DQ, robustness, and data-trust evidence.
- Page 6: methodology, architecture, KPI dictionary, and traceability.
- Page 0: cover and navigation.

---

## 2. Non-negotiable rules

| Rule | Implementation consequence |
|---|---|
| Real data only | Every visual reads a stored view/query or a recorded evidence table. No synthetic rows, no illustrative values, no placeholder trends. |
| Empty is not zero | Every zero KPI carries a visible coverage label. Zero encounters, restrictions, UAS facts, or weather links are “not measured / insufficient evidence,” not “none occurred.” |
| No what-if, forecast, or scenario | Q9 is answered as “not answerable.” Do not add multipliers, projections, trend lines, or simulated corridors. |
| No safety/capacity overclaim | Occupancy is observed 2D vehicle-minutes with a 60-second cap. Candidate cells are screening indicators, not approved corridors. |
| Reader role only | Power BI connects with `aerogrid_reader`; no writer credentials, no embedded secrets, no Service workspace. |
| No raw data in PBIX | Import aggregates and reporting views only. Do not import `fact_vehicle_tracking` row-level data or raw staging payloads. |
| Traceability | Every visual has an ID and cites a view/query and DQ check. `DQ3-A-002` must pass. |
| Reproducibility | Every displayed number can be re-run from the cited query at the recorded data-as-of time. |
| Manual/weekly refresh | No five-minute polling, no scheduled cloud refresh, no real-time claim (`L3-001`). |
| Size guard | `.pbix` and screenshots PDF each under 10 MB (`D3-008`); larger files become GitHub Actions artifacts. |

---

## 3. Evidence snapshot used by this specification

These are the recorded values at the time of design. They are **not** live values. Recompute them at build and capture a new evidence snapshot before publishing.

| Item | Recorded value | Source |
|---|---:|---|
| Tracking positions | 27,479 | `Phase3/evidence/analytics_run_20261118T110136Z.md` |
| Distinct vehicles | 156 | same |
| Vehicle dimension rows | 158 real; 156 with tracking; 2 UAS with no facts | same |
| Journeys | 178 | same |
| Occupancy facts / cell-hours | 1,754 | same |
| Real 2D grid cells | 3,658 | same |
| Sites | 4 real; only `KBTP` observed | same |
| Sources | 3 dimension rows; only `TARTAN` has facts | same |
| Observed months | 1 (`2022-01`) | same |
| Active days | 2 | same |
| Observed hours | 20 of 24 | same |
| Event window | 2022-01-01 08:09:40Z to 2022-01-02 03:59:47Z | same |
| Data as-of | 2026-11-13 12:37:21Z | same |
| Analytics capture | 2026-11-18T11:01:37Z | same |
| Gold-view verify capture | 2026-11-18T11:34:54Z | `Phase3/evidence/gold_views_20261118T113454Z.md` |
| Average altitude | 29,924.13 ft MSL | same |
| Average ground speed | 414.29 kts | same |
| Average journey duration | 145.22 s | same |
| Observed journey distance | 20,497.439 nm | same |
| Occupancy minutes | 86.40 vehicle-minutes | same |
| Average active vehicles / cell-hour | 1.11 | same |
| Peak active vehicles in a cell-hour | 4 | same |
| Detected encounters | 0 | same |
| Restriction activation facts | 0 | same |
| Unknown-weather positions | 27,479 | same |
| Positions missing altitude or speed | 752 | same |
| Top-10 vehicle share | 17.8% | derived from `vw_vehicle_analysis` |
| Top-20 vehicle share | 28.7% | derived from `vw_vehicle_analysis` |
| Positions 15:00–23:59 UTC | 66.7% | derived from `QW-P3-02-06` |
| Positions 12:00–23:59 UTC | 81.6% | derived from `QW-P3-02-06` |
| Peak hour | 17:00 UTC: 3,169 positions / 16 vehicles | same |
| Unobserved window | 04:00–07:59 UTC | same |

### 3.1 Recorded pipeline evidence

| Item | Recorded value | Source |
|---|---:|---|
| WP-11 apply run | `43502710978`, `SUCCESS`, `etl_run_id=11`, 35 s | `Phase2/PROGRESS.md` |
| Rows read / accepted / rejected / duplicate | 23,414 / 23,254 / 160 / 0 | same |
| Manifests | 8 | same |
| DQ results | 36: 32 PASS, 4 WARN, 0 FAIL | same |
| DQ warnings | `DQ-C-003`, `DQ-C-008`, `DQ-A-008`, `DQ-T-003` | same |
| Reject reasons in run 11 | `INVALID_TIMESTAMP=1`, `ZERO_COORDINATE=159` | same |
| Cumulative reject ledger | 578 events (418 prior + 160), spans runs (`L-006`) | `Phase2/PROGRESS.md` |
| UAS staged accepted | 22,602 | `Phase2/PROGRESS.md` |
| Weather staged accepted | 400 | same |
| Airspace staged accepted | 252 | same |
| Database size | 71.72 MiB before WP-P3-05 verify; 71.78 MiB at end | `Phase3/PROGRESS.md` |
| Index candidates | 3, all `NEUTRAL`, 0 applied, 992 KiB avoided | same |
| `DQ3-A-006` | PASS | same |
| Gold-view reconciliation | 3/3 PASS (`DQ3-A-001`) | `Phase3/evidence/gold_views_20261118T113454Z.md` |
| Reader proof | PASS in WP-11 apply run; per-member proof `H-017` remains open | `Phase2/PROGRESS.md` |

> The gold-view verify evidence records `Reader access: NOT_RUN`; the separate H3-005 apply was recorded as reader-proofed. The dashboard must say “reader proof recorded via H3-005” and must not claim that the verify run itself proved reader access.

---

## 4. Business-question scorecard

This is the authoritative status table for the dashboard. It must appear in full on Page 4 and in compact form on Page 3.

| ID | Business question | Status | What the data can say | What is missing | Evidence / limitation |
|---|---|---|---|---|---|
| Q1 | Altitude layer and grid crowding | `PARTIAL` | 3,658 real 2D grid cells; 20 observed hours; KBTP only; peak 17:00 UTC | No physical altitude-band dimension; one site | `L-003`, `L3-002`; `QW-P3-02-06`; `vw_traffic_density_hour_grid` |
| Q2 | Longest-occupied sky zones | `PARTIAL` | Top 2D cells by observed cell-hours / occupancy minutes | 2D only; 60-second occupancy cap; no vertical zones | `L-003`; `vw_corridor_capacity_inputs`; `vw_occupied_grid_hours` |
| Q3 | Traffic volume and height trends | `PARTIAL` | One month, average altitude 29,924.13 ft MSL | No adjacent prior month; growth is `NO_PRIOR_MONTH` | `L3-002`; `vw_monthly_traffic_growth`; `QW-P3-02-01` |
| Q4 | Peak times and manned/UAS mix | `PARTIAL` | Peak 17:00 UTC; 66.7% of positions 15:00–23:59 UTC | UAS has no facts; mix cannot be measured | `L-008`; `QW-P3-02-06`; `vw_source_performance` |
| Q5 | Close-encounter frequency and hotspots | `NOT ANSWERABLE` | 0 detected episodes; exact-timestamp pairing; single loaded source | No reliable encounter evidence; do not trend zero | `L-004`, `L-008`; `fact_close_encounter` = 0 |
| Q6 | Risk-prone vehicle categories | `NOT ANSWERABLE` | No encounters; vehicle type is `UNSPECIFIED` for TARTAN | No encounter facts; no operator identity | `L-004`, `L3-003`; `vw_encounter_vehicle_types` = empty |
| Q7 | Impact of flight restrictions | `NOT ANSWERABLE` | 0 restriction activation facts | No historical restriction snapshot for the study window | `L-005`; `fact_restriction_activation` = 0 |
| Q8 | Weather correlation | `NOT ANSWERABLE` | 27,479 tracking positions have unknown weather keys | No weather linkage on facts | `L-001`; `DQ-C-003`; `vw_weather_operations` |
| Q9 | Corridor capacity stress-test | `NOT ANSWERABLE` | Observed 2D occupancy only; 86.40 vehicle-minutes | No what-if model, no synthetic scenarios, no capacity evidence | `L-003`, `L-007`; `D3-009` |
| Q10 | Candidate drone corridors | `SCREENING ONLY` | Low-observed-traffic 2D cells can be ranked | Not connected routes, not approved, no safety clearance | `L-007`; `vw_candidate_corridor_cells` |

**Summary:** 4 partial, 1 screening-only, 5 not answerable. No question is fully answered by the current sample.

---

## 5. Page architecture

### 5.1 Page map

| Page | Name | Type | Purpose |
|---|---|---|---|
| 00 | Cover | Supporting | Orientation, scope, data-as-of, navigation, attribution |
| 01 | Executive Overview | **Core page 1** | KPIs, one-month trend, hourly rhythm, site/source coverage, headline insight |
| 02 | Detailed Analysis | **Core page 2** | 2A traffic/time/space and 2B fleet/source/space |
| 03 | Decision Brief | **Core page 3** | Decision, readiness, recommended actions, guardrails |
| 04 | Coverage & Question Scorecard | Supporting | Full Q1–Q10 status, zero-coverage semantics, limitations |
| 05 | ETL & Data Trust | Supporting | Pipeline health, DQ, rejects, reconciliation, capacity, optimization |
| 06 | Method & Evidence | Supporting | Architecture, KPI dictionary, traceability, refresh, attribution |

**Core-page rule:** Pages 01, 02, and 03 satisfy the three-page brief. Pages 00, 04, 05, and 06 are supporting evidence pages and must be labeled `SUPPORTING`, not counted as additional core pages. Page 02 uses two bookmark states (2A/2B) so it remains one core page.

### 5.2 Canvas and grid

| Property | Value |
|---|---|
| Canvas | 1600 × 900 px, 16:9 |
| Page background | `#F5F7FA` |
| Outer margin | 24 px |
| Content width | 1552 px |
| Header height | 84 px |
| Navigation bar height | 44 px |
| Footer height | 28 px |
| Card gutter | 12–16 px |
| Standard card radius | 8 px |
| Standard card border | 1 px `#D9E2EC` |
| Standard card shadow | Subtle, 85% transparency, bottom-right |
| Safe text margin inside cards | 16 px |

Coordinates below are implementation targets; keep the grid and gutters consistent if a visual must move by a few pixels.

### 5.3 Header and navigation

**Header (all pages):**

- Navy band `#0B1F33`, full width, 84 px.
- Left: page title, white, Segoe UI Semibold, 20 pt.
- Left second line: scope/subtitle, cyan `#6FD3E8`, 10 pt.
- Right: `Data as of <timestamp> UTC` and `Refresh: manual` in white, 9–10 pt.
- Right: coverage pill, 240 × 24 px:
  - Green `OBSERVED` when the page’s primary scope has facts.
  - Amber `PARTIAL` when the page includes observed + missing coverage.
  - Red `NOT ANSWERABLE` when the page is about absent evidence.
- Supporting pages also show a small gray `SUPPORTING` pill.

**Navigation bar (all pages):**

- White background, 44 px, bottom border `#D9E2EC`.
- Buttons, left to right: `00 Cover`, `01 Executive`, `02 Detailed`, `03 Decision`, `04 Coverage`, `05 Data Trust`, `06 Method`.
- Active button: navy fill, white text.
- Inactive button: transparent fill, slate text.
- Right: `Reset filters` button.
- Use page-navigation buttons, not hyperlinks to local files.
- Do not put credentials, hostnames, or connection strings in navigation labels.

### 5.4 Global filters

| Slicer | Field | Placement | Behavior |
|---|---|---|---|
| Site | `Site[site_code]` | Page 2 filter bar; optional page 1 | All 4 real sites visible; selecting a zero-coverage site must show a coverage message, not a zero-activity conclusion |
| Month | `Month[Month]` | Page 2 filter bar | Single observed month; label “1 observed month” |
| Source | `SourceDim[source_system]` | Page 2 filter bar | All 3 sources visible; UAS sources show no-fact coverage labels |
| Vehicle type | `Vehicle[vehicle_type_label]` | Page 2B | Only `UNSPECIFIED` and UAS rows; do not imply real operator segments |
| Hour band | `HourBand[Band]` derived from UTC hour | Page 2A | Bands: `00–03`, `04–07`, `08–11`, `12–15`, `16–19`, `20–23` |
| Observed only | Toggle / bookmark | Page 2 | Optional; default off so coverage gaps remain visible |

**Filter rules:**

- Do not add a “date range” slicer that implies continuous daily coverage. Use the observed month and observed dates only.
- Do not default-filter to `KBTP`; show the coverage gap by default, then let the user filter.
- Preserve zero/coverage rows in the semantic model. Do not remove zero-fact source or vehicle rows with Power Query filters.
- Exclude `-1` unknown dimension members from normal visuals; show unknown coverage through labels and audit cards, not as a real site/vehicle.

### 5.5 Bookmarks

| Bookmark | Purpose |
|---|---|
| `BM_2A_Traffic` | Show Page 2A container; hide 2B |
| `BM_2B_Fleet` | Show Page 2B container; hide 2A |
| `BM_Reset` | Clear slicers and return to the default page state |
| `BM_ShowCoverageNotes` | Reveal coverage-note panel on Pages 1–4 |
| `BM_ShowEvidence` | Reveal evidence citations on Page 3 or 6 |

Use the Selection pane to group objects: `Header`, `Nav`, `KPI`, `Visuals`, `Notes`, `Footer`. Name every object with its visual ID so reviewers can audit the PBIX.

### 5.6 Drill-through and tooltips

| From | To | Fields | Purpose |
|---|---|---|---|
| Site matrix | Page 2A | `site_code` | Inspect one site’s time/space pattern |
| Source matrix | Page 2B | `source_system` | Inspect one source’s vehicles/journeys |
| Vehicle table / scatter | Hidden vehicle detail page | `vehicle_key` | Inspect one source-scoped vehicle |
| Grid cell bar/table | Hidden grid-cell detail page | `grid_key` | Inspect 2D occupancy and caveats |
| DQ matrix | Hidden DQ detail page | `check_id` | Inspect all 36 checks |
| Question scorecard | Page 3 | `question_id` | Move from evidence to decision |

Custom tooltip pages are listed in Section 16.

---

## 6. Semantic model

### 6.1 Connection and storage mode

| Setting | Value |
|---|---|
| Connector | PostgreSQL database connector |
| Role | `aerogrid_reader` |
| Database | `neondb` |
| Mode | Import |
| Query folding | Not required; all sources are views/aggregates |
| Credentials | Entered by the author at refresh; never saved in the repo or screenshots |
| Auto date/time | Disabled |
| Date table | `Date` marked as date table |
| Refresh | Manual in Power BI Desktop; no Service schedule (`L3-001`) |
| PBIX handling | Derived artifact; do not commit if it contains credentials; follow `D3-008` |

**Why Import:** the data volume is small, the source is a cloud PostgreSQL free tier, and DirectQuery would add latency and credential exposure without a benefit. Import also makes screenshots reproducible after refresh.

### 6.2 Tables and grains

Use these report-table names. The source object is the traceability link.

| Report table | Source object | Grain | Key fields | Use | Caveat |
|---|---|---|---|---|---|
| `KPI` | `QW-P3-02-02` native query | One row | `tracking_positions`, `distinct_vehicles`, `journeys_observed`, `detected_encounters`, `data_as_of_utc` | Executive KPI cards | Unfiltered snapshot; cite query |
| `Monthly` | `project_reporting.vw_monthly_traffic_growth` | Site-month | `month_utc`, `site_key` | Monthly volume, altitude, growth | 1 row; growth `NO_PRIOR_MONTH` |
| `MonthlySimple` | `project_reporting.vw_monthly_traffic` | Site-month | `month_utc`, `site_key` | Optional cross-check | Same grain; do not double count |
| `Vehicle` | `project_reporting.vw_vehicle_analysis` | Vehicle | `vehicle_key` | Vehicle concentration, scatter, top table | Source-scoped identity, not operator (`L3-003`) |
| `Source` | `project_reporting.vw_source_performance` | Source | `source_system` | Source coverage, journeys, observed months | UAS rows have zero facts (`L-008`) |
| `HourlyGrid` | `project_reporting.vw_traffic_density_hour_grid` | Hour-site-cell | `time_key`, `site_key`, `grid_key` | Hourly heatmap, position-weighted averages | 2D cells; no altitude band |
| `Occupancy` | `project_reporting.vw_occupied_grid_hours` | Hour-site-cell | `time_key`, `site_key`, `grid_key` | Occupied cell-hours, occupancy minutes, active vehicles | 2D; 60 s cap (`L-003`) |
| `PeakHours` | `project_reporting.vw_peak_site_hours` | Site-hour | `site_key`, `hour_ts` | Peak hour, source counts | Report source counts, not operator mix |
| `Corridor` | `project_reporting.vw_corridor_capacity_inputs` | Site-cell | `site_key`, `grid_key` | Top occupied cells, screening | Not capacity, not a corridor |
| `Candidate` | `project_reporting.vw_candidate_corridor_cells` | Site-cell | `site_key`, `grid_key` | Q10 screening table | Screening only (`L-007`) |
| `WeatherOps` | `project_reporting.vw_weather_operations` | Site-weather key | `site_key`, `weather_key` | Weather coverage card | All current keys unknown (`L-001`) |
| `EncounterDaily` | `project_reporting.vw_daily_encounter_hotspots` | Day-site-cell | `encounter_day_utc`, `site_key`, `grid_key` | Q5 zero card | Empty; not proof of no encounters |
| `EncounterTypes` | `project_reporting.vw_encounter_vehicle_types` | Encounter | `encounter_id` | Q6 reference | Empty |
| `Restriction` | `project_reporting.vw_restriction_traffic_impact` | Activation | `activation_id` | Q7 zero card | Empty; no historical snapshot |
| `Site` | `project_dw.dim_site` | Site | `site_key` | Site slicer/matrix | 4 real + unknown; exclude unknown |
| `Time` | `project_dw.dim_time` | UTC hour | `time_key` | Hour/date attributes | Minimal columns; derive bands |
| `Date` | DAX `CALENDAR` from min/max event date | Date | `Date` | Date table | Mark as date table |
| `Month` | Distinct `Monthly[month_utc]` | Month | `MonthStart` | Monthly axis | One row currently |
| `SourceDim` | Distinct `Source` | Source | `source_system` | Source slicer | 3 rows |
| `Grid` | `project_dw.dim_spatial_grid` | Grid cell | `grid_key` | Grid drill-through | 3,658 real + unknown |
| `DQ` | `project_staging.dq_result` | DQ check per run | `check_id`, `etl_run_id` | Data Trust | 36 rows for run 11 |
| `Run` | `project_staging.etl_run_log` (latest) | ETL run | `etl_run_id` | Run status/counts | Latest only |
| `Manifest` | `project_staging.source_manifest` | Manifest | `source_manifest_id` | Provenance count | 8 rows |
| `RejectSummary` | Grouped `project_staging.stg_reject` | Reason/source/run | `reason_code`, `source_system` | Reject Pareto | Run 11 and cumulative must be separated (`L-006`) |
| `Coverage` | `QW-P3-02-07` native query | One row | coverage fields | Coverage diagnostics | One row |
| `QuestionScorecard` | Static reference table from Phase 1/Phase 3 docs | Question | `question_id` | Q1–Q10 | Documentation, not a measure |
| `Evidence` | Static recorded-evidence table | Evidence item | `evidence_id` | Reader proof, DB size, index verdict, gold reconciliation | Label “recorded evidence snapshot” |
| `IndexEvidence` | Static table from WP-P3-05 PDF | Index candidate | `candidate_id` | Optimization card | 3 rows, all `NEUTRAL` |
| `EtlCoverage` | Aggregated from `Manifest` / `Run` / staging counts | Source/site | `source_system` | Staged vs facts coverage | Use recorded counts; no raw rows |

**Do not import:** `fact_vehicle_tracking` row-level, `fact_flight_journey` row-level, `stg_adsb_position`, `stg_uas_position`, raw METAR, raw airspace payloads, or any raw file. If a visual needs a row-level drill-through, build a narrow aggregate query or a hidden supporting page from the view, not the raw fact.

### 6.3 Relationships

| From | To | Cardinality | Filter | Active |
|---|---|---|---|---|
| `Monthly[site_key]` | `Site[site_key]` | Many-to-one | Single | Yes |
| `Monthly[month_utc]` | `Month[MonthStart]` | Many-to-one | Single | Yes |
| `HourlyGrid[time_key]` | `Time[time_key]` | Many-to-one | Single | Yes |
| `HourlyGrid[site_key]` | `Site[site_key]` | Many-to-one | Single | Yes |
| `HourlyGrid[grid_key]` | `Grid[grid_key]` | Many-to-one | Single | Yes |
| `Occupancy[time_key]` | `Time[time_key]` | Many-to-one | Single | Yes |
| `Occupancy[site_key]` | `Site[site_key]` | Many-to-one | Single | Yes |
| `Occupancy[grid_key]` | `Grid[grid_key]` | Many-to-one | Single | Yes |
| `PeakHours[site_key]` | `Site[site_key]` | Many-to-one | Single | Yes |
| `Corridor[site_key]` | `Site[site_key]` | Many-to-one | Single | Yes |
| `Corridor[grid_key]` | `Grid[grid_key]` | Many-to-one | Single | Yes |
| `Candidate[site_key]` | `Site[site_key]` | Many-to-one | Single | Yes |
| `Candidate[grid_key]` | `Grid[grid_key]` | Many-to-one | Single | Yes |
| `WeatherOps[site_key]` | `Site[site_key]` | Many-to-one | Single | Yes |
| `Vehicle[source_system]` | `SourceDim[source_system]` | Many-to-one | Single | Yes |
| `Source[source_system]` | `SourceDim[source_system]` | Many-to-one | Single | Yes |
| `Time[date_utc]` | `Date[Date]` | Many-to-one | Single | Yes |
| `DQ[etl_run_id]` | `Run[etl_run_id]` | Many-to-one | Single | Yes |
| `RejectSummary[etl_run_id]` | `Run[etl_run_id]` | Many-to-one | Single | Yes |

**Relationship rules:**

- Keep `Monthly` and `MonthlySimple` disconnected from each other; use `Monthly` for visuals and `MonthlySimple` only for a cross-check card.
- Do not create active relationships from `EncounterTypes` to `Vehicle` twice; if used, leave it disconnected or use role-playing inactive relationships. The table is empty, so a table visual is sufficient.
- Do not create a relationship between `WeatherOps[weather_key]` and tracking facts; the weather keys are unknown and the view is already aggregated.
- Use single-direction filters. Avoid many-to-many relationships.
- Hide all surrogate keys from the report view after relationships are set.

### 6.4 Power Query steps

1. Connect with the PostgreSQL connector using `aerogrid_reader`; use the reader connection details from the approved private setup. Do not paste connection strings into the PBIX, repo, screenshots, or chat.
2. Load the reporting views and the audit tables listed in Section 6.2.
3. Set data types explicitly:
   - Keys: whole number, do not summarize.
   - Counts: whole number.
   - Measures: decimal number.
   - Timestamps: date/time with time zone converted to UTC display.
   - `month_utc`: date.
   - `data_as_of_utc`: date/time.
4. Add `HourBand` from `Time[hour_utc]`:
   - `00–03`, `04–07`, `08–11`, `12–15`, `16–19`, `20–23`.
5. Add `Date` as a calculated table:
   - `CALENDAR (MIN('Time'[date_utc]), MAX('Time'[date_utc]))`.
   - Add `Year`, `Quarter`, `Month`, `MonthName`, `Day`, `DayOfWeek`, `IsWeekend`.
6. Add `Month` as a distinct table from `Monthly[month_utc]` with `MonthStart`, `MonthLabel`, `MonthYear`.
7. Add `SourceDim` as distinct `source_system` + `source_category` from `Source`.
8. Add `RejectSummary` by grouping `stg_reject` by `etl_run_id`, `source_system`, `reason_code`; count rows. Do not import the reject payload.
9. Add `LatestRun` as `Table.FirstN(Table.Sort(Run, {{"etl_run_id", Order.Descending}}), 1)`.
10. Disable load for any staging query not used by an aggregate.
11. Hide technical columns and tables from the report view.
12. Set `Site[site_code]`, `SourceDim[source_system]`, `Vehicle[source_entity_id]`, and `Grid[grid_cell_id]` as the user-facing labels.
13. Set `QuestionScorecard[question_id]` sort by a numeric `question_order` column.
14. Set `Month[MonthStart]` sort by `MonthStart`; set `HourBand[Band]` sort by `BandOrder`.
15. Disable auto date/time and Q&A if the model is intended for evaluator screenshots only. If Q&A is enabled, add synonyms and verify that it cannot invent answers.

### 6.5 Static reference tables

Static tables are allowed only for **recorded evidence** and **documentation**, never for KPI values that should come from the warehouse.

| Table | Rows | Fields | Source | Label |
|---|---:|---|---|---|
| `QuestionScorecard` | 10 | `question_id`, `question_short`, `status`, `what_we_can_say`, `what_is_missing`, `evidence`, `limitation` | Phase 1 business questions + Phase 3 docs | “Documentation table” |
| `Evidence` | ~8 | `evidence_id`, `captured_at_utc`, `evidence`, `value`, `status`, `source` | WP-11 run, H3-005, WP-P3-05 PDF, gold evidence | “Recorded evidence snapshot” |
| `IndexEvidence` | 3 | `candidate_id`, `query_id`, `before_ms`, `after_ms`, `cost_before`, `cost_after`, `index_kib`, `verdict` | `Phase3/reports/Indexing_Report.pdf` | “Measured, not benchmarked” |

Every static table must show its capture date and source citation in the page footer or tooltip. Refresh the static table when a new run supersedes it.

`Evidence[value]` is stored as invariant text; numeric values (for example `71.78`) are converted in DAX. Keep units in a separate label and never use `MAX` across mixed evidence values.

---

## 7. KPI dictionary and DAX

### 7.1 KPI definitions

| KPI | Definition | Source | Zero/empty semantics | DQ link |
|---|---|---|---|---|
| Observed tracking positions | Count of tracking rows in scope | `fact_vehicle_tracking` via views | 0 = missing coverage; label required | `DQ3-A-003` |
| Distinct vehicles observed | Distinct `vehicle_key` in scope | `fact_vehicle_tracking` | 0 = missing coverage; source-scoped | `L3-003` |
| Journeys observed | Count of journey rows | `fact_flight_journey` | 0 = missing coverage; not “no flights” | `DQ3-A-003` |
| Occupied cell-hours | Count of occupancy rows | `fact_airspace_occupancy` | 0 = missing coverage; 2D/60 s cap | `L-003` |
| Occupancy minutes | Sum of `total_occupancy_minutes` | occupancy | Observed vehicle-minutes, not capacity | `L-003` |
| Average active vehicles / cell-hour | Sum active / count cell-hours | occupancy | Observed, not capacity | `L-003` |
| Peak active vehicles | Max `active_vehicle_count` | occupancy | Observed peak, not capacity | `L-003` |
| Average altitude | Position-weighted average of `avg_altitude_msl_ft` | tracking/hourly view | Null when no valid rows | `DQ-A-004` |
| Average speed | Position-weighted average of `avg_ground_speed_kts` | tracking/hourly view | Null when no valid rows | `DQ-A-005` |
| Month-over-month growth | `(current − prior) / prior` | `vw_monthly_traffic_growth` | Null when no prior/adjacent/zero; never ±∞ | `DQ3-A-001` |
| Detected encounters | Count of encounter rows | `fact_close_encounter` | 0 = no detected episodes AND insufficient overlapping evidence | `L-004`, `L-008` |
| Restriction activations | Count of activation rows | `fact_restriction_activation` | 0 = no snapshot coverage | `L-005` |
| Unknown-weather share | Unknown weather positions / total positions | `vw_weather_operations` | 100% = no linkage | `DQ-C-003` |
| Top-10 vehicle share | Sum top 10 vehicle positions / total | `vw_vehicle_analysis` | Descriptive concentration only | `L3-003` |
| DQ pass/warn/fail | Count of DQ rows by status | `dq_result` | 0 FAIL does not mean perfect data | `DQ3-A-002` |
| Reader proof | Recorded read-only check | WP-11 run / H3-005 | Recorded evidence, not live | `H-017` caveat |
| Index verdict | Measured before/after verdict | WP-P3-05 | `NEUTRAL` means no claimed speed-up | `DQ3-A-006` |

### 7.2 DAX measures

Create these measures in a dedicated `_Measures` table. Use `DIVIDE` to avoid divide-by-zero. Use `BLANK()` for missing, not 0.

```DAX
Observed Positions (KPI) =
MAX ( 'KPI'[tracking_positions] )

Observed Vehicles (KPI) =
MAX ( 'KPI'[distinct_vehicles] )

Observed Journeys (KPI) =
MAX ( 'KPI'[journeys_observed] )

Observed Occupancy Minutes (KPI) =
MAX ( 'KPI'[observed_occupancy_minutes] )

Detected Encounters (KPI) =
COALESCE ( MAX ( 'KPI'[detected_encounters] ), 0 )

Data As Of =
MAX ( 'KPI'[data_as_of_utc] )

Data As Of Label =
"Data as of " & FORMAT ( [Data As Of], "yyyy-mm-dd hh:mm" ) & " UTC"

First Event =
MAX ( 'KPI'[first_event_ts] )

Last Event =
MAX ( 'KPI'[last_event_ts] )

Observed Positions (Site) =
COALESCE ( SUM ( 'Monthly'[tracking_positions] ), 0 )

Observed Vehicles (Site-Month) =
COALESCE ( SUM ( 'Monthly'[distinct_vehicles] ), 0 )

Observed Positions (Source) =
COALESCE ( SUM ( 'Source'[tracking_positions] ), 0 )

Observed Journeys (Source) =
COALESCE ( SUM ( 'Source'[journeys_observed] ), 0 )

Observed Positions (Vehicle) =
COALESCE ( SUM ( 'Vehicle'[tracking_positions] ), 0 )

Observed Journeys (Vehicle) =
COALESCE ( SUM ( 'Vehicle'[journeys_observed] ), 0 )

Observed Occupancy Minutes =
COALESCE ( SUM ( 'Occupancy'[total_occupancy_minutes] ), 0 )

Occupied Cell-Hours =
COUNTROWS ( 'Occupancy' )

Average Active Vehicles per Cell-Hour =
DIVIDE (
    SUM ( 'Occupancy'[active_vehicle_count] ),
    COUNTROWS ( 'Occupancy' )
)

Peak Active Vehicles =
MAX ( 'Occupancy'[active_vehicle_count] )

Average Altitude (Weighted) =
DIVIDE (
    SUMX (
        'HourlyGrid',
        'HourlyGrid'[avg_altitude_msl_ft] * 'HourlyGrid'[tracking_positions]
    ),
    SUMX ( 'HourlyGrid', 'HourlyGrid'[tracking_positions] )
)

Average Speed (Weighted) =
DIVIDE (
    SUMX (
        'HourlyGrid',
        'HourlyGrid'[avg_speed_kts] * 'HourlyGrid'[tracking_positions]
    ),
    SUMX ( 'HourlyGrid', 'HourlyGrid'[tracking_positions] )
)

Observed Hours =
DISTINCTCOUNT ( 'HourlyGrid'[time_key] )

Active Days =
DISTINCTCOUNT ( 'Time'[date_utc] )

Sites with Tracking =
COUNTROWS (
    FILTER (
        VALUES ( 'Site'[site_code] ),
        [Observed Positions (Site)] > 0
    )
)

Sources with Facts =
COUNTROWS (
    FILTER (
        VALUES ( 'SourceDim'[source_system] ),
        [Observed Positions (Source)] > 0
    )
)

Site Coverage Status =
IF (
    [Observed Positions (Site)] > 0,
    "OBSERVED",
    "NO TRACKING COVERAGE - not proof of no activity"
)

Source Coverage Status =
IF (
    [Observed Positions (Source)] > 0,
    "OBSERVED",
    "NO TRACKING COVERAGE - not proof of inactivity"
)

MoM Growth =
IF (
    SELECTEDVALUE ( 'Monthly'[mom_growth_status] ) = "COMPUTED",
    MAX ( 'Monthly'[mom_growth_pct] ),
    BLANK ()
)

MoM Growth Label =
SWITCH (
    SELECTEDVALUE ( 'Monthly'[mom_growth_status], "NO OBSERVED MONTH" ),
    "COMPUTED", FORMAT ( [MoM Growth], "0.0%" ),
    "NO_PRIOR_MONTH", "N/A - no prior month",
    "NO_ADJACENT_PRIOR_MONTH", "N/A - no adjacent prior month",
    "PRIOR_MONTH_ZERO", "N/A - prior month zero",
    "NO OBSERVED MONTH"
)

Peak Hour UTC =
VAR _Top =
    TOPN (
        1,
        VALUES ( 'PeakHours'[hour_ts] ),
        CALCULATE ( SUM ( 'PeakHours'[tracking_positions] ) ), DESC
    )
RETURN
    MAXX ( _Top, FORMAT ( 'PeakHours'[hour_ts], "HH:00" ) )

Peak Hour Positions =
MAXX (
    TOPN (
        1,
        'PeakHours',
        SUM ( 'PeakHours'[tracking_positions] ), DESC
    ),
    SUM ( 'PeakHours'[tracking_positions] )
)

Peak Hour Vehicles =
MAXX (
    TOPN (
        1,
        'PeakHours',
        SUM ( 'PeakHours'[tracking_positions] ), DESC
    ),
    SUM ( 'PeakHours'[observed_vehicles] )
)

Unknown Weather Share =
DIVIDE (
    SUMX (
        FILTER ( 'WeatherOps', 'WeatherOps'[weather_unknown] = TRUE ),
        'WeatherOps'[tracking_positions]
    ),
    SUM ( 'WeatherOps'[tracking_positions] )
)

Encounter Count =
COALESCE ( SUM ( 'EncounterDaily'[detected_encounters] ), 0 )

Encounter Evidence Label =
"ZERO - no detected episodes AND insufficient overlapping evidence (L-004, L-008); not proof of no encounters"

Restriction Count =
COUNTROWS ( 'Restriction' )

UAS Fact Positions =
CALCULATE (
    [Observed Positions (Source)],
    'SourceDim'[source_category] = "UAS"
)

Top 10 Vehicle Share =
VAR _Total = SUM ( 'Vehicle'[tracking_positions] )
VAR _Top =
    SUMX (
        TOPN ( 10, 'Vehicle', 'Vehicle'[tracking_positions], DESC ),
        'Vehicle'[tracking_positions]
    )
RETURN
    DIVIDE ( _Top, _Total )

Top 20 Vehicle Share =
VAR _Total = SUM ( 'Vehicle'[tracking_positions] )
VAR _Top =
    SUMX (
        TOPN ( 20, 'Vehicle', 'Vehicle'[tracking_positions], DESC ),
        'Vehicle'[tracking_positions]
    )
RETURN
    DIVIDE ( _Top, _Total )

Vehicle Rank =
RANKX (
    ALLSELECTED ( 'Vehicle'[vehicle_key] ),
    [Observed Positions (Vehicle)],
    ,
    DESC,
    DENSE
)

Cumulative Vehicle Positions =
VAR _Rank = [Vehicle Rank]
RETURN
    SUMX (
        FILTER (
            ALLSELECTED ( 'Vehicle' ),
            [Vehicle Rank] <= _Rank
        ),
        [Observed Positions (Vehicle)]
    )

Cumulative Vehicle Share =
DIVIDE (
    [Cumulative Vehicle Positions],
    CALCULATE ( [Observed Positions (Vehicle)], ALLSELECTED ( 'Vehicle' ) )
)

Latest Run ID =
MAX ( 'Run'[etl_run_id] )

Rows Read =
SUM ( 'Run'[rows_read] )

Rows Accepted =
SUM ( 'Run'[rows_accepted] )

Rows Rejected =
SUM ( 'Run'[rows_rejected] )

Rows Duplicate =
SUM ( 'Run'[rows_duplicate] )

Reject Rate =
DIVIDE ( [Rows Rejected], [Rows Read] )

DQ Pass =
CALCULATE ( COUNTROWS ( 'DQ' ), 'DQ'[status] = "PASS" )

DQ Warn =
CALCULATE ( COUNTROWS ( 'DQ' ), 'DQ'[status] = "WARN" )

DQ Fail =
CALCULATE ( COUNTROWS ( 'DQ' ), 'DQ'[status] = "FAIL" )

DQ Total =
COUNTROWS ( 'DQ' )

Manifest Count =
COUNTROWS ( 'Manifest' )

Database Size MiB =
VAR _Value =
    LOOKUPVALUE (
        'Evidence'[value],
        'Evidence'[evidence_id], "DB_SIZE_MIB"
    )
RETURN
    IF ( ISBLANK ( _Value ), BLANK (), VALUE ( _Value ) )

Database Guard % =
DIVIDE ( [Database Size MiB], 700 )

Reader Proof =
LOOKUPVALUE (
    'Evidence'[value],
    'Evidence'[evidence_id], "READER_PROOF"
)

Index Verdict =
LOOKUPVALUE (
    'Evidence'[value],
    'Evidence'[evidence_id], "INDEX_VERDICT"
)
```

**Measure caveat:** `Observed Vehicles (Site-Month)` sums monthly distinct counts. It is correct for the one-month sample; do not present it as a distinct count across multiple months. If multi-month coverage arrives, use a vehicle-site bridge or a dedicated query and label the change.

### 7.3 Format strings

| Measure type | Format |
|---|---|
| Counts | `#,##0` |
| Distance | `#,##0.000 "nm"` |
| Altitude | `#,##0 "ft MSL"` |
| Speed | `#,##0.0 "kts"` |
| Minutes | `#,##0.00 "min"` |
| Percent | `0.0%` |
| Date | `yyyy-mm-dd` |
| Timestamp | `yyyy-mm-dd hh:mm "UTC"` |
| Missing | `BLANK()` or `N/A` with a reason, never `0` |

### 7.4 Coverage-label rules

| Situation | Label | Color | Do not say |
|---|---|---|---|
| Facts exist for scope | `OBSERVED` | Green `#2E8B57` | “Complete” |
| Facts exist but method/coverage limited | `PARTIAL` | Amber `#F2A900` | “Full answer” |
| Zero rows because no source/fact coverage | `NO COVERAGE` | Red `#D64545` | “Zero activity” |
| Encounter/restriction zero | `NOT PROOF OF ZERO` | Red/amber | “No incidents” |
| Hour/cell not observed | `UNOBSERVED` | Gray `#8EA9C1` | “0” |
| Candidate corridor | `SCREENING ONLY` | Purple `#7B61FF` | “Approved corridor” |
| Source-scoped vehicle | `SOURCE-SCOPED ID` | Slate `#5B6B7C` | “Operator” |

Every KPI card and every zero-bearing visual must include one of these labels in the visual, not only in a tooltip. `DQ3-A-003` fails if an unlabeled zero is visible.

---

## 8. Theme and visual language

### 8.1 Palette

| Token | Hex | Use |
|---|---|---|
| Navy | `#0B1F33` | Header, titles, primary text, active navigation |
| Blue | `#2E86C1` | Primary data series, observed traffic |
| Cyan | `#6FD3E8` | Secondary accent, subtitles, highlights |
| Amber | `#F2A900` | Partial coverage, warnings, peak callout |
| Purple | `#7B61FF` | Screening/candidate visuals |
| Green | `#2E8B57` | PASS / observed / read-only success |
| Red | `#D64545` | FAIL / no coverage / “not proof of zero” |
| Slate | `#5B6B7C` | Secondary text, source-scoped identity |
| Light slate | `#8EA9C1` | Unobserved/missing cells, secondary bars |
| Background | `#F5F7FA` | Canvas |
| Card | `#FFFFFF` | Visual background |
| Border | `#D9E2EC` | Card and table borders |
| Text | `#1B2A38` | Body text |
| Muted text | `#5B6B7C` | Captions, footnotes |

**Color rules:**

- Use blue for observed data, gray for unobserved, amber for partial/peak, red for absent/unsafe-to-infer, purple for screening.
- Never use red for observed values or green for zeros.
- Never rely on color alone: include a text status.
- Use a maximum of three colors in one chart unless a legend is present.
- Use data labels for KPI cards and bar charts; use tooltips for dense heatmaps.

### 8.2 Theme JSON

Save as `AeroGrid-Observatory.json` and import in Power BI Desktop under **View → Themes → Browse for themes**.

```json
{
  "name": "AeroGrid Observatory",
  "dataColors": [
    "#2E86C1",
    "#6FD3E8",
    "#F2A900",
    "#7B61FF",
    "#2E8B57",
    "#D64545",
    "#5B6B7C",
    "#8EA9C1",
    "#C9A227",
    "#4C9F70"
  ],
  "background": "#F5F7FA",
  "foreground": "#1B2A38",
  "tableAccent": "#0B1F33",
  "textClasses": {
    "callout": {
      "fontSize": 32,
      "fontFace": "Segoe UI Semibold",
      "color": "#0B1F33"
    },
    "title": {
      "fontSize": 20,
      "fontFace": "Segoe UI Semibold",
      "color": "#0B1F33"
    },
    "header": {
      "fontSize": 12,
      "fontFace": "Segoe UI Semibold",
      "color": "#1B2A38"
    },
    "label": {
      "fontSize": 10,
      "fontFace": "Segoe UI",
      "color": "#5B6B7C"
    }
  },
  "visualStyles": {
    "*": {
      "*": {
        "background": [
          {
            "show": true,
            "color": {
              "solid": {
                "color": "#FFFFFF"
              }
            },
            "transparency": 0
          }
        ],
        "border": [
          {
            "show": true,
            "color": {
              "solid": {
                "color": "#D9E2EC"
              }
            },
            "radius": 8
          }
        ],
        "dropShadow": [
          {
            "show": true,
            "color": {
              "solid": {
                "color": "#0B1F33"
              }
            },
            "position": "BottomRight",
            "preset": "BottomRight",
            "transparency": 85
          }
        ]
      }
    }
  }
}
```

If the installed Desktop version rejects a `visualStyles` key, remove only that block and apply the card styling manually. The color tokens and text classes are the contract; the exact shadow schema is not.

### 8.3 Typography

| Element | Font | Size | Weight | Color |
|---|---|---|---:|---|
| Page title | Segoe UI Semibold | 20 | Semibold | White |
| Page subtitle | Segoe UI | 10 | Regular | `#6FD3E8` |
| Card title | Segoe UI Semibold | 12–14 | Semibold | `#0B1F33` |
| KPI value | Segoe UI Semibold | 28–32 | Semibold | `#0B1F33` |
| KPI label | Segoe UI | 9–10 | Regular | `#5B6B7C` |
| Body | Segoe UI | 10–11 | Regular | `#1B2A38` |
| Table header | Segoe UI Semibold | 9–10 | Semibold | White on navy |
| Table body | Segoe UI | 9 | Regular | `#1B2A38` |
| Footnote | Segoe UI | 8–9 | Regular | `#5B6B7C` |
| Tooltip title | Segoe UI Semibold | 11 | Semibold | `#0B1F33` |
| Tooltip body | Segoe UI | 9 | Regular | `#1B2A38` |

### 8.4 Card standards

- White background, 1 px border, 8 px radius, 16 px inner padding.
- Card title top-left; optional status pill top-right.
- KPI value large; subtitle explains source/coverage; footer cites query ID.
- No decorative icons that imply an unmeasured state.
- No gauge charts. No speedometer. No “health score” invented from arbitrary weights.
- Use `OBSERVED`, `PARTIAL`, `NO COVERAGE`, `NOT PROOF OF ZERO`, `SCREENING ONLY` pills.

### 8.5 Chart selection rules

| Need | Use | Avoid |
|---|---|---|
| One observed month | Column chart with one bar and a “no prior month” note | Line chart with one point, trend line, forecast |
| Hour-of-day pattern | Column chart with 24 categories, blank missing hours; heatmap for date × hour | Continuous line that interpolates missing hours |
| Site/source coverage | Matrix/table with status text | Pie/donut that hides zero-coverage categories |
| Vehicle concentration | Pareto (bars + cumulative % line) | Pie chart of 156 slices |
| Vehicle behavior | Scatter (altitude vs speed, size = positions) | 3D scatter, bubble animation |
| Top occupied cells | Horizontal bar, top 15 | Map that implies routes/corridors |
| DQ status | Matrix/table by severity/status + WARN detail | Gauge or single “quality score” |
| Rejects | Pareto by reason/source | Stacked area |
| Pipeline flow | Shapes/text ribbon with counts | Sankey with invented flows |
| Question status | Table with status pills | Radar chart or score |

**No map by default.** If a map is added, use a scatter of cell centers with a visible note: “Observed 2D cell centers; not flight paths, routes, or corridors.” Do not use a live traffic map or a basemap that implies real-time tracking.

---

## 9. Page 00 — Cover

**Purpose:** orient the reader in under 30 seconds and provide navigation.

### 9.1 Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| Header band | `P00-HDR` | Shape | 0 | 0 | 1600 | 84 |
| Title | `P00-TITLE` | Text | 24 | 18 | 900 | 30 |
| Subtitle | `P00-SUB` | Text | 24 | 50 | 900 | 18 |
| Scope card | `P00-SCOPE` | Card | 24 | 120 | 760 | 220 |
| Read-me card | `P00-README` | Card | 808 | 120 | 768 | 220 |
| Navigation tiles | `P00-NAV-01` … `P00-NAV-04` | Buttons | 24 | 372 | 370 | 120 |
| Evidence strip | `P00-EVID` | Card | 24 | 516 | 1552 | 220 |
| Footer | `P00-FOOT` | Text | 24 | 860 | 1552 | 24 |

### 9.2 Content

**Title:** `AeroGrid — Observed Airspace Intelligence`  
**Subtitle:** `Phase 3 decision-support dashboard · Tartan ADS-B · KBTP · 2022-01`

**Scope card:**

- `27,479` source-linked tracking positions.
- `156` observed vehicle identities; `178` journeys; `1,754` occupied 2D cell-hours.
- `1` site with tracking (`KBTP`) of `4`; `1` source with facts (`TARTAN`) of `3`.
- `1` observed month; `2` active days; `20` observed hours.
- Data as-of `2026-11-13 12:37 UTC`; refresh is manual.

**Read-me card:**

1. This is observed data, not real-time data.
2. Empty coverage is labeled; it is not zero activity.
3. No safety, capacity, weather-impact, restriction, or corridor conclusion is supported by this sample.
4. Every number cites a stored query or recorded evidence item.

**Navigation tiles:**

- `01 Executive Overview` — “What did we observe?”
- `02 Detailed Analysis` — “Where, when, who, and which source?”
- `03 Decision Brief` — “What should management do?”
- `04–06 Supporting` — “Coverage, data trust, method.”

**Evidence strip:** a compact timeline:

```text
Phase 1 questions -> Phase 2 warehouse -> Phase 3 analytics -> BI decision support
```

with a note: `Phase 2 facts are unchanged; Phase 3 reads through project_reporting and aerogrid_reader.`

**Footer:** source attribution and `P3-BI-SPEC-001`.

---

## 10. Page 01 — Executive Overview (Core page 1)

**Purpose:** give a management reader the observed picture and its limits without requiring them to understand the warehouse.

### 10.1 Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| Header | `P01-HDR` | Shared header | 0 | 0 | 1600 | 84 |
| Nav | `P01-NAV` | Shared nav | 0 | 84 | 1600 | 44 |
| KPI 01 | `P01-KPI-01` | Card | 24 | 144 | 248 | 112 |
| KPI 02 | `P01-KPI-02` | Card | 284 | 144 | 248 | 112 |
| KPI 03 | `P01-KPI-03` | Card | 544 | 144 | 248 | 112 |
| KPI 04 | `P01-KPI-04` | Card | 804 | 144 | 248 | 112 |
| KPI 05 | `P01-KPI-05` | Card | 1064 | 144 | 248 | 112 |
| KPI 06 | `P01-KPI-06` | Card | 1324 | 144 | 252 | 112 |
| Monthly chart | `P01-V01` | Column chart | 24 | 272 | 760 | 248 |
| Hourly chart | `P01-V02` | Column chart | 808 | 272 | 768 | 248 |
| Site matrix | `P01-V03` | Matrix | 24 | 536 | 496 | 300 |
| Source matrix | `P01-V04` | Matrix | 536 | 536 | 496 | 300 |
| Insight card | `P01-V05` | Text card | 1048 | 536 | 528 | 300 |
| Footer | `P01-FOOT` | Text | 24 | 860 | 1552 | 24 |

### 10.2 KPI cards

| ID | Value | Label | Subtitle / coverage |
|---|---:|---|---|
| `P01-KPI-01` | 27,479 | Observed tracking positions | `OBSERVED` · source-linked rows |
| `P01-KPI-02` | 156 | Distinct vehicle identities | `SOURCE-SCOPED` · 158 dim rows; 2 UAS no facts |
| `P01-KPI-03` | 178 | Observed journeys | `OBSERVED` · ADS-B segments |
| `P01-KPI-04` | 1,754 | Occupied 2D cell-hours | `PARTIAL` · 86.40 vehicle-minutes; 60 s cap |
| `P01-KPI-05` | 0 | Detected encounters | `NOT PROOF OF ZERO` · insufficient overlapping evidence |
| `P01-KPI-06` | 1 / 4 | Sites with tracking | `COVERAGE GAP` · KBTP only |

**Card formatting:**

- Value: 30 pt, navy.
- Label: 10 pt, slate.
- Status pill: top-right, 8 pt, colored.
- Footer: query ID and data-as-of, 8 pt.
- Card background: white; left border 4 px in status color.
- For `P01-KPI-05`, use amber/red border and a visible `NOT PROOF OF ZERO` label; do not show a green zero.

### 10.3 Visual `P01-V01` — Monthly observed traffic

| Property | Specification |
|---|---|
| Type | Clustered column chart |
| Axis | `Month[MonthLabel]` |
| Values | `[Observed Positions (Site)]` |
| Series | Single series, blue `#2E86C1` |
| Data labels | On, `#,##0`, 10 pt |
| Title | `Observed traffic: one month only` |
| Subtitle | `2022-01 · 27,479 positions · no adjacent prior month` |
| Annotation | Text box: `MoM growth: N/A — no prior month` |
| Tooltip | `Month`, positions, distinct vehicles, coverage status |
| Interactions | Cross-filters `P01-V03` by site if a site is selected; no trend line, no forecast |
| Empty behavior | If no month selected, show a coverage note, not zero |

**Why a column chart:** a line chart with one point would imply a trend. A single column plus an explicit `NO_PRIOR_MONTH` label is honest.

### 10.4 Visual `P01-V02` — Hourly rhythm

| Property | Specification |
|---|---|
| Type | Column chart |
| Axis | `Time[hour_utc]` 0–23 |
| Values | `SUM('HourlyGrid'[tracking_positions])` |
| Data labels | On; hide labels for blank hours |
| Title | `Positions by UTC hour` |
| Subtitle | `20 observed hours; 04–07 UTC unobserved` |
| Conditional formatting | Peak hour amber; other bars blue; blank hours no bar |
| Annotation | `Peak 17:00 UTC · 3,169 positions · 16 vehicles` |
| Tooltip | Hour, positions, distinct vehicles, avg altitude, avg speed, coverage |
| Interactions | Selecting an hour cross-filters the site matrix; no interpolation |

**Missing-hour handling:** the axis must show all 24 hours. For hours 04–07, return `BLANK()` so the bars are absent; add a gray band or text note “no observed rows.” Do not plot zero.

### 10.5 Visual `P01-V03` — Site coverage matrix

| Property | Specification |
|---|---|
| Type | Matrix |
| Rows | `Site[site_code]`, `Site[site_name]` |
| Values | `[Observed Positions (Site)]`, `[Observed Vehicles (Site-Month)]`, `[Observed Occupancy Minutes]`, `[Site Coverage Status]` |
| Sort | Observed positions descending; zero-coverage sites visible |
| Formatting | Header navy/white; alternating rows; data bars on positions; status pill |
| Title | `Site coverage` |
| Subtitle | `4 real sites; 1 observed` |
| Tooltip | Site code/name, status, first/last event |
| Interactions | Drill-through to Page 2A by site |

**Rows expected:** `KBTP` with 27,479; `DJI_CO`, `KAGC`, `NIGHTJAR_PA` with 0 and `NO TRACKING COVERAGE - not proof of no activity`. Do not hide the zero rows.

### 10.6 Visual `P01-V04` — Source coverage matrix

| Property | Specification |
|---|---|
| Type | Matrix |
| Rows | `SourceDim[source_system]`, `Source[source_category]` |
| Values | `[Observed Positions (Source)]`, `[Observed Journeys (Source)]`, `[Source Coverage Status]` |
| Formatting | Data bars; status pill; UAS rows amber/red |
| Title | `Source coverage` |
| Subtitle | `3 source rows; 1 with facts` |
| Tooltip | Source, category, observed months, sites covered, coverage labels |
| Interactions | Drill-through to Page 2B by source |

**Rows expected:** `TARTAN` / `MANNED_ADSB` with 27,479 and 178; `NIGHTJAR` / `UAS` with 0 and `NO TRACKING COVERAGE`; `NOMINAL_DJI` / `UAS` with 0 and `NO TRACKING COVERAGE`. Add note: “UAS is staged but not loaded into facts (`L-008`).”

### 10.7 Visual `P01-V05` — Insight card

**Title:** `What the data says — and what it does not`

**Signals:**

- 27,479 positions from one high-altitude manned ADS-B sample; average 29,924 ft MSL and 414 kts.
- Evening-weighted: 66.7% of positions 15:00–23:59 UTC; peak 17:00 UTC with 16 vehicles.
- 86.40 observed occupancy vehicle-minutes across 1,754 cell-hours; average 1.11 active vehicles per cell-hour, peak 4.
- Moderate concentration: top 10 vehicles 17.8%, top 20 28.7%.

**Do not conclude:**

- This is not low-altitude UAS intelligence.
- 0 encounters is not proof of safety.
- 0 restrictions is not proof of compliance.
- Unknown weather is not “no weather effect.”
- One month is not a trend.
- 2D cells are not corridors or altitude layers.

**Footer:** `Sources: QW-P3-02-02, QW-P3-02-06, vw_vehicle_analysis. See Page 5 for trust evidence.`

---

## 11. Page 02 — Detailed Analysis (Core page 2)

Page 02 is one core page with two bookmark states. The header remains constant; the content container toggles between 2A and 2B.

### 11.1 Shared header and filter bar

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| Header | `P02-HDR` | Shared header | 0 | 0 | 1600 | 84 |
| Nav | `P02-NAV` | Shared nav | 0 | 84 | 1600 | 44 |
| 2A button | `P02-TAB-2A` | Button | 24 | 140 | 150 | 36 |
| 2B button | `P02-TAB-2B` | Button | 184 | 140 | 150 | 36 |
| Site slicer | `P02-FILT-SITE` | Slicer | 24 | 188 | 220 | 64 |
| Month slicer | `P02-FILT-MONTH` | Slicer | 256 | 188 | 180 | 64 |
| Source slicer | `P02-FILT-SOURCE` | Slicer | 448 | 188 | 200 | 64 |
| Vehicle type slicer | `P02-FILT-TYPE` | Slicer | 660 | 188 | 200 | 64 |
| Hour band slicer | `P02-FILT-BAND` | Slicer | 872 | 188 | 180 | 64 |
| Reset button | `P02-FILT-RESET` | Button | 1064 | 188 | 120 | 36 |
| Coverage note | `P02-FILT-NOTE` | Text | 1200 | 188 | 376 | 64 |

**Filter bar rules:**

- Show all real sites and sources.
- When a zero-coverage selection is active, display a red/amber banner: `NO TRACKING COVERAGE for this selection; not proof of no activity.`
- Do not auto-select `KBTP`.
- Keep the filter bar visible in both 2A and 2B.

### 11.2 Page 2A — Traffic, Time & Space

#### Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| KPI 01 | `P02A-KPI-01` | Card | 24 | 268 | 248 | 96 |
| KPI 02 | `P02A-KPI-02` | Card | 284 | 268 | 248 | 96 |
| KPI 03 | `P02A-KPI-03` | Card | 544 | 268 | 248 | 96 |
| KPI 04 | `P02A-KPI-04` | Card | 804 | 268 | 248 | 96 |
| KPI 05 | `P02A-KPI-05` | Card | 1064 | 268 | 248 | 96 |
| KPI 06 | `P02A-KPI-06` | Card | 1324 | 268 | 252 | 96 |
| Hour × date heatmap | `P02A-V01` | Matrix | 24 | 380 | 980 | 330 |
| Top occupied cells | `P02A-V02` | Bar chart | 1020 | 380 | 556 | 330 |
| Site matrix | `P02A-V03` | Matrix | 24 | 726 | 760 | 110 |
| Question card | `P02A-V04` | Text card | 800 | 726 | 776 | 110 |

#### KPI cards

| ID | Value | Label | Status |
|---|---:|---|---|
| `P02A-KPI-01` | 27,479 | Observed positions | `OBSERVED` |
| `P02A-KPI-02` | 156 | Distinct vehicles | `SOURCE-SCOPED` |
| `P02A-KPI-03` | 178 | Journeys | `OBSERVED` |
| `P02A-KPI-04` | 86.40 | Occupancy minutes | `PARTIAL` |
| `P02A-KPI-05` | 17:00 | Peak hour UTC | `OBSERVED` |
| `P02A-KPI-06` | 20 / 24 | Observed hours | `COVERAGE GAP` |

#### Visual `P02A-V01` — UTC hour × date heatmap

| Property | Specification |
|---|---|
| Type | Matrix with conditional formatting |
| Rows | `Date[Date]` (2 observed dates) |
| Columns | `Time[hour_utc]` (0–23) |
| Values | `SUM('HourlyGrid'[tracking_positions])` |
| Conditional formatting | Background color scale: `#F5F7FA` (blank), `#EAF4FB` (low), `#2E86C1` (mid), `#0B4F7A` (high) |
| Blank handling | Blank cells light gray with `—`; do not show 0 |
| Data labels | On, 8 pt, white on dark cells; black on light cells |
| Title | `When traffic was observed` |
| Subtitle | `UTC hour × date; gray = unobserved, not zero` |
| Tooltip | Date, hour, positions, distinct vehicles, avg altitude, avg speed |
| Interactions | Selecting a cell cross-filters `P02A-V02` and `P02A-V03` |
| Annotation | `Peak: 2022-01-01 17:00 UTC · 3,169 positions · 16 vehicles` |

**Why a heatmap:** the data has only two dates and a 4-hour gap. A heatmap shows the observed blocks and the gap without drawing a false continuous line.

#### Visual `P02A-V02` — Top occupied 2D cells

| Property | Specification |
|---|---|
| Type | Horizontal bar chart |
| Axis | `Corridor[grid_cell_id]` |
| Values | `SUM('Corridor'[observed_occupancy_minutes])` |
| Top N | 15 by occupancy minutes |
| Color | Blue; bar with peak active vehicles ≥ 4 highlighted amber |
| Data labels | On, 8 pt |
| Title | `Longest-observed 2D cells` |
| Subtitle | `Observed occupancy; 2D cells, not altitude layers or corridors` |
| Tooltip | Grid cell, observed cell-hours, avg/peak active vehicles, occupancy minutes, encounters (0 with caveat), 2D note |
| Interactions | Selecting a cell opens the grid-cell tooltip or drill-through |
| Caveat | Add a visible `2D / 60 s cap` pill |

**Q2 mapping:** this visual is the partial answer to “longest-occupied sky zones.” It must not call the bars “sky zones” without the 2D caveat.

#### Visual `P02A-V03` — Site matrix

| Property | Specification |
|---|---|
| Type | Matrix |
| Rows | `Site[site_code]` |
| Values | positions, occupancy minutes, coverage status; distinct vehicles only with a documented site-hour query |
| Formatting | Data bars; status pill; zero rows visible |
| Title | `Site coverage in the selected scope` |
| Interactions | Drill-through to a site detail page |

**Measure note:** `HourlyGrid` is aggregated at hour-site-cell grain and has no vehicle key. Use hourly positions and occupancy so the matrix responds to the heatmap; do not sum `distinct_vehicles` across cells. Omit distinct vehicles unless a documented site-hour query is added.

#### Visual `P02A-V04` — Question card

**Title:** `Q1 and Q2 — what this page can and cannot answer`

- **Q1 `PARTIAL`:** “2D grid crowding is observable for 20 hours at KBTP. Altitude-layer crowding is not measurable because the physical grid has no altitude-band column.”
- **Q2 `PARTIAL`:** “Longest-observed 2D cells are ranked by occupancy minutes. The 60-second occupancy cap and 2D grain mean this is not a vertical sky-zone or capacity answer.”
- **Next data:** altitude-band grid, more months, more sites, longer occupancy window.

### 11.3 Page 2B — Fleet, Source & Space

#### Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| KPI 01 | `P02B-KPI-01` | Card | 24 | 268 | 248 | 96 |
| KPI 02 | `P02B-KPI-02` | Card | 284 | 268 | 248 | 96 |
| KPI 03 | `P02B-KPI-03` | Card | 544 | 268 | 248 | 96 |
| KPI 04 | `P02B-KPI-04` | Card | 804 | 268 | 248 | 96 |
| KPI 05 | `P02B-KPI-05` | Card | 1064 | 268 | 248 | 96 |
| KPI 06 | `P02B-KPI-06` | Card | 1324 | 268 | 252 | 96 |
| Pareto | `P02B-V01` | Bar + line | 24 | 380 | 760 | 330 |
| Scatter | `P02B-V02` | Scatter | 800 | 380 | 776 | 330 |
| Source matrix | `P02B-V03` | Matrix | 24 | 726 | 500 | 110 |
| Top vehicles | `P02B-V04` | Table | 540 | 726 | 1036 | 110 |

#### KPI cards

| ID | Value | Label | Status |
|---|---:|---|---|
| `P02B-KPI-01` | 1 / 3 | Sources with facts | `COVERAGE GAP` |
| `P02B-KPI-02` | 156 | Vehicle identities | `SOURCE-SCOPED` |
| `P02B-KPI-03` | 178 | Journeys | `OBSERVED` |
| `P02B-KPI-04` | 29,924 | Avg altitude (ft MSL) | `OBSERVED` |
| `P02B-KPI-05` | 414.3 | Avg speed (kts) | `OBSERVED` |
| `P02B-KPI-06` | 17.8% / 28.7% | Top-10 / top-20 share | `DESCRIPTIVE` |

#### Visual `P02B-V01` — Vehicle concentration Pareto

| Property | Specification |
|---|---|
| Type | Line and clustered column chart |
| Axis | `Vehicle[source_entity_id]` |
| Column values | `[Observed Positions (Vehicle)]` |
| Line values | `[Cumulative Vehicle Share]` |
| Top N | Top 20 vehicles by positions; “Other” not shown |
| Column color | Blue `#2E86C1` |
| Line color | Amber `#F2A900` |
| Data labels | Columns on; line off |
| Title | `Vehicle concentration: top 20 observed identities` |
| Subtitle | `Top 10 = 17.8% · top 20 = 28.7% of positions` |
| Tooltip | Vehicle ID, source, positions, journeys, avg altitude, avg speed, active days, identity note |
| Interactions | Selecting a vehicle filters the scatter and top table |
| Caveat | `Source-scoped identity, not operator` pill |

**Why Pareto:** it answers “how concentrated is observed activity?” without implying fleet ownership or operator identity.

#### Visual `P02B-V02` — Vehicle behavior scatter

| Property | Specification |
|---|---|
| Type | Scatter chart |
| X axis | `Vehicle[avg_ground_speed_kts]` |
| Y axis | `Vehicle[avg_altitude_msl_ft]` |
| Size | `Vehicle[tracking_positions]` |
| Color | `SourceDim[source_category]` |
| Details | `Vehicle[source_entity_id]` |
| Title | `Observed vehicle behavior` |
| Subtitle | `One point per source-scoped identity; size = positions` |
| Tooltip | Vehicle ID, source, positions, journeys, active days, peak hour, coverage |
| Annotation | `Most observations sit in a high-altitude, high-speed manned ADS-B band.` |
| Caveat | `Not operator identity; not a safety classification.` |
| Interactions | Selecting a point filters the Pareto and top table |

**Why scatter:** it shows the observed behavior distribution and outliers without implying aircraft type, operator, or risk.

#### Visual `P02B-V03` — Source matrix

| Property | Specification |
|---|---|
| Type | Matrix |
| Rows | `SourceDim[source_system]`, `Source[source_category]` |
| Values | positions, distinct vehicles, sites covered, journeys, observed months, coverage |
| Formatting | Status pills; zero rows visible |
| Title | `Source performance and coverage` |
| Tooltip | First/last event, avg altitude/speed, observed months, coverage |
| Interactions | Drill-through to a source detail page |

**Rows expected:** `TARTAN` observed; `NIGHTJAR` and `NOMINAL_DJI` zero with `NO TRACKING COVERAGE` and `NO_JOURNEY_COVERAGE`.

#### Visual `P02B-V04` — Top vehicles table

| Column | Field | Format |
|---|---|---|
| Rank | `[Vehicle Rank]` | `#,##0` |
| Vehicle ID | `Vehicle[source_entity_id]` | Text |
| Source | `Vehicle[source_system]` | Text |
| Positions | `Vehicle[tracking_positions]` | `#,##0` |
| Avg altitude | `Vehicle[avg_altitude_msl_ft]` | `#,##0 ft` |
| Avg speed | `Vehicle[avg_ground_speed_kts]` | `#,##0.0 kts` |
| Journeys | `Vehicle[journeys_observed]` | `#,##0` |
| Active days | `Vehicle[active_days_utc]` | `#,##0` |
| Peak hour | `Vehicle[peak_hour_utc]` | `HH:00` |
| Coverage | `Vehicle[tracking_coverage]` | Status pill |

- Top 10 by positions; table scrolls to 20 if needed.
- Do not show `operator_name` because it is not real.
- Add a footer: `Identity is source-scoped; observed behavior is not operator identity (L3-003).`

### 11.4 Page 2B question card

Add a small card or footer:

- **Q3 `PARTIAL`:** one month; growth not computable.
- **Q4 `PARTIAL`:** peak time observable; manned/UAS mix not measurable because UAS has no facts.
- **Q6 `NOT ANSWERABLE`:** no encounter facts; vehicle type is `UNSPECIFIED`.
- **Q10 `SCREENING ONLY`:** low-observed-traffic cells are not corridors.

---

## 12. Page 03 — Decision Brief (Core page 3)

**Purpose:** state the management decision, the evidence, and the next actions. This is not a summary page; it is the decision page.

### 12.1 Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| Header | `P03-HDR` | Shared header | 0 | 0 | 1600 | 84 |
| Nav | `P03-NAV` | Shared nav | 0 | 84 | 1600 | 44 |
| Decision banner | `P03-DEC` | Card | 24 | 144 | 1552 | 96 |
| Decision card 1 | `P03-D1` | Card | 24 | 256 | 504 | 150 |
| Decision card 2 | `P03-D2` | Card | 548 | 256 | 504 | 150 |
| Decision card 3 | `P03-D3` | Card | 1072 | 256 | 504 | 150 |
| Readiness table | `P03-V01` | Table | 24 | 424 | 1000 | 300 |
| Actions table | `P03-V02` | Table | 1040 | 424 | 536 | 300 |
| Guardrails | `P03-GUARD` | Card | 24 | 740 | 760 | 100 |
| Next data | `P03-NEXT` | Card | 800 | 740 | 776 | 100 |
| Footer | `P03-FOOT` | Text | 24 | 860 | 1552 | 24 |

### 12.2 Decision banner

**Text:** `Decision: Do not approve operational capacity, corridors, or safety actions from this sample. Use the dashboard to validate the analytics pipeline and prioritize data acquisition.`

**Subtext:** `The pipeline is reproducible and DQ-clean at the critical level. The sample is one site, one source, one month, and zero UAS/weather/restriction/encounter facts.`

**Formatting:** navy card, white text, amber left border 8 px. No green “approved” styling.

### 12.3 Decision cards

| ID | Title | Body | Evidence |
|---|---|---|---|
| `P03-D1` | `The analytics pipeline is decision-ready` | 10/10 analytical queries, 3/3 gold views reconcile, `DQ3-A-004` PASS, 0 critical DQ failures, reader proof recorded. | `Phase3/evidence/analytics_run_20261118T110136Z.md`; `Phase3/PROGRESS.md` |
| `P03-D2` | `The sample is not operationally representative` | 1 site, 1 source, 1 month, 156 high-altitude manned ADS-B identities, 0 UAS facts, 27,479 unknown-weather positions, 0 restriction facts, 0 encounters. | `L-001`, `L-004`, `L-005`, `L-008`; `QW-P3-02-02` |
| `P03-D3` | `Invest in coverage before optimization` | 3 index candidates were measured `NEUTRAL`; no index was applied. The bottleneck is data coverage, not query speed. | `D3-011`; `Phase3/reports/Indexing_Report.pdf` |

### 12.4 Visual `P03-V01` — Decision readiness table

| Column | Content |
|---|---|
| ID | Q1–Q10 |
| Question | Short label |
| Status | `PARTIAL`, `SCREENING ONLY`, `NOT ANSWERABLE` |
| What we can say now | One sentence |
| What is missing | One sentence |
| Evidence | Query/check ID |

Rows: 10. Use 9 pt body, 9 pt header, 30 px row height. Status pills colored. This table is a compact version of Page 4.

### 12.5 Visual `P03-V02` — Recommended actions

| Priority | Action | Why | Owner | Acceptance evidence |
|---|---|---|---|---|
| P0 | Load a second month and at least one additional site with tracking | Q3 growth and Q1/Q2 multi-site comparison are impossible now | B/A | `vw_monthly_traffic_growth` has ≥2 adjacent months; site count >1 |
| P0 | Load UAS facts from the staged 22,602 accepted rows with approved mapping | Q4 mix and Q6 become measurable only with UAS facts | B/E | UAS source has tracking/journey facts; `L-008` updated |
| P1 | Backfill/link weather keys to tracking | Q8 is blocked by 27,479 unknown weather keys | B/C | Unknown-weather share falls below 100% with a documented linkage |
| P1 | Capture real restriction snapshots for the study window | Q7 has 0 activation facts and no historical snapshot | B | Restriction facts >0 with timestamps; `L-005` updated |
| P1 | Deploy an improved encounter algorithm (±20 s or documented) | Q5/Q6 are not answerable with exact-timestamp pairing | D/E | Encounter facts with `algorithm_version`; `L-004` updated |
| P2 | Evaluate altitude-band grid / 3D model | Q1/Q2 need vertical structure | C | Decision + new grid/fact evidence |
| P2 | Evaluate operator identity source | Q6 needs real operator data, not inferred segments | B | Real operator dimension; `L3-003` updated |
| P2 | Revisit indexes/materialization after data growth | Current indexes are neutral; no speed-up claim | D | New `EXPLAIN ANALYZE` evidence per `D3-010` |

### 12.6 Guardrails card

- No synthetic scenarios, no what-if multipliers, no forecasts.
- Zero is labeled as missing coverage or insufficient evidence.
- No “safe,” “compliant,” “certified,” “capacity,” or “corridor” claims.
- Every number cites a stored query or recorded evidence.
- Reader role only; no credentials in artifacts.

### 12.7 Next-data card

**Minimum evidence package for the next decision:**

1. Two adjacent months at one site, plus a second site with tracking.
2. UAS facts with a documented identity mapping.
3. Weather keys linked to tracking facts.
4. Real restriction snapshots for the study window.
5. A documented encounter algorithm and evidence.

**Acceptance:** each item updates a named view/query and a named limitation; the dashboard must be re-captured with a new data-as-of timestamp.

---

## 13. Page 04 — Coverage & Question Scorecard (Supporting)

**Purpose:** make coverage gaps and the full Q1–Q10 scorecard impossible to miss.

### 13.1 Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| Header | `P04-HDR` | Shared header | 0 | 0 | 1600 | 84 |
| Nav | `P04-NAV` | Shared nav | 0 | 84 | 1600 | 44 |
| Coverage matrix | `P04-V01` | Matrix | 24 | 144 | 760 | 300 |
| Zero cards | `P04-ZEROS` | 6 cards | 800 | 144 | 776 | 300 |
| Question scorecard | `P04-V02` | Table | 24 | 460 | 1552 | 300 |
| Limitations | `P04-V03` | Table | 24 | 776 | 1552 | 64 |
| Footer | `P04-FOOT` | Text | 24 | 860 | 1552 | 24 |

### 13.2 Coverage matrix `P04-V01`

| Row | Columns |
|---|---|
| Site | `site_code`, tracking coverage, journeys, occupancy, source, status |
| Source | `source_system`, category, staged rows, fact rows, status |
| Fact | tracking, journey, occupancy, encounter, restriction, weather-linked |
| Method | 2D/60 s occupancy, exact-timestamp encounters, no historical restrictions, no raw archive |

Use a matrix with a status column and short notes. Do not use a 100% stacked bar for coverage; it hides the absent categories.

### 13.3 Zero cards `P04-ZEROS`

| Card | Value | Label | Explanation |
|---|---:|---|---|
| Encounters | 0 | `NOT PROOF OF ZERO` | No detected episodes; exact-timestamp pairing; single source (`L-004`, `L-008`) |
| Restrictions | 0 | `NO SNAPSHOT COVERAGE` | No historical restriction snapshot (`L-005`) |
| UAS facts | 0 | `STAGED, NOT LOADED` | 22,602 UAS staging rows; 0 facts (`L-008`) |
| Weather-linked | 0 | `NO LINKAGE` | 27,479 unknown weather keys (`L-001`, `DQ-C-003`) |
| Ground state | 27,479 unknown | `INFERRED ONLY` | `on_ground` unknown; WP07-AIR-01 inference (`L-002`, `DQ-C-008`) |
| Vertical grid | 0 altitude bands | `2D ONLY` | Physical grid is 0.01° 2D bins (`L-003`) |

### 13.4 Question scorecard `P04-V02`

Use the full table from Section 4. Columns: ID, Question, Status, What we can say, What is missing, Evidence. 10 rows; 9 pt. Add filters by status. This is the authoritative on-dashboard scorecard.

### 13.5 Limitations `P04-V03`

A compact strip:

`L-001 weather · L-002 ground state · L-003 2D occupancy · L-004 encounters · L-005 restrictions · L-006 reject ledger · L-007 corridors · L-008 UAS · L-009 zones · L-010 raw archive · L3-001 manual refresh · L3-002 growth instability · L3-003 identity`

Link to the canonical limitations document in the footer text; do not reproduce all 13 rows in a tiny font. Use a tooltip or drill-through for the full register.

---

## 14. Page 05 — ETL & Data Trust (Supporting)

**Purpose:** prove the pipeline is robust enough for descriptive analytics and expose every warning. This page is part of “represent the whole project.”

### 14.1 Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| Header | `P05-HDR` | Shared header | 0 | 0 | 1600 | 84 |
| Nav | `P05-NAV` | Shared nav | 0 | 84 | 1600 | 44 |
| KPI 01 | `P05-KPI-01` | Card | 24 | 144 | 248 | 96 |
| KPI 02 | `P05-KPI-02` | Card | 284 | 144 | 248 | 96 |
| KPI 03 | `P05-KPI-03` | Card | 544 | 144 | 248 | 96 |
| KPI 04 | `P05-KPI-04` | Card | 804 | 144 | 248 | 96 |
| KPI 05 | `P05-KPI-05` | Card | 1064 | 144 | 248 | 96 |
| KPI 06 | `P05-KPI-06` | Card | 1324 | 144 | 252 | 96 |
| ETL ribbon | `P05-V01` | Shapes/text | 24 | 256 | 1552 | 96 |
| DQ summary | `P05-V02` | Matrix | 24 | 368 | 760 | 240 |
| Reject Pareto | `P05-V03` | Bar chart | 800 | 368 | 776 | 240 |
| Gold/index evidence | `P05-V04` | Card | 24 | 624 | 760 | 200 |
| Coverage staged vs facts | `P05-V05` | Matrix | 800 | 624 | 776 | 200 |
| Footer | `P05-FOOT` | Text | 24 | 860 | 1552 | 24 |

### 14.2 KPI cards

| ID | Value | Label | Status |
|---|---:|---|---|
| `P05-KPI-01` | `SUCCESS` | Latest ETL run | `PASS` · run 43502710978 · 35 s |
| `P05-KPI-02` | 23,414 | Rows read | `RECONCILED` |
| `P05-KPI-03` | 23,254 | Rows accepted | `RECONCILED` |
| `P05-KPI-04` | 160 | Rows rejected | `0.68%` · 1 timestamp, 159 zero coordinate |
| `P05-KPI-05` | 32 / 4 / 0 | DQ PASS / WARN / FAIL | `NO CRITICAL FAIL` |
| `P05-KPI-06` | `PASS` | Reader proof | `RECORDED` · H3-005; H-017 per-member proof open |

**Formatting:** no green “perfect data” badge. `P05-KPI-05` is green for 0 FAIL but amber for 4 WARN; label both.

### 14.3 Visual `P05-V01` — ETL flow ribbon

Use shapes/text, not a data visual. Six stages:

```text
Fetch -> Manifest -> Staging -> Dimensions/Facts -> DQ gate -> Gold views -> BI
```

Each stage has a status pill and a count:

| Stage | Evidence |
|---|---|
| Fetch | 8 source manifests |
| Manifest | URL, licence, SHA-256, fetched_at |
| Staging | 23,414 read / 23,254 accepted / 160 rejected / 0 duplicate |
| Dimensions/Facts | 820 dimension rows; facts unchanged |
| DQ gate | 36 checks; 32 PASS / 4 WARN / 0 FAIL |
| Gold views | 3 views; `DQ3-A-001` PASS |
| BI | Reader role; manual refresh |

Add a small `Fail closed` lock icon/text and `One transaction` label. Do not draw a Sankey with invented flow volumes.

### 14.4 Visual `P05-V02` — DQ summary

| Property | Specification |
|---|---|
| Type | Matrix |
| Rows | `DQ[severity]`, `DQ[status]` |
| Values | count of checks |
| Title | `DQ results: 36 checks, 0 critical failures` |
| Conditional formatting | PASS green, WARN amber, FAIL red |
| Detail | Separate table of the 4 WARN rows: `check_id`, `status`, `observed_value`, `meaning`, `limitation` |
| Tooltip | Check description, expected, observed, scope |
| Drill-through | Hidden `P05A_DQ_Detail` page with all 36 rows |

**WARN rows to show:**

| Check | Observed | Meaning |
|---|---:|---|
| `DQ-C-003` | 27,479 | Tracking weather keys unknown; `dim_weather[-1]` is not an observation |
| `DQ-C-008` | 27,479 | Ground state unknown; WP07-AIR-01 is inferred |
| `DQ-A-008` | not recorded in available docs | Wind-direction warning; do not invent an observed count; show `WARN` and cite the run |
| `DQ-T-003` | 1 | No accepted restriction snapshot; not one missing flight |

> `DQ-A-008` exact observed value is not recorded in the available evidence. Display “WARN — observed value not captured in the dashboard source” and link to the DQ detail page; do not fabricate a number.

### 14.5 Visual `P05-V03` — Reject Pareto

| Property | Specification |
|---|---|
| Type | Bar chart |
| Axis | `RejectSummary[reason_code]` |
| Values | `SUM('RejectSummary'[reject_count])` |
| Filter | `etl_run_id = 11` |
| Title | `Run 11 rejects: 160 of 23,414 rows (0.68%)` |
| Subtitle | `1 invalid timestamp · 159 zero coordinate` |
| Annotation | `Cumulative ledger: 578 events across runs (L-006). Do not add cumulative rejects to run 11.` |
| Tooltip | Source, reason, count, run ID, first/last reject timestamp if available |
| Interactions | Selecting a reason shows source breakdown |

**Separate cards:**

- `Run 11 rejects`: 160.
- `Cumulative ledger`: 578 (418 prior + 160); scope = all runs, not run 11.

### 14.6 Visual `P05-V04` — Gold/index evidence

Two stacked cards:

**Gold views:**

- 3/3 views reconcile (`DQ3-A-001` PASS).
- `vw_monthly_traffic_growth`: 1 row / 27,479 tracking.
- `vw_vehicle_analysis`: 158 rows / 27,479 tracking / 178 journeys.
- `vw_source_performance`: 3 rows / 27,479 tracking / 178 journeys.
- Apply recorded via H3-005; verify evidence captured 2026-11-18T11:34:54Z.
- No separate gold-view apply run ID is recorded in the repo; cite H3-005 and the admin record. Do not invent a run ID.

**Index measurement:**

- 3 candidates measured `NEUTRAL`; 0 applied; 992 KiB avoided.
- `OQ-P3-05-01`: 28.927 → 29.064 ms, cost 5,683.16 both, 488 KiB.
- `OQ-P3-05-02`: 32.055 → 32.240 ms, cost 11,359.07 both, 488 KiB.
- `OQ-P3-05-03`: 33.101 → 33.220 ms, cost 9,347.77 both, 16 KiB.
- `DQ3-A-006` PASS; `D3-011` no apply.
- Label: “one EXPLAIN ANALYZE pair, not a benchmark; no speed-up claimed.”

### 14.7 Visual `P05-V05` — Staged vs facts coverage

| Row | Staged accepted | Fact coverage | Status |
|---|---:|---|---|
| Tartan ADS-B | 27,479 | 27,479 tracking | OBSERVED |
| UAS (Nightjar + nominal DJI) | 22,602 | 0 tracking, 0 journeys | STAGED, NOT LOADED |
| METAR weather | 400 | 0 linked tracking keys | STAGED, NOT LINKED |
| FAA airspace | 252 | 0 restriction activations | STAGED, NOT EVALUATED |
| OpenSky | 0 | 0 | NOT LOADED (`D-013`) |

**Rule:** staged rows are not facts. Do not sum staged UAS into traffic. Do not call 0 UAS facts “no UAS activity.”

### 14.8 Robustness controls checklist

| Control | Status | Evidence |
|---|---|---|
| Single transaction for apply | PASS | `etl/run.py`; rollback on critical DQ |
| Reconciliation `read = accepted + rejected + duplicate` | PASS | `etl_run_log` |
| Fail closed on critical DQ | PASS | 0 FAIL; failure-path tests |
| Idempotent reruns | PASS (design/tests) | `ON CONFLICT`; second apply proof `H-018` remains open |
| Retry/backoff for transient fetch | PASS | PR #27; run 43502710978 |
| Reader-only access | PASS (recorded) | WP-11 reader proof; per-member `H-017` open |
| Capacity guard | PASS | 71.78 MiB vs 700 MB |
| No secrets in artifacts | REQUIRED | Screenshot review; no connection strings |
| Weekly/manual cadence | PASS | Schedule gated; no polling |
| Raw archive | OPEN | `L-010`; manifest only |

### 14.9 Data freshness card

- **Event time:** 2022-01-01 08:09:40Z to 2022-01-02 03:59:47Z.
- **Warehouse data-as-of:** 2026-11-13 12:37:21Z.
- **Analytics capture:** 2026-11-18T11:01:37Z.
- **Dashboard refresh:** manual; record the actual refresh timestamp at build.
- **Not real-time:** no streaming, no alerts, no SLA (`L3-001`).

---

## 15. Page 06 — Method & Evidence (Supporting)

**Purpose:** let a reviewer reproduce and audit the dashboard without asking the author.

### 15.1 Layout

| Object | ID | Type | x | y | w | h |
|---|---|---|---:|---:|---:|---:|
| Header | `P06-HDR` | Shared header | 0 | 0 | 1600 | 84 |
| Nav | `P06-NAV` | Shared nav | 0 | 84 | 1600 | 44 |
| Architecture | `P06-V01` | Diagram | 24 | 144 | 760 | 300 |
| KPI dictionary | `P06-V02` | Table | 800 | 144 | 776 | 300 |
| Traceability | `P06-V03` | Table | 24 | 460 | 1552 | 300 |
| Attribution/refresh | `P06-V04` | Card | 24 | 776 | 1552 | 64 |
| Footer | `P06-FOOT` | Text | 24 | 860 | 1552 | 24 |

### 15.2 Architecture `P06-V01`

Use a clean block diagram:

```text
Public sources
  -> project_staging (manifest, rejects, DQ, run log)
  -> project_dw (6 dimensions, 5 facts)
  -> project_reporting (10 Phase 2 views + 3 Phase 3 gold views)
  -> analytical SQL + ROLLUP/CUBE
  -> Power BI semantic model (Import, reader role)
  -> 3 core pages + supporting evidence pages
```

Add labels: `real data only`, `fail closed`, `idempotent`, `reconciled`, `manual/weekly`, `no Docker`, `Neon Free`.

### 15.3 KPI dictionary `P06-V02`

Use the KPI table from Section 7.1. Columns: KPI, formula, source, zero semantics, DQ link. 9 pt; scroll if needed. This is the dashboard’s self-documentation.

### 15.4 Traceability `P06-V03`

The table covers every data-bearing visual and evidence card. Headers, navigation controls, filters, footers, and text-only labels/cards are specified in the page sections and are not separate data visuals.

| Visual ID | Page | Source query/view | DQ check | Evidence |
|---|---|---|---|---|
| `P00-SCOPE` | 0 | `QW-P3-02-02`, `QW-P3-02-07` | `DQ3-A-002` | analytics evidence |
| `P00-EVID` | 0 | recorded evidence / Phase 3 docs | `DQ3-A-002` | docs |
| `P01-KPI-01` | 1 | `QW-P3-02-02` | `DQ3-A-002` | analytics evidence |
| `P01-KPI-02` | 1 | `QW-P3-02-02` / `vw_vehicle_analysis` | `DQ3-A-001` | analytics + gold evidence |
| `P01-KPI-03` | 1 | `QW-P3-02-02` | `DQ3-A-002` | analytics evidence |
| `P01-KPI-04` | 1 | `QW-P3-02-02` / `vw_occupied_grid_hours` | `L-003`, `DQ3-A-003` | analytics evidence |
| `P01-KPI-05` | 1 | `fact_close_encounter` | `L-004`, `L-008` | analytics evidence |
| `P01-KPI-06` | 1 | `QW-P3-02-03` / `vw_monthly_traffic_growth` | `DQ3-A-003` | analytics evidence |
| `P01-V01` | 1 | `vw_monthly_traffic_growth` / `QW-P3-02-01` | `DQ3-A-001` | gold evidence |
| `P01-V02` | 1 | `vw_traffic_density_hour_grid` / `QW-P3-02-06` | `DQ3-A-003` | analytics evidence |
| `P01-V03` | 1 | `vw_monthly_traffic_growth` / `vw_occupied_grid_hours` / `QW-P3-02-03` | `DQ3-A-003` | analytics + gold evidence |
| `P01-V04` | 1 | `vw_source_performance` / `QW-P3-02-05` | `DQ3-A-001` | gold evidence |
| `P01-V05` | 1 | `QW-P3-02-02`, `QW-P3-02-06`, `vw_vehicle_analysis` | `DQ3-A-002` | analytics + gold evidence |
| `P02A-KPI-01` | 2A | `QW-P3-02-02` | `DQ3-A-002` | analytics evidence |
| `P02A-KPI-02` | 2A | `QW-P3-02-02` / `vw_vehicle_analysis` | `DQ3-A-001` | analytics + gold evidence |
| `P02A-KPI-03` | 2A | `QW-P3-02-02` | `DQ3-A-002` | analytics evidence |
| `P02A-KPI-04` | 2A | `vw_occupied_grid_hours` / `QW-P3-02-02` | `L-003` | analytics evidence |
| `P02A-KPI-05` | 2A | `vw_peak_site_hours` / `QW-P3-02-06` | `DQ3-A-003` | analytics evidence |
| `P02A-KPI-06` | 2A | `vw_traffic_density_hour_grid` / `QW-P3-02-06` | `DQ3-A-003` | analytics evidence |
| `P02A-V01` | 2A | `vw_traffic_density_hour_grid` | `DQ3-A-003` | analytics evidence |
| `P02A-V02` | 2A | `vw_corridor_capacity_inputs` | `L-003`, `L-007` | analytics evidence |
| `P02A-V03` | 2A | `vw_traffic_density_hour_grid` / `vw_occupied_grid_hours` / `QW-P3-02-03` | `DQ3-A-003` | analytics evidence |
| `P02B-KPI-01` | 2B | `vw_source_performance` | `DQ3-A-001` | gold evidence |
| `P02B-KPI-02` | 2B | `vw_vehicle_analysis` | `DQ3-A-001` | gold evidence |
| `P02B-KPI-03` | 2B | `QW-P3-02-02` / `vw_vehicle_analysis` | `DQ3-A-002` | analytics + gold evidence |
| `P02B-KPI-04` | 2B | `vw_vehicle_analysis` / `QW-P3-02-02` | `DQ3-A-002` | analytics + gold evidence |
| `P02B-KPI-05` | 2B | `vw_vehicle_analysis` / `QW-P3-02-02` | `DQ3-A-002` | analytics + gold evidence |
| `P02B-KPI-06` | 2B | `vw_vehicle_analysis` | `L3-003` | gold evidence |
| `P02B-V01` | 2B | `vw_vehicle_analysis` | `DQ3-A-001` | gold evidence |
| `P02B-V02` | 2B | `vw_vehicle_analysis` | `L3-003` | gold evidence |
| `P02B-V03` | 2B | `vw_source_performance` | `DQ3-A-001` | gold evidence |
| `P02B-V04` | 2B | `vw_vehicle_analysis` | `L3-003` | gold evidence |
| `P03-D1` | 3 | `Phase3/evidence/analytics_run_20261118T110136Z.md`; `Phase3/PROGRESS.md` | `DQ3-A-004` | analytics evidence |
| `P03-D2` | 3 | `QW-P3-02-02`; limitations docs | `L-001`, `L-004`, `L-005`, `L-008` | analytics evidence |
| `P03-D3` | 3 | `Phase3/reports/Indexing_Report.pdf` | `DQ3-A-006`, `D3-011` | indexing evidence |
| `P03-V01` | 3 | Question scorecard | `DQ3-A-002` | Phase 1 + Phase 3 docs |
| `P03-V02` | 3 | Phase 3 recommended actions | `DQ3-A-002` | Phase 3 docs |
| `P04-V01` | 4 | `QW-P3-02-07` + coverage views | `DQ3-A-003` | analytics evidence |
| `P04-ZEROS` | 4 | `fact_close_encounter`, `fact_restriction_activation`, staging, `vw_weather_operations` | `L-001`, `L-004`, `L-005`, `L-008` | analytics + docs |
| `P04-V02` | 4 | Question scorecard | `DQ3-A-002` | Phase 1 + Phase 3 docs |
| `P05-KPI-01` | 5 | `Run` / `QW-P3-02-02` | `DQ3-A-002` | WP-11 run |
| `P05-KPI-02` | 5 | `Run` | `DQ3-A-002` | WP-11 run |
| `P05-KPI-03` | 5 | `Run` | `DQ3-A-002` | WP-11 run |
| `P05-KPI-04` | 5 | `Run` / `RejectSummary` | `DQ3-A-002` | WP-11 run |
| `P05-KPI-05` | 5 | `DQ` | `DQ3-A-002` | WP-11 run |
| `P05-KPI-06` | 5 | `Evidence` / WP-11 reader proof | `H-017` caveat | WP-11 run |
| `P05-V01` | 5 | `Run`, `Manifest`, `DQ` | `DQ3-A-002` | WP-11 run |
| `P05-V02` | 5 | `project_staging.dq_result` | `DQ3-A-002` | WP-11 run |
| `P05-V03` | 5 | `project_staging.stg_reject` | `L-006` | WP-11 run |
| `P05-V04` | 5 | gold/index evidence | `DQ3-A-001`, `DQ3-A-006` | gold + indexing evidence |
| `P05-V05` | 5 | `Manifest`, `Run`, staging counts | `DQ3-A-002` | WP-11 run |
| `P06-V01` | 6 | Phase 3 architecture docs | `DQ3-A-002` | docs |
| `P06-V02` | 6 | KPI dictionary (Section 7.1) | `DQ3-A-002` | this spec |
| `P06-V03` | 6 | this traceability table | `DQ3-A-002` | this spec |
| `P06-V04` | 6 | attribution/refresh docs | `DQ3-A-002` | docs |

This table must be complete before review; add any data visual added after this spec.

### 15.5 Attribution and refresh `P06-V04`

**Attribution:**

- TartanAviation ADS-B — CC BY 4.0.
- Nightjar / nominal-io DJI — CC BY 4.0 / MIT notices preserved.
- NOAA AWC + IEM METAR — NOAA/NWS and IEM attribution.
- FAA airspace / UDDS — FAA/AIS attribution; fetch date in evidence.
- OpenSky — not loaded; must not appear as measured.

**Refresh recipe:**

1. Open the PBIX on the approved machine.
2. Confirm the PostgreSQL connection uses `aerogrid_reader`; do not save credentials in the file.
3. Refresh all queries.
4. Check `Data As Of`, KPI cards, and Page 5 counts against the latest evidence file.
5. Capture screenshots and a new screenshots PDF with the capture date and data-as-of.
6. Record the refresh timestamp, Desktop version, PBIX size, and evidence citations in the insights report.
7. If refresh fails, do not publish; record the failure and keep the previous artifacts.

---

## 16. Tooltip pages

Custom tooltip pages are hidden from navigation. Use 320 × 240 px, white card, 8 px radius, 9 pt text.

| Tooltip | Fields | Required caveat |
|---|---|---|
| `TT_Site` | Site code/name, positions, distinct vehicles, journeys, occupancy, coverage | “Zero = missing coverage, not zero activity” |
| `TT_Vehicle` | Vehicle ID, source, positions, avg altitude/speed, journeys, active days, peak hour, coverage | “Source-scoped identity, not operator” |
| `TT_Grid` | Grid cell, lat/lon, observed cell-hours, avg/peak active, occupancy minutes, encounters | “2D cell, not altitude layer or corridor” |
| `TT_DQ` | Check ID, severity, status, observed, expected, scope, limitation | “0 FAIL does not mean perfect data” |
| `TT_Question` | Question, status, what we can say, what is missing, evidence | “No synthetic answer” |
| `TT_Index` | Query ID, before/after ms, cost, index size, verdict | “One measured pair, not a benchmark” |

Tooltips must not show connection strings, hostnames, usernames, or raw rows.

---

## 17. Interactions and accessibility

### 17.1 Cross-filtering

- Page 1 site matrix -> monthly/hourly charts filtered by site.
- Page 1 hourly chart -> site matrix filtered by hour.
- Page 2A heatmap -> top cells and site matrix.
- Page 2B Pareto -> scatter and top table.
- Page 2B source matrix -> vehicle visuals.
- Page 5 DQ summary -> DQ detail drill-through.
- Page 4 question table -> Page 3 decision context.

Use `Edit interactions` to disable interactions that would create a misleading zero. For example, selecting a UAS source with no facts should show a coverage message, not blank charts.

### 17.2 Drill-through

| Drill-through page | From | Fields | Content |
|---|---|---|---|
| `P02A_Site_Detail` | Site matrix | `site_key` | Site KPIs, hourly pattern, top cells, coverage |
| `P02B_Source_Detail` | Source matrix | `source_system` | Source KPIs, vehicles, journeys, coverage |
| `P02B_Vehicle_Detail` | Vehicle table/scatter | `vehicle_key` | Vehicle KPIs, observed hours, journeys, caveat |
| `P02A_Grid_Detail` | Grid bar/table | `grid_key` | Cell occupancy, 2D caveat, encounters |
| `P05A_DQ_Detail` | DQ matrix | `check_id` | All 36 DQ rows with observed/expected |

Drill-through pages are supporting, not core. Keep the header and a `Back` button.

### 17.3 Accessibility

- Alt text for every visual. Example for `P01-V02`: “Column chart of observed tracking positions by UTC hour; 20 of 24 hours observed; peak at 17:00 UTC with 3,169 positions; hours 04:00–07:59 have no observed rows and are not zero.”
- Alt text for `P01-KPI-05`: “Zero detected encounters; this is not proof of zero encounters because the encounter method requires exact timestamps and only one source is loaded.”
- Tab order: header -> filter bar -> KPI row -> main visual -> secondary visual -> table -> footer.
- Contrast: white on navy, navy on white, white on blue; do not use amber text on white for small text.
- Do not rely on color alone; status pills include text.
- Minimum font size: 8 pt for footnotes, 9 pt for tables, 10 pt for body, 20 pt for page titles.
- Use `Show items with no data` only where the visual has a coverage label; otherwise missing bars should be blank, not zero.
- Avoid animations, auto-play, and flashing.
- Provide a text summary on Page 3 for screen readers.

---

## 18. Refresh, screenshots, and evidence

### 18.1 Build sequence

1. Create the PBIX from a clean Power BI Desktop file.
2. Connect with `aerogrid_reader`; import the tables in Section 6.2.
3. Build the semantic model and relationships.
4. Add measures and format strings.
5. Import the theme JSON.
6. Build pages in order: 00, 01, 02A, 02B, 03, 04, 05, 06.
7. Add bookmarks, navigation, drill-through, and tooltips.
8. Add alt text and tab order.
9. Test every filter state, especially zero-coverage selections.
10. Refresh and capture a new evidence snapshot.
11. Export screenshots PDF, one page per dashboard page.
12. Record the Desktop version, PBIX size, data-as-of, refresh time, and evidence paths.

### 18.2 Screenshots PDF

| Requirement | Detail |
|---|---|
| Pages | One PDF page per dashboard page, in order 00–06 |
| Capture date | Visible on every page |
| Data as-of | Visible on every page |
| Filters | Capture the default state; optionally add a zero-coverage state on Page 2A |
| Redaction | No connection strings, hostnames, usernames, or credentials |
| Size | <10 MB (`D3-008`); otherwise GitHub Actions artifact |
| Evidence | Each screenshot cites its page ID and source query in the insights report |

### 18.3 Evidence record

Add a short record to the insights report and `Phase3/PROGRESS.md`:

```text
PBIX build:
  Desktop version:
  Build date:
  Data as-of:
  Refresh time:
  PBIX size:
  Screenshots PDF size:
  KPI values checked against:
  DQ checks:
  Reviewer A:
  Reviewer D:
```

Do not mark WP-P3-06 `DONE` until reviewers A/D approve and the evidence is recorded.

---

## 19. Acceptance checklist

### 19.1 WP-P3-06 acceptance

- [ ] Three core pages exist: Executive, Detailed, Decision.
- [ ] Supporting pages are labeled `SUPPORTING`.
- [ ] Every visual traces to a stored query/view (`DQ3-A-002`).
- [ ] Every zero KPI carries a coverage label (`DQ3-A-003`).
- [ ] Dashboard numbers match the cited views/queries at capture (`DQ3-A-005`).
- [ ] No credentials, connection strings, or raw data in the PBIX/screenshots.
- [ ] Reader-role connection only.
- [ ] `.pbix` and screenshots PDF each <10 MB.
- [ ] Screenshots PDF has one page per dashboard page, with capture date and data-as-of.
- [ ] ETL health and robustness are visible on Page 5.
- [ ] Q1–Q10 scorecard is visible on Page 4 and summarized on Page 3.
- [ ] No synthetic data, forecast, what-if, or unapproved KPI.
- [ ] Reviewers A/D approve.

### 19.2 Functional test cases

| ID | Test | Expected |
|---|---|---|
| `T-01` | Open PBIX and refresh | Refresh succeeds with reader role; no writer credentials |
| `T-02` | Check `Data As Of` | Matches the captured evidence timestamp |
| `T-03` | Check executive KPIs | 27,479 / 156 / 178 / 1,754 / 0 / 1 of 4 |
| `T-04` | Select `KAGC` | `NO TRACKING COVERAGE` message; no zero-activity claim |
| `T-05` | Select `NIGHTJAR` | `NO TRACKING COVERAGE`; UAS staged-not-loaded note |
| `T-06` | Select the observed month | MoM shows `N/A — no prior month` |
| `T-07` | Open encounter card | 0 with `NOT PROOF OF ZERO` and L-004/L-008 |
| `T-08` | Open DQ page | 32 PASS / 4 WARN / 0 FAIL; WARN names visible |
| `T-09` | Open reject page | 160 run-11 rejects; 578 cumulative with L-006 caveat |
| `T-10` | Open index card | 3 `NEUTRAL`, 0 applied, 992 KiB avoided, DQ3-A-006 PASS |
| `T-11` | Search PBIX/screenshots for secrets | None |
| `T-12` | Check screenshots PDF | One page per page; data-as-of visible |
| `T-13` | Check alt text/tab order | Present and logical |
| `T-14` | Check file sizes | <10 MB each |
| `T-15` | Reviewer A/D review | Signed off in PROGRESS |

---

## 20. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Zero reads as “no activity” | High | `D3-009`; coverage pills; `DQ3-A-003`; test T-04/T-05 |
| Single-month growth misread | Medium | `NO_PRIOR_MONTH`; no trend line; label in Page 1/3 |
| Encounters zero misread as safe | High | `NOT PROOF OF ZERO`; L-004/L-008; no green zero |
| 2D occupancy called capacity | High | `PARTIAL`/`2D` pill; no capacity wording; L-003 |
| Candidate cells called corridors | High | `SCREENING ONLY`; L-007; no map routes |
| Credentials in PBIX/screenshots | High | Reader role; screenshot redaction; no saved connection string; reviewer check |
| Static evidence drifts | Medium | Capture date and source; refresh with new run; do not use static for live KPIs |
| PBIX too large | Medium | Aggregate-only; size guard; artifact fallback |
| Desktop version incompatibility | Medium | Record version; screenshots PDF; keep PBIX (`R3-08`) |
| Data Trust page overclaims reader proof | High | Say “recorded via H3-005; H-017 open”; do not claim all five members |
| Second apply/idempotency unproven | Medium | Say “design/tests; H-018 open”; do not claim rerun proof |
| `DQ-A-008` observed count unknown | Medium | Show WARN and “value not captured”; do not invent |

---

## 21. Decisions and open items

### 21.1 Approved decisions

| ID | Decision | Why | Status |
|---|---|---|---|
| `D3-012` | Data Trust page may read aggregated `project_staging` audit tables (`etl_run_log`, `dq_result`, `stg_reject`, `source_manifest`) with `aerogrid_reader`, plus a labeled static evidence table for reader proof, DB size, and index verdict. No raw payloads. | Enables a live ETL health page without new warehouse objects | Approved 2026-11-20 by requester-admin |
| `D3-013` | Pages 04–06 are supporting evidence pages; core remains 3 pages (01–03). Page 02 uses 2A/2B bookmarks. | Preserves the three-page brief while representing the whole project | Approved 2026-11-20 by requester-admin |
| `D3-014` | The dashboard uses Import mode and aggregate/reporting views only; no raw facts in PBIX. | Protects size, privacy, and reproducibility | Approved 2026-11-20 by requester-admin |

`D3-012`–`D3-014` are approved for build. `D3-012` permits aggregated audit tables only; no raw payloads. The static evidence fallback remains available if reader access fails.

### 21.2 Open items

| Item | Owner | Next step |
|---|---|---|
| Confirm Power BI Desktop version for screenshots | E | Record in insights report |
| Confirm reader credential path for refresh | E | Use private setup; never paste into chat |
| Confirm `DQ-A-008` observed value | A/B | Query `dq_result` for run 11; do not invent |
| Confirm whether per-member reader proof (`H-017`) is complete | A | Update Data Trust page wording only with evidence |
| Confirm whether second apply (`H-018`) is complete | A | Update idempotency wording only with evidence |
| Reviewer A/D sign-off on final PBIX and screenshots | A/D | After artifacts are captured; the spec is approved for build |

---

## 22. Traceability and source map

### 22.1 Query IDs

| Query ID | File | Purpose |
|---|---|---|
| `QW-P3-02-01` | `Phase3/sql/analytical/01_monthly_traffic_growth.sql` | Monthly volume + MoM |
| `QW-P3-02-02` | `Phase3/sql/analytical/02_kpi_snapshot.sql` | Executive KPI snapshot |
| `QW-P3-02-03` | `Phase3/sql/analytical/03_site_traffic_summary.sql` | Site summary |
| `QW-P3-02-04` | `Phase3/sql/analytical/04_vehicle_activity_summary.sql` | Vehicle summary |
| `QW-P3-02-05` | `Phase3/sql/analytical/05_source_performance.sql` | Source summary |
| `QW-P3-02-06` | `Phase3/sql/analytical/06_time_of_day_pattern.sql` | Hour-of-day pattern |
| `QW-P3-02-07` | `Phase3/sql/analytical/07_coverage_diagnostics.sql` | Coverage diagnostics |
| `QW-P3-03-01` | `Phase3/sql/olap/01_rollup_site_source_category_vehicle_type.sql` | ROLLUP |
| `QW-P3-03-02` | `Phase3/sql/olap/02_cube_site_source_system.sql` | CUBE |
| `QW-P3-03-03` | `Phase3/sql/olap/03_grand_total_reconciliation.sql` | Grand-total reconciliation |

### 22.2 Views

| View | Use |
|---|---|
| `vw_monthly_traffic_growth` | Monthly volume/growth |
| `vw_vehicle_analysis` | Vehicle concentration/behavior |
| `vw_source_performance` | Source coverage/performance |
| `vw_traffic_density_hour_grid` | Hourly site/cell traffic |
| `vw_occupied_grid_hours` | Occupancy detail |
| `vw_peak_site_hours` | Peak hour |
| `vw_corridor_capacity_inputs` | Top 2D cells |
| `vw_candidate_corridor_cells` | Q10 screening |
| `vw_weather_operations` | Weather coverage |
| `vw_daily_encounter_hotspots` | Q5 zero evidence |
| `vw_encounter_vehicle_types` | Q6 zero evidence |
| `vw_restriction_traffic_impact` | Q7 zero evidence |

### 22.3 Evidence files

| Evidence | Path |
|---|---|
| Analytics run | `Phase3/evidence/analytics_run_20261118T110136Z.md` |
| Gold-view verify | `Phase3/evidence/gold_views_20261118T113454Z.md` |
| Indexing report | `Phase3/reports/Indexing_Report.pdf` |
| Phase 3 status | `Phase3/PROGRESS.md` |
| Phase 3 decisions | `Phase3/DECISIONS.md` |
| Phase 2 status | `Phase2/PROGRESS.md` |
| Limitations | `Phase2/docs/13_accepted_data_limitations.md`; `Phase3/docs/13_accepted_data_limitations.md` |
| Data dictionary | `data/data_dictionary.md` |
| Phase 1 questions | `Phase1/Business_Questions.tex` |
| Reporting views | `Phase2/sql/05_reporting/01_reporting_views.sql` |
| Gold views | `Phase3/sql/views/01_gold_views.sql` |

### 22.4 Attribution

- TartanAviation ADS-B — CC BY 4.0.
- Nightjar / nominal-io DJI — CC BY 4.0 / MIT.
- NOAA AWC + IEM METAR — NOAA/NWS and IEM.
- FAA airspace / UDDS — FAA/AIS.
- OpenSky — not loaded; do not show as measured.

---

## Appendix A — KPI values at evidence capture

| KPI | Value | Display format |
|---|---:|---|
| Tracking positions | 27,479 | `27,479` |
| Distinct vehicles | 156 | `156` |
| Journeys | 178 | `178` |
| Occupancy facts | 1,754 | `1,754` |
| Occupancy minutes | 86.40 | `86.40 min` |
| Average active vehicles / cell-hour | 1.11 | `1.11` |
| Peak active vehicles | 4 | `4` |
| Average altitude | 29,924.13 | `29,924 ft MSL` |
| Average speed | 414.29 | `414.3 kts` |
| Average journey duration | 145.22 | `145.22 s` |
| Observed journey distance | 20,497.439 | `20,497.439 nm` |
| Detected encounters | 0 | `0 · NOT PROOF OF ZERO` |
| Restriction facts | 0 | `0 · NO SNAPSHOT COVERAGE` |
| Unknown weather positions | 27,479 | `100% unknown` |
| Missing altitude/speed positions | 752 | `752` |
| Sites with tracking | 1 of 4 | `1 / 4` |
| Sources with facts | 1 of 3 | `1 / 3` |
| Observed months | 1 | `1` |
| Active days | 2 | `2` |
| Observed hours | 20 of 24 | `20 / 24` |
| Top-10 vehicle share | 17.8% | `17.8%` |
| Top-20 vehicle share | 28.7% | `28.7%` |
| Peak hour | 17:00 UTC | `17:00` |
| Peak positions | 3,169 | `3,169` |
| Peak vehicles | 16 | `16` |

## Appendix B — Question scorecard detail

Use Section 4 as the canonical table. The dashboard table on Page 4 must include all 10 rows, not a subset. Page 3 may use a compact 10-row version or a 6-row summary plus “see Page 4.”

## Appendix C — ETL / DQ evidence detail

| Item | Value | Note |
|---|---|---|
| Run ID | `43502710978` | `SUCCESS` on `main@165d59d` |
| ETL run ID | `11` | `etl_run_id` |
| Duration | 35 s | recorded |
| Read | 23,414 | validate/apply summary |
| Accepted | 23,254 | reconcile |
| Rejected | 160 | 1 `INVALID_TIMESTAMP`, 159 `ZERO_COORDINATE` |
| Duplicate | 0 | reconcile |
| Manifests | 8 | source provenance |
| Dimensions | 820 rows | `dim_weather` 400, `dim_airspace_zone` 252, `dim_time` 166, `dim_vehicle` 2 |
| DQ | 36 | 32 PASS, 4 WARN, 0 FAIL |
| WARNs | `DQ-C-003`, `DQ-C-008`, `DQ-A-008`, `DQ-T-003` | `DQ-A-008` observed count not captured |
| Reader proof | PASS | WP-11 apply; per-member `H-017` open |
| Gold views | 3/3 reconcile | `DQ3-A-001` PASS |
| Indexes | 3 `NEUTRAL`; 0 applied | `DQ3-A-006` PASS; 992 KiB avoided |
| DB size | 71.78 MiB | 700 MB guard |
| Raw archive | OPEN | `L-010` |

## Appendix D — Implementation checklist for the PBIX author

- [ ] Import the theme JSON.
- [ ] Set canvas to 1600 × 900; apply page background.
- [ ] Create `_Measures` table and add measures from Section 7.2.
- [ ] Set format strings and display folders.
- [ ] Hide keys and technical columns.
- [ ] Build Page 00 cover and navigation.
- [ ] Build Page 01 executive; test zero-coverage selections.
- [ ] Build Page 02A/2B; add bookmarks and filter bar.
- [ ] Build Page 03 decision; add scorecard and actions.
- [ ] Build Page 04 coverage/scorecard.
- [ ] Build Page 05 ETL/data trust; add DQ/reject/index evidence.
- [ ] Build Page 06 method/traceability.
- [ ] Add tooltip pages and drill-through pages.
- [ ] Add alt text, tab order, and accessibility labels.
- [ ] Refresh; check KPI values against evidence.
- [ ] Capture screenshots PDF with capture date and data-as-of.
- [ ] Record Desktop version, PBIX size, and evidence paths.
- [ ] Request A/D review; do not self-approve.

---

**End of specification.**
