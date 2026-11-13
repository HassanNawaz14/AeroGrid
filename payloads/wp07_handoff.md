## Update after the protected persistent WP-07 load — 2026-11-13

**The previous "rollback-only / no persisted facts" status above is historical.** A separate approved one-time CI persistence workflow ran successfully and the user independently verified Neon now contains:

- Tracking facts: **27,479**; unknown grid assignments: **0**.
- Real 2D spatial-grid cells: **3,658** (plus the `-1` unknown member).
- Persisted `wp07-v1` hourly occupancy facts: **1,754**.
- Persisted close-encounter facts: **0**; restriction-activation facts: **0**.
- The three WP-07 tables now exist permanently. This is **not** merely the earlier dry run.

The 2026-11-12 live FAA probe is not a source of historical 2022 TFRs, and the exact-time encounter algorithm cannot prove that no near-time conflicts happened. Review WP07-AIR-01, WP07-GRID-01, the 60-second cap and documented scope limitations; record G5 only with the owner's sign-off. Details: [Member E implementation evidence](MemberE_Implementation_Evidence_2026-11-13.md).
