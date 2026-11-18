# Phase 3 Operations, Access and Security

**Status:** extends `Phase2/docs/07_operations_access_and_security.md`; the Phase 2
access model is unchanged and remains authoritative for the warehouse.

## Access model (unchanged)

| Principal | Access |
|---|---|
| Human owner | Admin through Neon/GitHub UI |
| Member A | Write through CI only; release packaging |
| Members B–E | `aerogrid_reader` — `SELECT` only |
| Power BI Desktop | Connects with the reader connection; read-only by construction |
| Public | No warehouse or bucket access |

## Phase 3 additions

1. **BI connections use the reader role only.** No writer credentials in Power BI,
   no shared dataset with embed keys. The `.pbix` file itself may cache data; treat
   it like a derived artifact and keep it under the size guard (`D3-008`).
2. **Artifact handling.** `.sql` files live in Git. `.pdf`/`.pptx`/`.pbix`
   deliverables are committed if < 10 MB each; larger files are published as
   GitHub Actions artifacts instead of being committed.
3. **No Power BI Service publishing** without a human-owned account and an explicit
   decision row (`D3-005`).
4. **Screenshots** must not show connection strings, hostnames with credentials, or
   member PII.

## Capacity guards (carried forward)

| Resource | Warn | Stop and ask |
|---|---|---|
| PostgreSQL storage | 700 MB | 1 GB free limit |
| Object storage | 3.5 GB | 5 GB |
| Compute | 60 CU-h/month | 100 CU-h/month |
| Egress | 3.5 GB | 5 GB |

New indexes and any materialized marts must state their storage impact in their
work package before apply.

## Human-only actions

Creating accounts (including any Power BI Service workspace), accepting terms,
managing Neon/GitHub secrets, changing roles or visibility, submitting course
deliverables, and presenting the final deck. Agents stop and queue these in
[../PROGRESS.md](../PROGRESS.md).
