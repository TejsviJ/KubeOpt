# Kubeopt

Kubeopt is a Kubernetes resource optimization project. It combines a Python optimizer and API with Kubernetes workload and access-control manifests, and includes configuration for local development with kind.

> Project status: experimental. Review manifests and resource recommendations for your environment before applying them to a cluster.

## What it includes

- `optimizer/` — metrics collection, analysis, and recommendation components.
- `app/api/` — API service.
- `kubernetes/`, `*.yaml` — workload, autoscaling, RBAC, and local cluster manifests.
- `Dockerfile.optimizer` — container build definition for the optimizer.
- `requirements.txt` — Python dependencies.

CAST AI integration: document the integration path, supported features, and configuration here as they are implemented. Do not commit API keys; provide them through your secret manager or local environment.

## Prerequisites

- Python 3
- Docker
- Kubernetes CLI (`kubectl`)
- [kind](https://kind.sigs.k8s.io/) for a local Kubernetes cluster

## Getting started

1. Clone this repository and create a virtual environment:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Review the manifests and configure any required image names, namespaces, and environment values.
3. Create or select a Kubernetes cluster, then apply only the manifests needed for your setup:

   ```sh
   kubectl apply -f kubernetes/
   ```

   Apply individual root-level YAML files separately when needed; the correct order depends on the cluster setup.

## Configuration and secrets

Keep kubeconfigs, AWS credentials, CAST AI tokens, `.env` files, private keys, and cluster-specific settings out of Git. Use Kubernetes Secrets or an external secret manager for runtime credentials. Commit a sanitized `.env.example` only if the application needs one.

## Development

Describe the optimizer and API run commands, expected metrics input, recommendation output, and local kind workflow here. Add tests and CI instructions as those workflows are established.

## Security

Do not apply these manifests to production without reviewing permissions, resource limits, images, and secret handling. Report vulnerabilities privately to the repository maintainers.

## License

Add the license and attribution that apply to the Kubeopt project. The separately maintained upstream autoscaler source is excluded from this repository; consult its own license and repository for that code.
