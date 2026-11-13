# Accepted Data Limitations and Implementation Triggers

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

This document is the canonical register of data limitations that Phase 2 has
**accepted rather than fixed**. Each entry carries the condition that turns the
limitation from an accepted caveat into required implementation work. A limitation is
never closed by silence, by a re-run, or by changing DQ severity.

## Authority

- The limitations were accepted administratively on 2026-11-13 under
  `D-025`, `D-026`, and `D-027`, and are summarised in the
  [final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).
- Administrative acceptance records a decision. It does not prove the limitation is
  harmless, and it does not permit hiding it in reports or DQ results.
- The register itself is created under `D-028` in [DECISIONS.md](../DECISIONS.md).

## Rules

1. **No silent closure.** An entry stays `OPEN` until the trigger is met, the work is
   done, and evidence is recorded in [PROGRESS.md](../PROGRESS.md).
2. **No silent severity change.** The linked DQ checks must not move from `WARN` to
   `PASS` by policy edit. Removing a warning requires the underlying data change.
3. **Unexpected movement is a finding.** If a linked DQ `observed` count changes
   without a corresponding source or load change, treat it as a regression and record
   a blocker.
4. **Scope or source changes stay human-gated.** Implementing any entry's "required
   work" may add a source, change the model, or change thresholds. That is a
   stop-and-ask decision, not an agent decision.
5. **Every audit reports the register.** `WP-11` includes the linked checks; `WP-12`
   reports every open row with its current observed value.

## Register

State verified against the live warehouse on 2026-11-13 by WP-08 run `43471609483`
(32 checks: 29 PASS, 3 WARN, 0 FAIL) and WP-10 run `43471616729` (10 views). After
the coverage guards were added, WP-08 run `43478821521` re-verified 36 checks
(30 PASS, 6 WARN, 0 FAIL) and WP-09 run `43478947023` generated both PDFs with the
coverage section rendered. The first approved `mode=apply` run
[`43502710978`](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43502710978)
then persisted all 36 checks under `etl_run_id=11` (32 PASS, 4 WARN, 0 FAIL) together
with real staging and dimension rows.

