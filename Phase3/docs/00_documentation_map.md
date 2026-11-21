# Phase 3 Documentation Map

Entry point for Phase 3 documentation. It explains which document is canonical and
who should read what. Phase 2's map (`Phase2/docs/00_documentation_map.md`) covers
everything about the warehouse build itself.

## Start paths

### Human reviewer

1. [Phase 3 README](../README.md) — scope and current status.
2. [Scope and objectives](01_phase3_scope_and_objectives.md) — what Phase 3 is.
3. [Architecture and platform](02_architecture_and_platform.md) — target architecture.
4. [Team division](08_team_work_division.md) — who owns what (BI has one owner).
5. [Progress board](../PROGRESS.md) — gates, blockers, human actions.

### Coding agent

1. [`../../AGENTS.md`](../../AGENTS.md) — repository-wide contract.
2. [`../AGENTS.md`](../AGENTS.md) — Phase 3 contract.
3. [`../PROGRESS.md`](../PROGRESS.md) — current state and blockers.
4. This map.
5. The canonical document for the assigned area.
6. The assigned work package in [dev_plan/01_work_breakdown.md](../dev_plan/01_work_breakdown.md).

## Canonical-source table

| Subject | Canonical document | Secondary reference |
|---|---|---|
| Phase 3 status, gates, human actions | [../PROGRESS.md](../PROGRESS.md) | [../README.md](../README.md) |
| Material decisions | [../DECISIONS.md](../DECISIONS.md) | Decision rows cite their documents |
| Work packages, dependencies, gates | [../dev_plan/](../dev_plan/README.md) | [../dev_plan/02_dependencies_and_gates.md](../dev_plan/02_dependencies_and_gates.md) |
| Scope and objectives | [01_phase3_scope_and_objectives.md](01_phase3_scope_and_objectives.md) | Phase 3 course brief (`Phase3/DWBI Lab Phase 3.pdf`) |
| Architecture and platform | [02_architecture_and_platform.md](02_architecture_and_platform.md) | `docs/Sample Project Architecture Diagram.png` |
| Data sources and licences | [03_data_sources_and_licensing.md](03_data_sources_and_licensing.md) | `Phase2/docs/03_data_sources_and_licensing.md` |
| Data model, KPIs, measures | [04_data_model.md](04_data_model.md) | `Phase2/docs/04_data_model.md`, `data/data_dictionary.md` |
| ETL and refresh pipeline | [05_etl_pipeline.md](05_etl_pipeline.md) | `Phase2/docs/05_etl_pipeline.md` |
| Data quality and reports | [06_data_quality_and_reports.md](06_data_quality_and_reports.md) | `Phase2/docs/06_data_quality_and_reports.md` |
| Dashboard specification | [14_power_bi_dashboard_spec.md](14_power_bi_dashboard_spec.md) | [../PROGRESS.md](../PROGRESS.md) |
| Access, security, artifact handling | [07_operations_access_and_security.md](07_operations_access_and_security.md) | `Phase2/docs/07_operations_access_and_security.md` |
| Release packaging and notes | [../templates/RELEASE_NOTES.md](../templates/RELEASE_NOTES.md) | [../scripts/package_artifacts.py](../scripts/package_artifacts.py), [../deliverables/README.md](../deliverables/README.md), [../reports/README.md](../reports/README.md) |
| SCD Type 2 evaluation (`WP-P3-H3`) | [WP-P3-H3_scd2_evaluation.md](WP-P3-H3_scd2_evaluation.md) | [../sql/scd2_evaluation/](../sql/scd2_evaluation/), [../scripts/evaluate_scd2.py](../scripts/evaluate_scd2.py) |
| Team ownership | [08_team_work_division.md](08_team_work_division.md) | Work packages |
| Agent rules | [09_agent_operating_manual.md](09_agent_operating_manual.md) | [`../AGENTS.md`](../AGENTS.md) |
| Human actions and verification | [10_human_operating_manual.md](10_human_operating_manual.md) | [../PROGRESS.md](../PROGRESS.md) |
| Risks and validation | [11_risks_and_validation.md](11_risks_and_validation.md) | `Phase2/docs/11_risks_and_validation.md` |
| Terms | [12_glossary.md](12_glossary.md) | `Phase2/docs/12_glossary.md` |
| Limitations carried forward | [13_accepted_data_limitations.md](13_accepted_data_limitations.md) | `Phase2/docs/13_accepted_data_limitations.md` |
