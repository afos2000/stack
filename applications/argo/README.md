# argo

Deploys **Argo Workflows** with a PostgreSQL database (for workflow persistence) and **MinIO** (for artifact storage).

## Dependencies
- **longhorn-system** — MinIO and PostgreSQL PVCs
- **postgres-operator** — alternative: this chart bundles its own PostgreSQL via Bitnami

## Key config
| Component | Version | Notes |
|-----------|---------|-------|
| argo-workflows | 0.45.27 | Workflow engine |
| postgresql (Bitnami) | 18.1.1 | Workflow persistence |
| minio (Bitnami) | 17.0.21 | Artifact repository (S3-compatible) |

### MinIO
- Root user: `andres` / `andresRules`
- Default bucket: `argo-storage`
- Console (browser) at MinIO pod port 9001

### PostgreSQL
- User: `andres`, password: `andresRules`
- Database: `postgres`

## Artifact repository config
The commented blocks in `values.yaml` show how to configure Argo Workflows to use MinIO as its artifact repository — uncomment and adjust if needed.

## Operations
```bash
# Submit a workflow
argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/main/examples/hello-world.yaml

# Access UI
kubectl port-forward -n argo svc/argo-workflows-server 2746:2746
```

## Connected apps
- **cloudflared** — may expose the workflows UI if configured
