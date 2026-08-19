# ci-toolkit

A versioned, portable library of **13 reusable GitHub Actions workflows** covering
test/lint, static analysis, security scanning, Docker build/push, deployment
(Docker Compose, Kubernetes, Helm), notifications, and repo sync — extracted
from [`auth-gateway-platform`](https://github.com/Ahmadzadeh920/auth-gateway-platform)
so any repository can call them via `workflow_call` instead of duplicating CI/CD logic.

> Application code and secrets stay in each caller repository. This repo only
> ships the pipeline contracts.

## Why this exists

Copy-pasted CI/CD YAML rots differently in every repo it's pasted into. This
toolkit centralizes the pipeline logic once, exposes it through explicit
`inputs` / `secrets` / `outputs` contracts, and lets every consuming
repository pin to a stable release tag (e.g. `@v1`) instead of duplicating or
re-inventing the workflow.

## Use cases

- **Multi-repo standardization** — enforce the same test, lint, CodeQL, and
  Trivy scanning process across every service without maintaining N copies.
- **Polyglot CI** — `reusable-test.yml` supports configurable dependency
  managers and test/lint commands, so it isn't locked to one language.
- **Container pipelines** — build, scan, and push Docker images to any
  OCI registry (defaults to `ghcr.io`) with a consistent tag/digest contract.
- **Multi-target deployment** — deploy the same artifact to Docker Compose
  (SSH), Kubernetes (kubectl), or Helm from one dispatcher workflow.
- **Release notifications** — post pipeline status to Slack, Microsoft Teams,
  or Discord from a single reusable step.
- **Repo mirroring/sync** — push a branch to a downstream/target repository
  (e.g. mirroring, GitOps promotion) via `reusable-sync.yml`.

## Applications

Any GitHub-hosted repository that wants CI/CD without owning pipeline logic:
microservices, internal tools, Kubernetes-deployed apps, Compose-deployed
apps on a VM, or repositories that just need consistent security scanning
(CodeQL/Trivy) and SonarQube quality gates.

## ⚠️ Critical structural constraint

GitHub **only** resolves reusable workflows referenced via
`uses: org/repo/.github/workflows/file.yml@ref` when the file physically
lives at `.github/workflows/` in the **source** repo, exactly like the
caller repo. Do not move the workflow files into a top-level `workflows/`
folder — they must stay under `.github/workflows/` here too, or callers
can't reference them.

## Repository structure

```text
ci-toolkit/
├── .github/
│   └── workflows/
│       ├── reusable-test.yml
│       ├── reusable-codeql.yml
│       ├── reusable-sonarqube.yml
│       ├── reusable-docker.yml
│       ├── reusable-docker-build.yml
│       ├── reusable-docker-push.yml
│       ├── reusable-trivy.yml
│       ├── reusable-notification.yml
│       ├── reusable-deploy.yml
│       ├── reusable-deploy-docker-compose.yml
│       ├── reusable-deploy-kubernetes.yml
│       ├── reusable-deploy-helm.yml
│       ├── reusable-sync.yml
│       └── self-lint.yml          # NEW: lints/validates this repo's own workflows on PR
├── docs/
│   ├── README.md                  # documentation model & versioning policy
│   ├── reusable-workflows.md      # full contract per workflow (inputs/secrets/outputs)
│   ├── permissions.md             # minimum GITHUB_TOKEN permissions per workflow
│   ├── secrets.md                 # secret name → purpose inventory (no values)
│   ├── variables.md               # non-sensitive `vars.*` inventory
│   ├── environments.md            # GitHub Environments setup (dev/staging/prod)
│   ├── oidc.md                    # OIDC adoption strategy & what it does/doesn't replace
│   └── migration-checklist.md     # checklist for onboarding a new caller repo
├── examples/
│   └── caller-ci.yml              # a full example pipeline calling this toolkit
├── README.md                      # this file
├── CHANGELOG.md
└── LICENSE
```

## Quick start

In a consuming repository, reference workflows by tag (never `@main` in
production — see [Versioning](#versioning)):

```yaml
# .github/workflows/ci.yml (in your application repo)
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    uses: your-org/ci-toolkit/.github/workflows/reusable-test.yml@v1
    with:
      python-versions: '["3.11", "3.12"]'
      working-directory: services/api

  codeql:
    uses: your-org/ci-toolkit/.github/workflows/reusable-codeql.yml@v1
    permissions:
      actions: read
      contents: read
      security-events: write

  docker-build:
    needs: test
    uses: your-org/ci-toolkit/.github/workflows/reusable-docker-build.yml@v1
    with:
      image-name: my-service
      registry-username: ${{ github.repository_owner }}
    secrets:
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

See `examples/caller-ci.yml` for a complete pipeline wiring together test →
CodeQL → SonarQube → Docker build → Trivy scan → Docker push → deploy →
notify, adapted from the original `ci.yml`.

## Workflow catalog

| Workflow | Purpose | Secrets required | Docs |
|---|---|---|---|
| `reusable-test.yml` | Install deps, lint, test, coverage, upload artifact | None | [reusable-workflows.md](docs/reusable-workflows.md#reusable-testyml) |
| `reusable-codeql.yml` | CodeQL static analysis | None | [reusable-workflows.md](docs/reusable-workflows.md#reusable-codeqlyml) |
| `reusable-sonarqube.yml` | SonarQube scan + quality gate | `sonar-token`, `sonar-host-url`, `DEPLOY_KEY` | [reusable-workflows.md](docs/reusable-workflows.md#reusable-sonarqubeyml) |
| `reusable-docker-build.yml` | Build image, optionally push/save artifact | `registry-password` | [reusable-workflows.md](docs/reusable-workflows.md#reusable-docker-buildyml) |
| `reusable-docker-push.yml` | Load a saved image artifact and push it | `registry-password` | [reusable-workflows.md](docs/reusable-workflows.md#reusable-docker-pushyml) |
| `reusable-docker.yml` | Combined build + push in one workflow | `registry-password` | [reusable-workflows.md](docs/reusable-workflows.md) |
| `reusable-trivy.yml` | Filesystem/image/config/SBOM vulnerability scan | None | [reusable-workflows.md](docs/reusable-workflows.md#reusable-trivyyml) |
| `reusable-notification.yml` | Slack / Teams / Discord pipeline notifications | `slack-webhook`, `teams-webhook`, `discord-webhook` (as used) | [reusable-workflows.md](docs/reusable-workflows.md#reusable-notificationyml) |
| `reusable-deploy.yml` | Generic dispatcher: Compose / Kubernetes / Helm | `ssh-host`, `ssh-user`, `ssh-private-key`, `kubeconfig` (as used) | [reusable-workflows.md](docs/reusable-workflows.md#reusable-deployyml) |
| `reusable-deploy-docker-compose.yml` | Docker Compose deployment over SSH | `ssh-private-key` (typ.) | [reusable-workflows.md](docs/reusable-workflows.md#deployment-specific-workflows) |
| `reusable-deploy-kubernetes.yml` | `kubectl`-based Kubernetes deployment | `DEPLOY_KEY` | [reusable-workflows.md](docs/reusable-workflows.md#deployment-specific-workflows) |
| `reusable-deploy-helm.yml` | Helm chart deployment | Helm/kube credentials as configured | [reusable-workflows.md](docs/reusable-workflows.md#deployment-specific-workflows) |
| `reusable-sync.yml` | Push a branch to a target repository | `target-token` | [reusable-workflows.md](docs/reusable-workflows.md#reusable-syncyml) |

Full inputs, outputs, and default runner labels for every workflow are
documented per-workflow in [`docs/reusable-workflows.md`](docs/reusable-workflows.md).

## Configuration reference

| Topic | File | What it covers |
|---|---|---|
| Documentation model & versioning | [`docs/README.md`](docs/README.md) | How this documentation set is organized; tag-based versioning policy |
| Full workflow contracts | [`docs/reusable-workflows.md`](docs/reusable-workflows.md) | Inputs, secrets, permissions, and outputs per workflow |
| Required permissions | [`docs/permissions.md`](docs/permissions.md) | Minimum `GITHUB_TOKEN` permission set per workflow |
| Secrets inventory | [`docs/secrets.md`](docs/secrets.md) | Every secret name, which workflow needs it, and whether OIDC can replace it — **names only, never values** |
| Variables inventory | [`docs/variables.md`](docs/variables.md) | Non-sensitive `vars.*` configuration recommended per workflow |
| Environments | [`docs/environments.md`](docs/environments.md) | Recommended `development` / `staging` / `production` GitHub Environments and protection rules |
| OIDC strategy | [`docs/oidc.md`](docs/oidc.md) | What OIDC can and can't replace (SSH and SonarQube tokens are **not** replaceable by OIDC; cloud registries/Kubernetes are good candidates) |
| Migration checklist | [`docs/migration-checklist.md`](docs/migration-checklist.md) | Step-by-step checklist for onboarding a new caller repository |

## Versioning

Do not consume workflows from `main` in production. Tag releases:

```text
v1
v1.1.0
v1.2.0
```

and have caller repos reference a fixed tag:

```yaml
uses: your-org/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

Bump the major tag only on breaking contract changes (renamed/removed
inputs or secrets); patch/minor tags for additive, backward-compatible
changes.

## Security notes

- This repository **never** contains secret values, kubeconfigs, private
  keys, or webhook URLs — only secret *names* and their purpose
  (see [`docs/secrets.md`](docs/secrets.md)).
- Grant each workflow the minimum `permissions:` block documented in
  [`docs/permissions.md`](docs/permissions.md) — never `permissions: write-all`.
- Prefer the ambient `GITHUB_TOKEN` over long-lived PATs for GHCR wherever
  the workflow supports it.
- Kubernetes/Helm deployment workflows default to a self-hosted `k3s`
  runner label — override the `runner` input if your infrastructure differs.

## Migrating an existing repo onto this toolkit

Follow [`docs/migration-checklist.md`](docs/migration-checklist.md) end to
end. In short: pin to a release tag, wire only the `workflow_call` inputs
you need, create only the secrets your selected workflows require, and test
in a non-production environment before promoting.

## Contributing

Workflow contract changes (renaming/removing an input, secret, or output)
are breaking changes — bump the major version tag and note it in
`CHANGELOG.md`. Additive changes (new optional input with a default) can
ship as a minor/patch release.

## License

MIT (or your preferred license) — update before making the repo public.
