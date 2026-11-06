# AeroGrid Diagrams

The canonical Phase 2 logical model is
[`aerogrid_schema.dbml`](aerogrid_schema.dbml). It is synchronized with
[`../data_dictionary.md`](../data_dictionary.md) and
[`../../Phase2/docs/04_data_model.md`](../../Phase2/docs/04_data_model.md).

## Historical exports

The `aerogrid_schema.svg`, `aerogrid_schema.png`, and `aerogrid_schema.pdf` files were
exported from the Phase 1 five-dimension model. They are retained as historical
artifacts and do not show `dim_site`, Phase 2 provenance fields, or the refined fact
grains.

Do not present those exports as the current model. Re-export them from the DBML only
after the Phase 2 schema is approved and implemented.

## Status

The DBML is the accepted logical schema. No database table exists yet; physical DDL is
authorized only inside the owning work package: `WP-04` for staging, `WP-05` for
dimensions, and `WP-06`/`WP-07` for facts.