| ID | Limitation | Observed state | Trigger that requires implementation | DQ hook | Status |
|---|---|---|---|---|---|
| `L-001` | No weather linkage on tracking facts | 27,479 rows with `weather_key = -1`; the `-1` member is not a measured METAR reading | Any deliverable that attributes traffic, encounters, or corridors to weather, or a METAR/ASOS window that can be joined to the load period | `DQ-C-003` (`WARN`) | `OPEN` |
| `L-002` | Ground state unobserved | `on_ground` is `NULL` on 27,479 rows; 7,433 positions are *inferred* airborne (WP07-AIR-01), not observed | Any ground/air separation requirement, or a source that records on-ground state | `DQ-C-008` (`WARN`) | `OPEN` |
| `L-003` | Occupancy is 2D with a 60-second cap | 3,658 real 0.01-degree cells plus one unknown; 1,754 occupancy facts; no altitude bands; adjacent samples capped at 60 s | Any altitude-band, 3D, or sub-60-second occupancy requirement | `DQ-U-003`, `DQ-R-004` | `OPEN` |
| `L-004` | Encounter predicate requires identical timestamps | 0 production encounter facts; an exploratory 20-second window found 22 prefiltered observation pairs, 0 within the severe/proximity limits | Any deliverable that reports encounter counts, rates, or "no conflicts" claims | `DQ-U-004`, `DQ-R-005`, `DQ-B-001`, `DQ-I-008` | `OPEN` |
| `L-005` | No historical restriction snapshot | 0 restriction activation facts; the FAA inspection in November 2026 found 0 features in the KBTP study box; no 2022 TFR archive is stored | Any restriction-compliance metric or temporal restriction analysis | `DQ-T-003` (`WARN`), `DQ-B-003`, `DQ-R-006` | `OPEN` |
| `L-006` | Reject ledger spans multiple ETL runs | 418 stored rejection events verified 2026-11-13 (416 `INVALID_VEHICLE_ID`, 2 `INVALID_TIMESTAMP`); run 11 added 160 more (1 `INVALID_TIMESTAMP`, 159 `ZERO_COORDINATE`), so the ledger now spans more runs | Any single-run yield, quality, or rejection-rate metric | `DQ-R-001` | `OPEN` |
| `L-007` | Corridor views are screening metrics only | `vw_corridor_capacity_inputs` and `vw_candidate_corridor_cells` each return 808 rows over observed cells | Any use as a validated corridor, capacity decision, or planning input | WP-10 view verification | `OPEN` |
| `L-008` | UAS sources are validated but never ingested | Run 11 loaded 22,602 accepted UAS positions into `project_staging.stg_uas_position` (Nightjar 12,447; DJI 10,155) and created 2 `dim_vehicle` members. No UAS tracking, journey, or encounter fact exists yet, so the limitation survives the staging load | Any deliverable that reports UAS traffic, UAS-to-manned separation, or combined airspace use | `DQ-G-003` (`WARN`) | `OPEN` |
| `L-009` | Airspace zones are never staged; OpenSky is unused | Run 11 staged 252 zones (Class 82, Route 170; Special Use 0 inside the study boxes) and created 252 `dim_airspace_zone` members. `project_staging.stg_opensky_state` holds 0 rows; OpenSky is optional under `D-013` and has no loader | Any deliverable that reports zone membership, zone proximity, occupancy inside a zone, or an OpenSky-derived metric | `DQ-G-004` (`WARN`) | `OPEN` |
| `L-010` | Fetched raw files are not archived to object storage | Every `WP-11` run downloads sources into a transient runner directory. No raw object is written to `aerogrid-raw` and no manifest-linked archive exists, so the exact bytes behind a load cannot be re-read later | Any provenance audit that needs the original bytes, or a re-run that must reproduce past input without network access | None; the run summary states it on every run | `OPEN` |

