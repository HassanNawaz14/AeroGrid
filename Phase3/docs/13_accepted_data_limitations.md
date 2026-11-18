# Phase 3 Accepted Data Limitations

**Status:** carried forward. The authoritative register is
`Phase2/docs/13_accepted_data_limitations.md` (`L-001` … `L-010`, all OPEN as of the
Phase 2 close). Phase 3 does **not** close them; it must design around them and
label them in BI artifacts (`D3-009`).

## Carry-forward table

| ID | Limitation (short) | Phase 3 consequence |
|---|---|---|
| L-001 | No weather linkage for tracking | Weather slicers show unknown-member share; label it |
| L-002 | Ground state unobserved | No "airborne-only" KPIs without the eligibility caveat |
| L-003 | Occupancy is 2D with a 60 s cap | Occupancy KPIs are "observed occupancy", not capacity |
| L-004 | Encounter predicate requires identical timestamps | Encounter KPI is 0 with an evidence caveat; do not trend it |
| L-005 | No historical restriction snapshot | Restriction visuals show evaluation rows only |
| L-006 | Reject ledger spans runs | Reject counts are cumulative, not per-window; label scope |
| L-007 | Corridor views are screening-only | No "certified corridor" language anywhere |
| L-008 | UAS staged but not in facts | UAS slices appear only after a real WP-11 load; label gaps |
| L-009 | Zones staged, no dependent facts; OpenSky unused | Airspace visuals limited to staged evidence |
| L-010 | Raw files not archived to object storage | Replayability note in evidence; owned by WP-P3-H1 |

## New Phase 3 limitations

| ID | Limitation | Trigger / owner |
|---|---|---|
| L3-001 | Power BI shows data as of last manual refresh; no Service auto-refresh | Until a human creates a workspace (`D3-005`) — E |
| L3-002 | Growth KPIs are unstable while monthly volumes are small | Revisit after two full months of weekly loads — E |
| L3-003 | Vehicle/operator segmentation is inferred from observed behavior, not real operator identity | Never label segments as real operators — E |

## Standing rule

A limitation may leave this list only through the hardening track or a recorded
decision with evidence — never by rewording a dashboard.
