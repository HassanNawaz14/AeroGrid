# Risks and Validation

## Purpose

This register tracks the risks that could invalidate the Phase 2 warehouse, break the
free-tier boundary, or breach the project constraints. Risks are reviewed before each
gate. Owners are placeholders until the human assigns names.

## Risk rating

| Rating | Meaning |
|---|---|
| High | Blocks a core deliverable or violates a constraint |
| Medium | Degrades quality, schedule, or reviewability |
| Low | Manageable with routine mitigation |

Probability and impact use `High`, `Medium`, or `Low`. A high/high risk requires a
human decision before the dependent work package proceeds.

## Risk register

| ID | Risk | Probability | Impact | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|
| `R-01` | Free-tier database capacity is insufficient | Medium | High | A | Curated window, raw in object storage, 700 MB warning, occupancy precomputation | DB > 700 MB or load estimate exceeds budget |
| `R-02` | Object storage exceeds 5 GB | Low | High | B | Archive selected CSVs only; no DJI video; retention review | Bucket > 3.5 GB |
| `R-03` | Tartan georeferencing is wrong | Medium | High | B + D | Validate known points/runway; document local-frame conversion; inspect sample tracks | Track outside airport or impossible speed |
| `R-04` | Tartan volume is too large for a full load | High | Medium | B + D | Load a documented window; archive full raw; measure before load | Parsed rows or DB estimate exceed budget |
| `R-05` | Nightjar/DJI timestamps are relative, not absolute | High | Medium | B + D | Preserve relative time; derive an explicit flight start only if source supports it; do not invent UTC | Timestamp starts at zero or 1970 |
| `R-06` | UAS and manned data cannot be spatially joined | Medium | High | D + E | Validate site mapping and coordinates; only pair within site/time; document limitations | Pairing requires impossible time travel |
| `R-07` | Historical TFR coverage is unavailable | High | Medium | B + E | Use real snapshots/effective windows; document forward-only limitation; do not synthesize TFRs | No historical TFR source |
| `R-08` | OpenSky historical access is unavailable | High | Low | A + B | Treat OpenSky as optional; use Tartan for primary ADS-B | Human cannot obtain access |
| `R-09` | Source schema changes | Medium | High | B | Snapshot parser, contract tests, fail closed on drift | Missing/new column or unexpected type |
| `R-10` | License terms are unclear or change | Low | High | Human | Record license/URL; ask before loading; attribution section | Terms unclear or source restricts use |
| `R-11` | Secret exposed | Low | High | Human + A | Environment secrets, no `.env`, rotate immediately, scan diff | Secret in Git/log/chat |
| `R-12` | Critical DQ fails before review | Medium | High | E | Fail closed, preserve previous data, publish report, ask human | `dq_result` critical FAIL |
| `R-13` | Thresholds are tuned to make results look good | Medium | High | E + Human | Pre-register thresholds, record algorithm version, do not tune after seeing results without decision | Threshold changes after results |
| `R-14` | Duplicate facts after rerun | Medium | High | C + D | Natural keys, unique constraints, idempotent upserts, reconciliation | Counts grow on identical rerun |
| `R-15` | Surrogate-key mapping is wrong | Medium | High | C | Seed `-1`, map on natural keys, orphan checks, review | Orphans or mismatched joins |
| `R-16` | Vehicle identity is merged incorrectly | Medium | Medium | C + D | Keep source-scoped identities; merge only with evidence | One key maps to unrelated vehicles |
| `R-17` | GPS/altitude quality is overstated | Medium | Medium | D + E | Report source accuracy; do not claim precision beyond data | Encounter distances near GPS noise |
| `R-18` | Derived metrics are mistaken for observed facts | Medium | High | E | Label derived facts and `algorithm_version`; explain in reports | Report treats estimated occupancy as measured |
| `R-19` | Team member unavailable | Medium | Medium | Human + A | Reviewer coverage, handoff template, no single point of failure | No reviewer or owner available |
| `R-20` | Scope creep | Medium | Medium | Human | One WP at a time; change requires decision record | New source/metric without approval |
| `R-21` | Implementation starts before G1 | Medium | High | A | Gate check at session start; refusal rule | Agent creates SQL/workflow early |
| `R-22` | Public repo exposes data that should not be public | Low | High | Human | Do not commit raw data; review reports for sensitive content | Raw archive or personal data in Git |
| `R-23` | Windows path/encoding issues break scripts | Medium | Low | A | Use pathlib, UTF-8, CI Linux as canonical | Local-only path failure |
| `R-24` | Free-tier compute/egress exceeded | Low | Medium | A | Weekly/manual runs, query reporting views, no polling | Usage warning |
| `R-25` | Neon project deletion or branch loss | Low | High | Human | Human-only destructive actions; raw archive is durable | Resource missing |
| `R-26` | Report claims cannot be reproduced | Medium | High | E | Store counts/checks, run IDs, code version; report evidence | PDF has no database evidence |
| `R-27` | Rubric mismatch | Low | High | A | Map every rubric item to acceptance evidence | Missing staging/report/DB evidence |
| `R-28` | Course policy on public data/AI use is unclear | Low | High | Human | Confirm policy; document real-data provenance and agent role | Instructor raises concern |
| `R-29` | Legacy synthetic sample files remain tracked | Medium | High | Human + A | Exclude from loads, document as legacy, and resolve `H-008` before implementation | Synthetic file appears in a load/report |

