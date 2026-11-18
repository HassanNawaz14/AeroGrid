-- WP-P3-05 / Phase 3 candidate indexes (P3-G3, Member D)
-- Idempotent CREATE INDEX IF NOT EXISTS statements on project_dw only.
-- Verify mode creates these inside a transaction that is always ROLLBACKed;
-- apply mode commits them from protected CI as aerogrid_etl. No base-table rows
-- are inserted, updated, or deleted by this file.
-- Every index names the dashboard-critical query it targets (DQ3-A-006). An
-- unmeasured index is not claimed to be an improvement; the report keeps the
-- measured before/after pair even when the result is neutral or worse.
-- Existing Phase 2 indexes stay untouched; these names intentionally do not
-- collide with them (checked by Phase3/tests/test_index_optimization.py).


-- index_id: IX-P3-05-01
-- index_name: ix_fact_vehicle_tracking_source_event
-- target_query: OQ-P3-05-01
-- rationale: vw_source_performance groups tracking rows by source_system and
--   observed month; a composite (source_system, event_ts) index lets the planner
--   restrict and order by source before the monthly aggregation instead of a full
--   fact scan. It does not duplicate the Phase 2 single-column indexes.
CREATE INDEX IF NOT EXISTS ix_fact_vehicle_tracking_source_event
    ON project_dw.fact_vehicle_tracking (source_system, event_ts);


-- index_id: IX-P3-05-02
-- index_name: ix_fact_vehicle_tracking_site_event_cover
-- target_query: OQ-P3-05-02
-- rationale: vw_monthly_traffic_growth aggregates per site and month and reads
--   vehicle_key, altitude_msl_ft, and ground_speed_kts for the same rows. A
--   covering (site_key, event_ts) index can serve an index-only scan for that
--   aggregation. Phase 2 already has ix_fact_vehicle_tracking_site_event without
--   the INCLUDE columns, so this candidate is only justified if measured cheaper.
CREATE INDEX IF NOT EXISTS ix_fact_vehicle_tracking_site_event_cover
    ON project_dw.fact_vehicle_tracking (site_key, event_ts)
    INCLUDE (vehicle_key, altitude_msl_ft, ground_speed_kts);


-- index_id: IX-P3-05-03
-- index_name: ix_fact_flight_journey_vehicle_cover
-- target_query: OQ-P3-05-03
-- rationale: vw_vehicle_analysis aggregates journey distance, duration, and speed
--   per vehicle_key. A covering (vehicle_key, start_ts) index can avoid touching
--   the journey heap for those aggregates. Phase 2 has
--   ix_fact_flight_journey_vehicle_start without the INCLUDE columns.
CREATE INDEX IF NOT EXISTS ix_fact_flight_journey_vehicle_cover
    ON project_dw.fact_flight_journey (vehicle_key, start_ts)
    INCLUDE (site_key, total_distance_nm, flight_duration_sec, avg_speed_kts,
             source_system);
