# WP-04 Staging Reject Reason Codes

Stable `reason_code` values recorded in `project_staging.stg_reject` and/or row-level
`reject_reason` columns. Codes are source-agnostic where possible; details carry
source-specific context.

| Code | Meaning | Typical sources |
|---|---|---|
| `INVALID_TIMESTAMP` | Timestamp missing, malformed, pre-2000/1970 epoch placeholder, or out of accepted range | Tartan, Nightjar, Nominal, METAR |
| `MISSING_REQUIRED_FIELD` | Required field absent or blank | All |
| `INVALID_NUMERIC` | Numeric parse failure | All |
| `INVALID_BOOLEAN` | Boolean parse failure | Nightjar, Nominal |
| `INVALID_COORDINATE` | Latitude/longitude outside valid range | Tartan, Nightjar, Nominal |
| `ZERO_COORDINATE` | `(0,0)` coordinate; pre-GPS/init row | Nightjar, Nominal |
| `ALTITUDE_OUT_OF_RANGE` | Altitude outside documented plausible range | Tartan, UAS |
| `SPEED_OUT_OF_RANGE` | Speed outside documented plausible range | Tartan, UAS |
| `HEADING_OUT_OF_RANGE` | Heading outside `[0,360)` | Tartan |
| `RANGE_OUT_OF_RANGE` | Negative range/bearing out of signed range | Tartan |
| `BEARING_OUT_OF_RANGE` | Bearing outside `[-180,180]` | Tartan |
| `INVALID_VEHICLE_ID` | Vehicle identifier missing or malformed | Tartan, UAS |
| `MISSING_NATURAL_KEY` | Natural key required for idempotent load is missing | FAA, manifest |
| `INVALID_FEATURE` | GeoJSON/ArcGIS feature missing geometry/attributes | FAA |
| `OUT_OF_SCOPE` | Real row outside the approved study site/date window | All (classified as rejected) |
| `DUPLICATE` | Exact or source-natural-key duplicate; skipped from accepted insert | All |
| `SCHEMA_DRIFT` | Unexpected column/type/content; fail-closed in loader | All |

Reconciliation: for each staging load, `rows_read = rows_accepted + rows_rejected +
rows_duplicate`. `OUT_OF_SCOPE` rows count as rejected with an explicit reason.
