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
(32 checks: 29 PASS, 3 WARN, 0 FAIL) and WP-10 run `43471616729` (10 views).

| ID | Limitation | Observed state | Trigger that requires implementation | DQ hook | Status |
|---|---|---|---|---|---|
| `L-001` | No weather linkage on tracking facts | 27,479 rows with `weather_key = -1`; the `-1` member is not a measured METAR reading | Any deliverable that attributes traffic, encounters, or corridors to weather, or a METAR/ASOS window that can be joined to the load period | `DQ-C-003` (`WARN`) | `OPEN` |
| `L-002` | Ground state unobserved | `on_ground` is `NULL` on 27,479 rows; 7,433 positions are *inferred* airborne (WP07-AIR-01), not observed | Any ground/air separation requirement, or a source that records on-ground state | `DQ-C-008` (`WARN`) | `OPEN` |
| `L-003` | Occupancy is 2D with a 60-second cap | 3,658 real 0.01-degree cells plus one unknown; 1,754 occupancy facts; no altitude bands; adjacent samples capped at 60 s | Any altitude-band, 3D, or sub-60-second occupancy requirement | `DQ-U-003`, `DQ-R-004` | `OPEN` |
| `L-004` | Encounter predicate requires identical timestamps | 0 production encounter facts; an exploratory 20-second window found 22 prefiltered observation pairs, 0 within the severe/proximity limits | Any deliverable that reports encounter counts, rates, or "no conflicts" claims | `DQ-U-004`, `DQ-R-005`, `DQ-B-001`, `DQ-I-008` | `OPEN` |
| `L-005` | No historical restriction snapshot | 0 restriction activation facts; the FAA inspection in November 2026 found 0 features in the KBTP study box; no 2022 TFR archive is stored | Any restriction-compliance metric or temporal restriction analysis | `DQ-T-003` (`WARN`), `DQ-B-003`, `DQ-R-006` | `OPEN` |
| `L-006` | Reject ledger spans multiple ETL runs | 418 stored rejection events (416 `INVALID_VEHICLE_ID`, 2 `INVALID_TIMESTAMP`); they are not one run's yield | Any single-run yield, quality, or rejection-rate metric | `DQ-R-001` | `OPEN` |
| `L-007` | Corridor views are screening metrics only | `vw_corridor_capacity_inputs` and `vw_candidate_corridor_cells` each return 808 rows over observed cells | Any use as a validated corridor, capacity decision, or planning input | WP-10 view verification | `OPEN` |

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

## Current DQ warnings map exactly to this register

| DQ check | Register entry | Observed | Required treatment |
|---|---|---:|---|
| `DQ-C-003` | `L-001` | 27,479 | Keep `WARN`; disclose in reports |
| `DQ-C-008` | `L-002` | 27,479 | Keep `WARN`; preserve `NULL` source field |
| `DQ-T-003` | `L-005` | 1 | Keep `WARN`; indicator of missing source, not a missing flight |

There are no other open DQ warnings. `0` critical failures is a pass condition, not
evidence that these three limitations are resolved.

## Audit hooks

| Package | Obligation |
|---|---|
| `WP-11` | Run the DQ suite on the weekly/manual cadence and fail only on `FAIL`; publish the three `WARN` counts and their `L-###` mapping in the run summary. |
| `WP-12` | Report every `OPEN` row with its observed value, trigger status, and owner. A limitation may be closed only with linked evidence and a `PROGRESS.md` entry. |

## Change history

| Date | Change | Reference |
|---|---|---|
| `2026-11-13` | Created the register from the G5–G7 accepted limitations; verified current values against live warehouse runs `43471609483` and `43471616729`. | `D-028` |
