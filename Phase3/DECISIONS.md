# Phase 3 Decisions

Material decisions for Phase 3, in `D3-###` order. Phase 2 decisions (`D-001` …
`D-031`) remain in force unless a row here explicitly supersedes one. To add a
decision: append a row, state what it changes, and update the canonical document in
the same work package.

| ID | Decision | Date | Supersedes / notes |
|---|---|---|---|
| D3-001 | Phase 3 builds analytics and BI **on the existing Phase 2 warehouse**; schemas, grains, and sources are unchanged | 2026-11-18 | Reaffirms D-014, D-015; new base tables require a new decision |
| D3-002 | All BI deliverables (Power BI `.pbix`, dashboard screenshots, business insights report, final presentation) are owned and authored by **Member E**; other members review only | 2026-11-18 | See [docs/08_team_work_division.md](docs/08_team_work_division.md) |
| D3-003 | Retail terms in the Phase 3 course brief map to AeroGrid domain terms (revenue→observed traffic, orders→journeys, customers→vehicles/operators, products→sources, region→site, channel→source system) | 2026-11-18 | Mapping table in [docs/01](docs/01_phase3_scope_and_objectives.md) |
| D3-004 | Required brief views are renamed to meaningful names: `vw_monthly_sales`→`vw_monthly_traffic_growth`, `vw_customer_analysis`→`vw_vehicle_analysis`, `vw_product_performance`→`vw_source_performance`; the mapping is documented and graded intent is preserved | 2026-11-18 | [docs/04](docs/04_data_model.md) |
| D3-005 | BI tooling is **Power BI Desktop** (free) connecting to Neon with the `aerogrid_reader` role; Power BI Service publishing is human-only and optional | 2026-11-18 | No secrets embedded in shared artifacts; see [docs/07](docs/07_operations_access_and_security.md) |
| D3-006 | Platform stays Neon Free + GitHub Actions; no new paid tooling, no local services | 2026-11-18 | Reaffirms D-001, D-005, D-006 |
| D3-007 | Materialized views are permitted for the gold layer **only after** WP-P3-05 shows with `EXPLAIN ANALYZE` evidence that plain views are insufficient; refresh must stay idempotent | 2026-11-18 | Deferred-proof rule; see [docs/05](docs/05_etl_pipeline.md) |
| D3-008 | Artifact size guard: `.pbix`/PDF/PPT artifacts are committed if < 10 MB each; larger artifacts are published as GitHub Actions release artifacts instead | 2026-11-18 | [docs/07](docs/07_operations_access_and_security.md) |
| D3-009 | Zero values in BI must carry the Phase 2 coverage semantics: empty means missing coverage, never "no events"; every KPI definition cites its source check | 2026-11-18 | Carries D-029 into BI; see [docs/06](docs/06_data_quality_and_reports.md) |
| D3-010 | Index optimization is measured rollback-first: verify mode creates each candidate inside a transaction, records `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` before/after plus index size, and always rolls back; only the `main`-only, token-gated `warehouse` workflow applies DDL, guarded at 700 MB. The PDF is built only from recorded evidence (DQ3-A-006), and a neutral or slower candidate is reported as measured, not claimed as an improvement | 2026-11-19 | WP-P3-05; see [docs/05](docs/05_etl_pipeline.md), [docs/07](docs/07_operations_access_and_security.md), `Phase3/sql/indexes/` |
