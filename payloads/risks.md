## Outstanding evidence-limited risks (2026-11-13)

- **No matched weather observations:** 27,479 tracking records use the unknown weather key (`DQ-C-003` warning). Do not label `dim_weather=-1` as a measured observation.
- **Unknown directly observed ground status:** 27,479 `on_ground` values are NULL (`DQ-C-008`). The 7,433 eligible airborne classifications are a documented screening inference, not observed truth.
- **No current KBTP TFR features / historical gap:** The FAA live-source probe found zero features in one selected box in November 2026; 2022 historical restriction evidence was not loaded (`DQ-T-003` warning).
- **Exact timestamp encounter limitation:** The deployed `wp07-v1` algorithm matches equal timestamps. Diagnostic ±20-second observation pairs do not establish a deployed detector. Zero stored encounter facts are data/policy scoped, not a universal safety conclusion.
- **Physical grain shortfall:** The deployed spatial grid and occupancy are 2D. Claims about an altitude-band model must be qualified or the schema explicitly changed under a reviewed decision.
- **Open acceptance:** G5 rules/coverage, G6 reporting and WP-11 automation, and G7 independent reader-access/end-to-end acceptance still need Member A confirmation. See [closeout handoff](MemberE_Implementation_Evidence_2026-11-13.md).
