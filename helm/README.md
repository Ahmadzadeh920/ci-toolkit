# helm/

Minimal example Helm chart skeleton consumed by
[`reusable-deploy-helm.yml`](../.github/workflows/reusable-deploy-helm.yml).

This is **not a real application chart** — `values.yaml` uses placeholder
values (`REGISTRY/IMAGE`, empty ingress host). Replace them with your own,
or keep your real chart in your application repository and just point the
workflow at it.

## Files

| File | Purpose |
|---|---|
| `Chart.yaml` | Minimal chart metadata |
| `values.yaml` | Default values — image, service, and disabled ingress by default |
| `templates/deployment.yaml` | Example templated Deployment referencing `.Values.image.*` and `.Values.service.*` |

## Usage

```yaml
jobs:
  deploy:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-helm.yml@v1
    with:
      runner: k3s
      application: my-app
      namespace: my-namespace
      helm-chart: helm/
      values-file: helm/values.yaml
      image-repository: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
      atomic: true
    secrets:
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

The workflow runs `helm upgrade --install` against `helm-chart`, with
optional automatic rollback via `atomic: true` if the rollout fails. It
assumes `helm`/`kubectl` are already authenticated on the runner (default
label: `k3s`).

See [`docs/reusable-workflows.md`](../docs/reusable-workflows.md) for the
full input/secret contract.
