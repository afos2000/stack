# reflector

Deploys **Reflector 9.1.37** — mirrors Secrets and ConfigMaps across namespaces.

## Dependencies
None.

## How it works
Annotate a source Secret/ConfigMap with:
```yaml
metadata:
  annotations:
    reflector.v1.k8s.emberstack.com/reflected: "true"
    reflector.v1.k8s.emberstack.com/reflected-version: "latest"
```

Then annotate the target with:
```yaml
metadata:
  annotations:
    reflector.v1.k8s.emberstack.com/reflects: "source-ns/source-name"
```

Reflector copies the source into the target namespace.

## Usage in this stack
- **keycloak** → reads DB creds from `postgres/keycloak-db-app` reflected into `keycloak/keycloak-db-keycloak`
