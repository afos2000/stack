# Stack Guide

End-to-end documentation for this GitOps Kubernetes stack.

## Architecture

```
Cloudflare (TLS termination)
    │
    ▼
cloudflared ───► ClusterIP services
    │
    ├── keycloak.andreskube.uk ──► keycloak
    └── argocd.andreskube.uk  ──► argocd (root)
                           
Internal services (no ingress):
    ├── vault ──► external-secrets ──► all apps
    ├── longhorn-system (distributed storage)
    └── metallb (load balancer IP pool)
```

## Dependency chain

Each app depends on the ones below it:

```
Level 0 (Infrastructure)
├── longhorn-system          ─ Distributed block storage (default SC)
├── metallb (k8s-objects)    ─ Load balancer IP pool (192.168.0.240-250)
└── cert-manager (root)      ─ TLS certificates

Level 1 (Platform)
├── postgres-operator        ─ CNPG operator for PostgreSQL clusters
├── vault                    ─ Secrets backend (KV v2)
└── reflector                ─ Cross-namespace secret mirroring

Level 2 (Services)
├── postgres/keycloak-db     ─ PostgreSQL database for Keycloak
├── external-secrets         ─ Syncs Vault secrets into K8s Secrets
└── reloader                 ─ Auto-restarts on config changes

Level 3 (Applications)
├── keycloak                 ─ SSO/OIDC provider (for ArgoCD)
├── argo (workflows)         ─ CI/CD workflow engine
└── cloudflared              ─ Cloudflare Tunnel (ingress)

Level 4 (User-facing)
└── argocd (root)            ─ GitOps CD (managed separately)
```

## Bootstrapping order

1. **Pre-reqs** — ArgoCD CRDs + cert-manager CRDs (see `INSTALL.md`)
2. **Deploy ArgoCD** — `argocd/` directory, then create the ApplicationSet
3. **Longhorn** — storage for everything else
4. **Vault** — initialize, unseal, configure KV + K8s auth (see `applications/vault/README.md`)
5. **Postgres operator** + **postgres** — database for Keycloak
6. **External secrets** — ClusterSecretStore pointing to Vault
7. **Cloudflared** — tunnel token in Vault, then routes traffic
8. **Keycloak** — admin password in Vault, DB creds via reflector
9. **Reflector** — mirrors `postgres/keycloak-db-app` → `keycloak/keycloak-db-keycloak`
10. **Reloader**, **Argo Workflows**, **Docker registry** — remaining services

## Secrets management

```
Vault (KV v2, mount: secrets/)
├── dockerhub ─────────────────── user + password
├── keycloak ──────────────────── admin-pw
├── cloudflare-tunnel ─────────── token
└── test-hello ────────────────── message
        │
        ▼
ExternalSecret (CRD)
        │
        ▼
Kubernetes Secret (in target namespace)
        │
        ▼
Pod (env var or volume mount)
```

All secrets flow from Vault → External Secrets Operator → K8s Secrets → pods.
No plaintext secrets in git (gitignore blocks `*secret.yaml`).

## Network

| Component | Type | Address |
|-----------|------|---------|
| ArgoCD (root) | LoadBalancer | 192.168.0.x (MetalLB) |
| Keycloak | ClusterIP (via cloudflared) | keycloak.andreskube.uk |
| Vault | ClusterIP | vault.vault:8200 |
| Longhorn UI | ClusterIP | (port-forward) |

## Storage

| App | Size | StorageClass | Purpose |
|-----|------|-------------|---------|
| vault | 10Gi | longhorn | Raft data |
| keycloak-db | 10Gi | longhorn | PostgreSQL data |
| minio (argo) | (default) | longhorn | Workflow artifacts |

## Adding a new app

1. Create `applications/<name>/Chart.yaml` (with upstream dependency) or raw manifests
2. Create `applications/<name>/values.yaml`
3. If the app needs credentials, create an ExternalSecret or store in Vault
4. If the app needs ingress, configure a public hostname in Cloudflare Tunnel dashboard
5. Commit → ArgoCD picks it up via ApplicationSet

## Next: Backstage

Planned: Deploy Backstage as the Internal Developer Portal (IDP),
providing a developer-facing UI over this infrastructure.
