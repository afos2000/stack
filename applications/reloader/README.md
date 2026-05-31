# reloader

Deploys **Reloader 2.2.3** — triggers rolling restarts when ConfigMaps/Secrets change.

## Dependencies
None.

## How it works
Annotate a Deployment with:
```yaml
metadata:
  annotations:
    reloader.stakater.com/match: "true"
```

Or reference secrets directly — Reloader watches all resources in the cluster and restarts Deployments that reference changed Secrets/ConfigMaps.

## Usage in this stack
Useful for any app that reads config from ConfigMaps or credentials from Secrets — Reloader ensures pods pick up changes automatically without manual restarts.
