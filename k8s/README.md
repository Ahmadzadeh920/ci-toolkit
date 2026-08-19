# k8s/

Minimal example manifests consumed by
[`reusable-deploy-kubernetes.yml`](../.github/workflows/reusable-deploy-kubernetes.yml).

This is **not a real application** — `deployment.yaml` uses placeholder
values (`my-app`, `my-namespace`, `REGISTRY/IMAGE:TAG`). Replace them with
your own before using it, or better, keep your real manifests in your
application repository and just point the workflow at them.

## Files

| File | Purpose |
|---|---|
| `deployment.yaml` | Example Deployment + Service pair showing the manifest shape the workflow applies |
| `rbac.yaml` | Example `Role` / `RoleBinding` for the service account the self-hosted runner deploys as — a starting point, not something to apply as-is |

## Usage

```yaml
jobs:
  deploy:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-kubernetes.yml@v1
    with:
      runner: k3s
      application: my-app
      namespace: my-namespace
      manifest: k8s/deployment.yaml
      image-repository: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
    secrets:
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

The workflow runs `kubectl apply` against `manifest` and waits for rollout.
It assumes `kubectl` is already authenticated on the runner (default label:
`k3s`) — it does not accept a `kubeconfig` secret directly.

`rbac.yaml` is a separate, one-time setup step for whoever administers the
cluster — it is not applied by the workflow itself. Scope the `Role` to the
minimum verbs/resources your deployment actually needs before granting it.

See [`docs/reusable-workflows.md`](../docs/reusable-workflows.md) for the
full input/secret contract.
