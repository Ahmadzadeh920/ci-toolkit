# Branching Strategies

Every repo that deploys through `ci-toolkit`'s reusable workflows picks one
`branching-strategy` value. That single choice determines which branches or
tags deploy where, via the shared `reusable-branch-context.yml` job. The
Kubernetes deploy workflow (`reusable-deploy-kubernetes.yml`) never
re-implements this logic itself — it just reads
`needs.resolve-context.outputs.environment` and consumes it directly as the
target **namespace**, gated on `should-deploy`.

> This page assumes Kubernetes as the deployment target. `environment` maps
> 1:1 to a Kubernetes namespace (`dev`, `staging`, `prod`). Other deployment
> targets (Docker Compose, Helm) consume the same `resolve-context` outputs
> but are out of scope here — see their own reusable workflows for how they
> interpret `environment`.

```yaml
jobs:
  resolve-context:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-branch-context.yml@v1
    with:
      branching-strategy: git-flow   # trunk | github-flow | git-flow
  deploy:
    needs: resolve-context
    if: needs.resolve-context.outputs.should-deploy == 'true'
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-kubernetes.yml@v1
    with:
      namespace: ${{ needs.resolve-context.outputs.environment }}
```

## `trunk` — trunk-based development

One long-lived branch. No `develop`, no `release/*`. Every merge to `main`
ships.

| Ref                          | Environment | Deploys? |
|-------------------------------|:-----------:|:--------:|
| `main` (push)                  | `prod`      | ✅ |
| any other branch               | –           | ❌ |
| tags                            | –           | ❌ (informational only) |

Pick this when you want continuous deployment and are comfortable with
feature flags / short-lived branches instead of release branches.

## `github-flow` — main is always deployable

Feature branches merge into `main` via PR; `main` is always production-ready.
Tags exist only to mark/promote a specific commit that's already on `main`.

| Ref                                  | Environment | Deploys? |
|----------------------------------------|:-----------:|:--------:|
| `main` (push)                          | `prod`      | ✅ |
| semver tag (`v1.2.3`) on `main`         | `prod`      | ✅ |
| feature branches                       | –           | ❌ |

Pick this for small teams shipping continuously with lightweight review, no
staging environment needed.

## `git-flow` — develop / release / main with a staging gate

Long-lived `develop` and `main`, plus short-lived `release/*` branches.
Merging to `main` alone does **not** deploy — only cutting a semver tag
promotes to production. This mirrors how this repo's existing
`release.yml` already only reacts to full semver tags (`v[0-9]+.[0-9]+.[0-9]+`)
and deliberately ignores floating major tags like `v1`.

| Ref                                  | Environment | Deploys? |
|----------------------------------------|:-----------:|:--------:|
| `develop` (push)                       | `staging`   | ✅ |
| `release/*` (push)                     | `staging`   | ✅ |
| `main` (push)                          | `prod`      | ❌ (waits for tag) |
| semver tag (`v1.2.3`)                   | `prod`      | ✅ |
| feature branches                       | –           | ❌ |

Pick this when you need a real staging environment and a deliberate,
tag-gated production release step (e.g. compliance sign-off, manual QA on a
release branch before it ships).

## Adding a new strategy

If none of the three fit, add a new `case` branch inside
`reusable-branch-context.yml`'s resolver script and a matching section here.
Don't add strategy-specific `if:` conditions to individual deploy workflows —
that defeats the point of centralizing this logic.

## Namespace naming convention

Since `environment` feeds `reusable-deploy-kubernetes.yml` directly as the
`namespace` input, keep namespace names identical to the environment values
above (`dev`, `staging`, `prod`) — don't prefix or suffix them per repo. If a
repo needs isolation (e.g. multiple services per environment), namespace it
as `<environment>-<service>` (e.g. `prod-auth-gateway`) in the caller
workflow, not by changing what `resolve-context` outputs.
