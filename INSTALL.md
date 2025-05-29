for argocd is needed to install manually the crds:

kubectl apply -k https://github.com/argoproj/argo-cd/manifests/crds\?ref\=stable

for cert-manager:

kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v1.12.0/cert-manager.crds.yaml
