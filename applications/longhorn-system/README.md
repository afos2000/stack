# longhorn-system

Deploys **Longhorn 1.7.2** — distributed block storage, the default StorageClass for the cluster.

## Dependencies
None (operates on raw disks attached to nodes).

## Key config
- **Default data path**: `/var/lib/longhorn`
- **Replicas**: 2 per volume
- **Tolerations**: Runs on control-plane nodes (`node-role.kubernetes.io/control-plane:NoSchedule`)
- **Default StorageClass**: Longhorn is the default (no other SC marked default)

## Storage consumers
| App | Size | Purpose |
|-----|------|---------|
| vault | 10Gi | Raft storage |
| postgres (keycloak-db) | 10Gi | PostgreSQL data |
| docker-registry | 50Gi | Docker Hub pull-through cache |
| minio (argo) | (default) | Workflow artifacts |

## Operations
- UI accessible via Longhorn frontend Service
- Snapshots and backups can be configured via Longhorn UI or CRDs
- Volume expansion supported (increase PVC size, controller handles the rest)
