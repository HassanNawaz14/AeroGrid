# Member E / WP-07 — source readiness remediation and acceptance record

## What was missing

1. Real Tartan records in `project_dw.fact_vehicle_tracking` have `on_ground=NULL` because the WP-04 source mapper cannot prove this state from Tartan's raw fields. `NULL` is **not** evidence of flight.
2. `dim_spatial_grid` has only the `-1` unknown row, because WP-05's real vehicle seed intentionally did not invent a grid. Existing tracking facts therefore use `grid_key=-1`.
3. These gaps block defensible airborne occupancy and derived encounter eligibility. This is remediation of earlier work and should be explicitly reviewed with the owners.

## Recommended fix (analytical, not aviation safety guidance)

### Airborne policy `WP07-AIR-01`

- Preserve original `fact_vehicle_tracking.on_ground` unchanged.
- `OBSERVED_AIRBORNE` only when source explicitly records `on_ground=False`.
- `OBSERVED_GROUND` only when source explicitly records `on_ground=True`; ground overrides any inferred signals.
- `INFERRED_AIRBORNE`: Tartan, KBTP, `TARTAN_ALTISGNSS_FALSE` (barometric datum indicator), ground speed **>=120 knots**, aircraft altitude MSL **>= surveyed KBTP elevation 1248.4 ft + 1000 ft**, and position within **10 NM** of KBTP survey coordinates.
- All other cases: `UNKNOWN` and excluded from airborne-derived facts. Never convert null ground-state to false or claim an inference is observed.

These are **proposed high-confidence analytical screening thresholds** chosen to reduce false positives. They are **not** the approved H-013 encounter separation thresholds, and are **not** a formal flight/ground detector. Airport elevation is not terrain elevation. If the team wants weaker/stricter rules, document a new decision and version the algorithm *before* trusting the results. The real sample must be checked for eligible counts in dry-run CI; zero eligible points is a blocker, not grounds to fabricate data.

Evidence sources (not data inputs):
- TartanAviation Scientific Data paper, original ADS-B column definitions, `Altitude` in feet MSL, `AltisGNSS` as altitude-measurement indicator: https://www.nature.com/articles/s41597-025-04775-6
- FAA/AirNav KBTP surveyed elevation 1248.4 ft MSL and approximate reference point 40.7765833, -79.9510833: https://www.airnav.com/airport/KBTP

### Spatial policy `WP07-GRID-01`

- Use a **2D, site-scoped, stable** geographic grid of 0.01-degree WGS84 bins, not a fabricated set of sample aircraft positions.
- For each accepted real Tartan position *already tied to an accepted tracking fact*, compute `lat_index=floor(latitude*100)`, `lon_index=floor(longitude*100)` and ID `wp07-g01:{site_key}:{lat_index}:{lon_index}`.
- Insert a grid member only for a cell containing at least one accepted real position. Store cell center (not an invented observation) in `lat_bin/lon_bin`.
- In the same approved transaction, backfill **only** tracking records currently mapped to `-1`, joining source IDs to real accepted `stg_adsb_position` rows and the derived cell ID. Use the `site_key` check.
- Use the optional `facts.py` patch to resolve new facts with the exact deterministic cell ID, falling back to old behavior for any preexisting grids.
- Existing table's occupancy grain is `(time_key, grid_key, algorithm_version)`, i.e. **hour × 2D grid**. Do not claim altitude-band occupancy until the schema has an altitude-band dimension and matching approved grain; there is no such column today.
- A 0.01-degree cell has varying ground dimensions by latitude (approximately 1.11 km north/south, 0.84 km east/west near KBTP). Do not call it a 1 km × 1 km rectangle.

## Execution order / safety

1. Check the patch with `git apply --check patches/01_wp07_core_grid_lookup.patch`; **do not overwrite the owner's `facts.py`** if the patch fails. Apply only after review.
2. Run new and full unit tests. Record counts and any changed existing tests.
3. CI dry run: `python -m etl.verify_wp07_facts` from `Phase2` on the approved `warehouse` runner. This executes grid seed/backfill, DDL, and derived mapping inside **one transaction**, then rolls back. No data remains changed.
4. Review input/output counts, grid-site consistency, observed/inferred/unknown classification counts, encounters, occupancy and restriction counts, idempotency. Zero encounters or restrictions can be honest results and should be documented.
5. Only after review and approved threshold decision, run the same workflow with explicit `--apply` (protected CI only). Then separately check stored counts and read-only access.
6. Update `data/data_dictionary.md`, `data/diagrams/aerogrid_schema.dbml`, `Phase2/docs/04_data_model.md`, `Phase2/DECISIONS.md`, and `Phase2/PROGRESS.md` to record method, limitations, results, changes and reviewer handoff. Do NOT mark WP-07 or G5 DONE based on successful local unit tests alone.

## Correctness caveats worth documenting at G5

- Source Tartan positions may represent receptions with age/staleness and altitude uncertainty; a high-confidence filter does not prove airborne status with aviation-grade precision.
- Position sets commonly have asynchronous timestamps. The current WP-07 encounter algorithm pairs **exactly equal** timestamps only, so an empty encounter table must not be interpreted as zero real conflicts. Before attempting ±seconds matching/interpolation, approve a temporal alignment rule and test it separately.
- Occupancy `total_occupancy_minutes` is observed *within-cell* adjacent-sample duration under the gap cap; it can undercount residence between sparse pings. It is not a synthetic trajectory duration.
- To use other sites, adopt appropriate terrain-elevation evidence and source-specific altitude policy; never apply KBTP elevation to KAGC or UAS sites.
- Always preserve original source IDs and ETL run lineage.
