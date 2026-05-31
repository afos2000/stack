# Status: Deployed (track planned, chart ready)

## Current state
Step 1-7 all complete. The chart is in `applications/docker-registry/` and will be picked up by the ArgoCD ApplicationSet automatically.

## What was implemented
| Step | What | Files |
|------|------|-------|
| 1 | Chart wrapper | `Chart.yaml`, `values.yaml` |
| 2 | Proxy config (Docker Hub) | `templates/configmap.yaml` |
| 3 | Longhorn PVC (50Gi) | `templates/pvc.yaml` |
| 4 | GC CronJob (weekly) | `templates/gc-cronjob.yaml` |
| 5 | Ingress (disabled, template ready) | `templates/ingress.yaml` |
| 6 | Containerd mirror docs | `CONTAINERD_MIRROR.md` |
| 7 | Verification | `helm template` validated |

## Containerd Mirror
Configure each node (manual step, documented in CONTAINERD_MIRROR.md):
```toml
[plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
  endpoint = ["http://docker-registry.docker-registry.svc.cluster.local:5000"]
```
