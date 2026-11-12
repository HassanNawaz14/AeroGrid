# WP-07: FAA restriction source-readiness increment

## What is included

This increment **does not write to Neon** and **does not change the WP-07 production fact loader**.
It answers the first integration question: *Does the current, approved FAA national-security TFR layer actually intersect the KBTP study window?*
The existing warehouse currently has zero FAA staging rows, zero real airspace zone members, zero restriction snapshots, and zero 2026 UTC time members.

- `etl/faa_restrictions.py`: standard-library HTTP read-only client for the exact FAA feature layer approved in `docs/source_validation/SRC-FAA-UDDS.md`. Uses `geometryType=esriGeometryEnvelope`, `spatialRel=esriSpatialRelIntersects`, WGS84, pagination, and bounded responses. Reuses `etl.sources.faa.normalize_tfr_feature`.
- `tests/test_faa_restrictions.py`: 11 unit tests using test-only fixtures. No live source dependency for tests.
- `sql/03_facts/09_wp07_faa_readiness.sql`: read-only Neon inventory query.

## Run in CMD from the AeroGrid root

```bat
python -m pytest -q Phase2/tests/test_faa_restrictions.py
python -m pytest -q Phase2/tests
cd Phase2
python -m etl.faa_restrictions --site KBTP
cd ..
```

The live FAA request may fail for network reasons; in that case **do not** interpret failure as zero coverage. The preview uses a documented KBTP-centered 0.25-degree *study box* (not the physical airport boundary). It prints only counts, no raw source rows and no credentials. Do not commit or archive arbitrary raw downloads.

**Interpretation:**
- `real_tfr_features_in_study_box=0`: genuine zero *at this source fetch time*, not a historical assessment of 2022.
- Nonzero features, `active_by_complete_window=0`: the complete, unambiguous effective windows do not prove an active restriction. Missing dates remain `UNKNOWN_WINDOW`.
- Nonzero complete-window active features: next implement source provenance (manifest/object-store archive), accepted staging, zone dimension mapping, 2026 UTC hour keys, `stg_restriction_snapshot`, and a rollback-only protected CI test. Do not execute production writes before that next integration review.

## Scope and limits

This is one approved FAA layer, not the full FAA TFR system. The class/route reference datasets and FAA UAS Facility Maps are separate; **do not** treat standing reference features as active TFRs. The service is current-only, not a 2022 historical archive. Even where a current TFR is active, present-day spatial coverage is not proof of an aircraft violation in 2022.

Sources: `Phase2/docs/source_validation/SRC-FAA-UDDS.md` and the official service:
`https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/Part_Time_National_Security_UAS_Flight_Restrictions/FeatureServer`.

## Before committing

- Check for and exclude generated `__pycache__`, `.env`, raw GeoJSON, secrets, and `patches/`.
- Keep `Phase2/sql/03_facts/06_...`, `07_...`, `08_...` diagnostic queries as separate reviewed source evidence; they do not need to be staged in this increment.
- Do not mark WP-07 or G5 `DONE` merely because unit tests or this preview succeed.
