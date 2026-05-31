# external-secrets

Deploys **External Secrets Operator 2.4.1** — syncs secrets from Vault into Kubernetes Secrets.

## Dependencies
- **vault** — upstream secrets backend (ClusterSecretStore targets `http://vault.vault:8200`)

## Key config
- `installCRDs: true` — brings in CRDs for ExternalSecret, ClusterSecretStore, etc.
- Auth: Kubernetes service account `external-secrets` → Vault role `eso`

## How it works
1. `ClusterSecretStore` named `vault-store` is created pointing to Vault
2. Any app can create an `ExternalSecret` referencing `vault-store`
3. ESO reads from Vault and writes the result as a standard Kubernetes Secret

## Adding a new secret
Create an ExternalSecret in the target app's `templates/`:
```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: my-secret
spec:
  secretStoreRef:
    name: vault-store
    kind: ClusterSecretStore
  target:
    name: my-secret
  data:
    - secretKey: MY_KEY
      remoteRef:
        key: secrets/data/my-path
        property: my-property
```

## Connected apps
All apps that fetch credentials from Vault use this operator.
