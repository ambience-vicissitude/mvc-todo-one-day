#!/usr/bin/env bash
# Creates a Kind cluster, builds and loads the images, and deploys the app.
# Manual on purpose (not part of CI). Requires: docker, kind, kubectl.
set -euo pipefail

CLUSTER=taskapp
cd "$(dirname "$0")/.."

for tool in docker kind kubectl; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 1; }
done

if ! kind get clusters | grep -qx "$CLUSTER"; then
  kind create cluster --name "$CLUSTER" --config k8s/kind/kind-config.yaml
fi
kubectl config use-context "kind-$CLUSTER"

echo "Building and loading images"
docker build -t task-backend:local backend
docker build -t task-frontend:local frontend
kind load docker-image task-backend:local task-frontend:local --name "$CLUSTER"

echo "Installing ingress-nginx (Kind flavour) and metrics-server (for the HPA)"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/kind/deploy.yaml
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.7.2/components.yaml
# Kind's kubelet uses a self-signed certificate; local clusters only.
kubectl patch deployment metrics-server -n kube-system --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
kubectl wait -n ingress-nginx --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller --timeout=180s

echo "Deploying the app"
kubectl delete job db-init -n taskapp --ignore-not-found
kubectl apply -f k8s/
kubectl wait -n taskapp --for=condition=complete job/db-init --timeout=180s
kubectl rollout restart deployment/backend deployment/frontend -n taskapp
kubectl rollout status deployment/backend -n taskapp --timeout=180s
kubectl rollout status deployment/frontend -n taskapp --timeout=180s

echo "Ready: http://localhost:8081  (smoke test: bash scripts/integration-test.sh http://localhost:8081)"
