# Phase 2 PR Checklist

## Scope

- [ ] PR is limited to one work package.
- [ ] The work package is authorized and its prerequisites are met.
- [ ] No unrelated refactor or Phase 1 edit is included.

## Data and sources

- [ ] Only real public data is used.
- [ ] Source URL, license, fetch time, size, and SHA-256 are recorded.
- [ ] No raw archive, dump, large binary, or synthetic row is added.
- [ ] Derived rows trace to real input rows.
- [ ] No threshold was changed silently.

## Model and keys

- [ ] Grain is documented.
- [ ] Primary, natural, and surrogate keys are correct.
- [ ] `-1` unknown members are respected.
- [ ] No orphan or duplicate natural keys.
- [ ] Rerun is idempotent.
- [ ] Counts reconcile.

## Quality

- [ ] Critical DQ checks pass or the PR is explicitly blocked.
- [ ] Warnings are visible in the report.
- [ ] The check catalog matches the stored results.
- [ ] No fabricated passing evidence.

## Security and operations

- [ ] No secret, `.env`, token, or connection string is included.
- [ ] No local database or Docker dependency is added.
- [ ] Free-tier limits are respected.
- [ ] Raw data stays in object storage.
- [ ] CI uses environment secrets only.

## Documentation

- [ ] Data dictionary and DBML are updated if the model changed.
- [ ] Canonical docs are updated if an interface or decision changed.
- [ ] `DECISIONS.md` is updated for a material decision.
- [ ] `PROGRESS.md` has status, evidence, blockers, and next step.
- [ ] Relative links resolve.

## Review

- [ ] Author ran the required checks and recorded results.
- [ ] Peer reviewer inspected the diff and evidence.
- [ ] Human approval is recorded for scope/gate/capacity changes.
