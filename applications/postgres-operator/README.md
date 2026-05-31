# postgres-operator

Deploys **CloudNative PG Operator 0.28.2** (CNPG) — manages PostgreSQL clusters via the `Cluster` CRD.

## Dependencies
- **longhorn-system** — PVCs for database storage

## Key config
- `crds.create: true` — installs the `Cluster` CRD
- Lightweight resource profile (100m/128Mi requests)

## How it works
The operator installs the `postgresql.cnpg.io/v1` API. To create a database, submit a `Cluster` resource (see `postgres/`). The operator provisions pods, handles replication, backups, and auto-generates secrets for database users.

## Connected apps
- **postgres** — the actual `Cluster` resource managed by this operator