## Validation plan

Validation happens in `WP-03` before any full load. It uses small, real samples and
does not create synthetic data.

### Tartan

1. Download a small real sample or the documented archive.
2. Identify fields for time, position, altitude, vehicle, and source.
3. Confirm coordinate frame and georeferencing method.
4. Compare converted coordinates to a known airport reference.
5. Check speed, heading, and altitude plausibility.
6. Count rows and estimate full-load size.
7. Record findings and unresolved questions.

Pass: converted tracks are inside the airport region, plausible speeds, and a
documented unit/datum mapping. Fail: any unresolved coordinate or unit ambiguity.

### Nightjar

1. Download only the CSV/GeoJSON files.
2. Confirm columns, row count, and time base.
3. Validate GPS coordinates and site.
4. Confirm 10 Hz claim from timestamps.
5. Check altitude datum and units.
6. Identify flight boundaries.
7. Do not download media.

Pass: coordinates match the documented site, timestamps are monotonic, units are
known. Fail: relative timestamps that cannot be anchored or unresolved altitude.

### Nominal-io DJI

1. Download only the three CSV files.
2. Confirm license and attribution.
3. Validate timestamps, coordinates, altitude, and serial.
4. Check row counts and duplicates.
5. Confirm no video is needed.

Pass: real flights, valid coordinates, documented units. Fail: unreadable schema or
unresolved time base.

### FAA

1. Query each layer with a small bounding box.
2. Confirm field names, geometry types, and pagination.
3. Confirm query limits and caching behavior.
4. Check whether TFR features include effective windows.
5. Store the snapshot timestamp.

Pass: geometry and attributes usable; historical limitation documented. Fail: no
usable geometry or unclear license.

### Weather

1. Fetch a real METAR for a known station/time.
2. Confirm units and null handling.
3. Confirm historical IEM query works for the data window.
4. Map stations to sites.
5. Test a missing-observation case.

Pass: real observations parse and station mapping is defensible. Fail: invalid units
or no historical coverage.

### OpenSky

1. Test anonymous current-state access only if used.
2. Do not assume historical access.
3. Record rate-limit behavior.
4. Keep it optional.

Pass: optional snapshot works and terms are acceptable. Fail: treat as unavailable;
do not block Phase 2.

## Validation evidence

Record in `Phase2/templates/SOURCE_VALIDATION.md`:

- Source URL and license.
- File name, size, SHA-256, fetch time.
- Row count and sample identifiers.
- Column mapping.
- Unit and time-base findings.
- Georeferencing result.
- Known limitations.
- Pass/fail decision.
- Reviewer.

## Capacity validation

Before a full load:

1. Parse the sample.
2. Estimate bytes per fact row.
3. Estimate total rows for the load window.
4. Add index overhead.
5. Compare to the 1 GB limit.
6. If the estimate exceeds 700 MB, reduce the window or aggregate before loading.
7. Record the estimate and decision.

Do not discover capacity by filling the database.

## Risk review points

| Gate | Review |
|---|---|
| `G1` | Human approvals, platform, source licenses, capacity assumptions |
| `G2` | Platform access proof, source validation, georeferencing, capacity estimate |
| `G3` | Staging, schema, key integrity, and dimension seeds |
| `G4` | Core fact reconciliation and idempotency |
| `G5` | Derived facts and threshold approval |
| `G6` | DQ, reports, reporting views, and automation |
| `G7` | Final acceptance and demo |

## Escalation

Stop and ask the human when a risk becomes a blocker, when a mitigation would change
scope, or when the free-tier boundary is at risk. Record the blocker in
`PROGRESS.md`; do not silently absorb it.