`L-008` and `L-009` were 0 rows before the first approved apply. Run 11 filled their
staging tables and flipped `DQ-G-002`–`DQ-G-004` to `PASS`, but staging coverage does
not close either entry: no UAS or restriction fact loader exists. See
[WP-11 ingestion status](#wp-11-ingestion-status-2026-11-14).

## Required work per trigger

### `L-001` Weather linkage

Stage and accept METAR/ASOS observations covering the load window, populate real
`dim_weather` members, backfill `weather_key` through the approved mapping path, then
re-derive facts and re-run `DQ-C-003`. Do not invent a weather row to clear the
warning, and do not substitute the `-1` unknown member for an observation.

### `L-002` Ground state

Use a source that records ground state, or promote the WP07-AIR-01 inference into an
explicitly labelled derived column with a documented rule. Keep the source
`on_ground` value `NULL`; never overwrite it with an inference.

### `L-003` Occupancy grain

Add an altitude-band grid dimension, record the new rule under a new
`algorithm_version`, and keep `wp07-v1` facts intact for comparability. A shorter
occupancy cap needs the same versioning treatment.

### `L-004` Encounter method

Implement the documented near-time matcher as a new `algorithm_version` with approved
thresholds. The 22-pair exploratory result is analysis evidence, not production fact
data, and must not be loaded as encounter records without that approval.

### `L-005` Restriction snapshot

Obtain a historical TFR/airspace snapshot that covers the flight window and has
usable provenance. Joining 2026 restrictions to 2022 flights is prohibited.

### `L-006` Reject ledger

Report rejects per `etl_run_id` using `project_staging.etl_run_log`. Never add
`stg_reject` counts to accepted staging rows to claim a single-run input total.

### `L-007` Corridor views

Either approve the corridor methodology and label the views accordingly, or keep the
"preliminary screening" label in every report and dashboard that uses them.

### `L-008` UAS ingestion

Call the existing `load_nightjar` and `load_nominal` loaders from the scheduled
ingestion path instead of from tests, stage the real rows, populate `dim_vehicle`
members for the UAS types, and re-derive the dependent facts. This is an
implementation step, not a source change: the sources are already approved under
`D-011`.

### `L-009` Airspace and OpenSky coverage

Stage the approved granular FAA features (`D-020`) into `stg_airspace_zone`, load
`dim_airspace_zone`, then re-derive occupancy and restriction facts. Enabling
OpenSky requires a separate human decision: it is optional under `D-013`, currently
has no loader, and its provenance and licence must be reviewed before use.

### `L-010` Raw archive

Persist each fetched source file to the private `aerogrid-raw` bucket and link it from
`source_manifest` before the transaction commits. Until that exists, provenance rests
on the recorded URL, fetch timestamp, and SHA-256 in `source_manifest`, which proves
what was read but cannot reproduce the bytes. Do not commit raw files to Git as a
substitute; that is prohibited by the repository rules.

## Coverage completion plan

This table answers "when is each staging table filled, and with how much data".
"Filled" means the source's real rows are accepted into staging by the scheduled
ingestion job, not that a sample was validated in a test. Volumes are the `WP-03`
initial-load estimate in
[11_risks_and_validation.md](11_risks_and_validation.md#risk-review-points); they are
planning figures, not accepted-row counts.

| Staging table | Filled by | Package | Expected volume (initial load) | Current state | Blocking precondition |
|---|---|---|---|---|---|
| `stg_adsb_position` | Tartan KBTP loader (running today) | `WP-06` (done) | ~609,000 rows for one week (~122–305 MB) | 27,479 accepted rows for 2022-01-01 | None |
| `stg_weather_metar` | AWC/IEM METAR loader | `WP-11` (done) | under 1,000 rows for the initial study dates (<0.5 MB) | 400 accepted rows from run 11 (2026-11-07..2026-11-13) | `L-001` additionally needs `weather_key` backfill |
| `stg_uas_position` | Nightjar and nominal-io DJI loaders | `WP-11` (done) | 22,762 rows (Nightjar 12,448 + DJI 10,314) | 22,602 accepted rows from run 11 | `L-008` additionally needs dependent facts |
| `stg_airspace_zone` | FAA granular airspace loader | `WP-11` (done) | under 1,000 filtered study-site features (<1 MB) | 252 accepted zones from run 11 | `L-009` additionally needs dependent facts |
| `stg_restriction_snapshot` | FAA TFR snapshot loader | `WP-11` ingestion, `WP-12` audit | unknown; 0 until a real historical snapshot is found | 0 rows; no loader | Needs a real historical snapshot covering the flight window; `L-005` may stay `OPEN` |
| `stg_reject` | All loaders (rejection ledger) | `WP-06`, `WP-11` | grows with every load | 418 stored events before run 11; run 11 added 160 | `L-006` reporting rule |
| `stg_opensky_state` | No loader exists | Not planned | 0 | 0 rows | Requires a new human decision; optional under `D-013` |

**Planned initial total:** ~632,000 rows and ~130–320 MB with indexes. That is below
the 500 MiB target and the 1 GiB free-tier limit. The full Tartan year (~22 million
rows, ~4.4 GB) is deliberately excluded because it exceeds that limit.

`WP-11` is the package that turns validation into recurring ingestion. Until its
ingestion workflow runs, every empty row above is missing coverage, not measured
zero. The coverage DQ checks (`DQ-G-001`–`DQ-G-004`) and the coverage section in
both PDFs make that distinction explicit on every run.

### How the ingestion job fills the tables

The sequence itself is already canonical: run modes (`initial`, `weekly`, `validate`,
`reports`), the end-to-end flow, and the manual-dispatch inputs are specified in
[05_etl_pipeline.md](05_etl_pipeline.md#run-modes). `WP-11` implements it as one
GitHub Actions workflow (`workflow_dispatch` plus the weekly Monday 06:00 UTC
schedule under `D-018`/`D-019`):

```
read approved source -> validate -> write staging (stg_*) and rejects
-> upsert dimensions -> map keys -> load core facts -> derive occupancy/restrictions
-> run DQ -> write run summary -> build both PDFs as artifacts
```

The loaders and normalizers already exist and are unit-tested. `WP-11` adds the job
that calls them and records `etl_run_log`, `source_manifest`, and `dq_result` rows:
`Phase2/etl/run.py` under `.github/workflows/wp11-ingest.yml` (`D-030`).

### WP-11 ingestion status (2026-11-14)

The pipeline is implemented and has completed its first approved warehouse write. It
has two modes:

- `validate` — fetch and parse real sources, no database access, no secret. Refuses
  the run if a requested source yields zero accepted rows.
- `apply` — one transaction for `source_manifest`, staging, rejects, dimension
  refresh, and DQ. Requires the protected `warehouse` job, `main`, a typed
  confirmation, and the `WAREHOUSE_CI_APPROVED` marker. A `CRITICAL` DQ failure rolls
  back the ingestion and records a separate `FAILED` run with the captured DQ rows.
  Apply also refuses an empty source before the first write, because the persisted
  coverage checks are table-wide and historical rows would otherwise keep them green.

Read-only validate run, 2026-11-14, window 2026-11-07 to 2026-11-14, stations
`KBTP`,`KAGC`:

| Source file | Rows read | Accepted | Rejected | Reject reason |
|---|---:|---:|---:|---|
| `weather:awc_KBTP_KAGC_*.json` | 400 | 400 | 0 | - |
| `uas:nightjar_20260804.csv` | 12,448 | 12,447 | 1 | `INVALID_TIMESTAMP` (epoch-zero row) |
| `uas:nominal_colorado.csv` | 2,781 | 2,622 | 159 | `ZERO_COORDINATE` |
| `uas:nominal_palos_verdes.csv` | 4,260 | 4,260 | 0 | - |
| `uas:nominal_offshore_sf.csv` | 3,273 | 3,273 | 0 | - |
| `airspace:faa_Class_Airspace.geojson` | 82 | 82 | 0 | - |
| `airspace:faa_Special_Use_Airspace.geojson` | 0 | 0 | 0 | service answered; no feature intersects the five study boxes (1,545 nationally) |
| `airspace:faa_Route_Airspace.geojson` | 170 | 170 | 0 | - |
| **TOTAL** | **23,414** | **23,254** | **160** | |

These are parsed counts from a read-only run, not staging rows.

The first approved `mode=apply` run
([`43502710978`](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43502710978),
`etl_run_id=11`, commit `165d59d`) completed `SUCCESS` in 35 s with:

| Result | Value |
|---|---|
| Rows read / accepted / rejected / duplicate | 23,414 / 23,254 / 160 / 0 |
| Source manifests recorded | 8 |
| Dimensions inserted | `dim_weather` 400, `dim_airspace_zone` 252, `dim_time` 166, `dim_vehicle` 2 |
| DQ checks persisted | 36: 32 `PASS`, 4 `WARN` (`DQ-C-003`, `DQ-C-008`, `DQ-A-008`, `DQ-T-003`), 0 `FAIL` |
| Coverage guards | `DQ-G-002`, `DQ-G-003`, `DQ-G-004` now `PASS`; `DQ-G-001` `PASS` |
| Reader proof job | `PASS` on the same dispatch: `aerogrid_reader` can `SELECT` and cannot write |

What remains for `WP-11` acceptance is the weekly schedule switch and per-member
reader proof: the schedule stays inert until a human creates
`WP11_SCHEDULE_ENABLED=true`; unattended writes additionally require
`WP11_SCHEDULE_APPLY_ENABLED=true`. Both are repository variables, not secrets, and
are human-only actions.

### Why the volumes are this size

No row is removed to make a number look better. Each limit comes from a documented
constraint:

| Reduction | Reason | Where it is recorded |
|---|---|---|
| One week of Tartan, not a year | A year is ~22 million rows (~4.4 GB) and exceeds the 1 GiB free-tier limit; free tiers only is `D-006` | [11_risks_and_validation.md](11_risks_and_validation.md#risk-review-points), [03_data_sources_and_licensing.md](03_data_sources_and_licensing.md) |
| UAS data is ~22,762 rows | The providers publish exactly these datasets: Nightjar `20260804` (12,448 rows) and three nominal-io DJI flights (10,314 rows). We load the real published sample, not a thinned copy | [03_data_sources_and_licensing.md](03_data_sources_and_licensing.md) |
| Airspace is filtered by study site | FAA publishes 12,849 national features; only the few dozen intersecting each study site (19–90 per site) can affect these flights, so the rest is not loaded | [03_data_sources_and_licensing.md](03_data_sources_and_licensing.md), `D-020` |
| Weather is the stations and hours around the flight window | Only that window can be joined honestly to these flights; a wider window would not match any tracking fact | [03_data_sources_and_licensing.md](03_data_sources_and_licensing.md), `L-001` |
| 0 encounters, 0 restrictions, 2D grid, 60-second cap | Method and source limits, not deletion: the encounter predicate needs identical timestamps, no 2022 TFR archive exists, and `wp07-v1` is a 2D grid with a 60-second sample cap | `L-003`, `L-004`, `L-005` |

## Current DQ warnings map exactly to this register

| DQ check | Register entry | Observed | Required treatment |
|---|---|---:|---|
| `DQ-C-003` | `L-001` | 27,479 | Keep `WARN`; disclose in reports |
| `DQ-C-008` | `L-002` | 27,479 | Keep `WARN`; preserve `NULL` source field |
| `DQ-T-003` | `L-005` | 1 | Keep `WARN`; indicator of missing source, not a missing flight |
| `DQ-G-002` | `L-001` | 1 | Keep `WARN`; 0 accepted METAR rows |
| `DQ-G-003` | `L-008` | 1 | Keep `WARN`; 0 accepted UAS rows |
| `DQ-G-004` | `L-009` | 1 | Keep `WARN`; 0 accepted airspace-zone rows |

`DQ-G-001` (`CRITICAL`) is the opposite guard: if the primary source ever produces
zero accepted rows, the run fails instead of reporting zero events.

There are no other open DQ warnings. `0` critical failures is a pass condition, not
evidence that these limitations are resolved.

## Audit hooks

| Package | Obligation |
|---|---|
| `WP-11` | Run the DQ suite on the weekly/manual cadence and fail only on `FAIL`; publish the `WARN` counts and their `L-###` mapping in the run summary, including the source-coverage rows (`DQ-G-002`–`DQ-G-004`). |
| `WP-12` | Report every `OPEN` row with its observed value, trigger status, and owner. A limitation may be closed only with linked evidence and a `PROGRESS.md` entry. |

## Change history

| Date | Change | Reference |
|---|---|---|
| `2026-11-13` | Created the register from the G5–G7 accepted limitations; verified current values against live warehouse runs `43471609483` and `43471616729`. | `D-028` |
| `2026-11-13` | Added `L-008` (UAS never ingested) and `L-009` (airspace never staged, OpenSky unused); added the coverage completion plan with expected volumes, the ingestion sequence, and the documented reason for each volume limit; added the `DQ-G-001`–`DQ-G-004` coverage guards. | `D-029` |
| `2026-11-14` | Added `L-010` (fetched raw files are not archived); recorded the WP-11 validate/apply pipeline and its read-only validate counts; noted that staging coverage does not close `L-001`, `L-008`, or `L-009`. | `D-030` |
| `2026-11-14` | Recorded the first approved apply run `43502710978` (`etl_run_id=11`): 23,254 accepted rows, 8 manifests, 820 dimension rows, 36 DQ results (32 PASS / 4 WARN / 0 FAIL), reader proof `PASS`. Updated `L-006`, `L-008`, and `L-009` observed values; all stay `OPEN`. | `D-030`, `B-015` |
