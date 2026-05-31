# postgres

Defines the **CloudNative PG Cluster** for **Keycloak's database**.

## Dependencies
- **postgres-operator** — provides the `Cluster` CRD
- **longhorn-system** — 10Gi PVC for PostgreSQL data

## Key config
- **Cluster name**: `keycloak-db`
- **Instance count**: 1
- **Storage**: 10Gi on Longhorn
- **Database**: `keycloak`, Owner: `keycloak`
- **Resources**: requests 250m/512Mi, limits 1CPU/1Gi

## Credentials
CNPG auto-generates a secret `<cluster-name>-app` (i.e. `keycloak-db-app`) in the `postgres` namespace with:
- `username`: `keycloak`
- `password`: (auto-generated)
- `dbname`: `keycloak`

Keycloak accesses these via **Reflector** — the secret is reflected into the `keycloak` namespace as `keycloak-db-keycloak`.

## Connected apps
- **keycloak** — connects as `keycloak-db-rw.postgres.svc:5432` with username `keycloak`

## Operations
```bash
# Get auto-generated password
kubectl get secret keycloak-db-app -n postgres -o jsonpath='{.data.password}' | base64 -d
```
