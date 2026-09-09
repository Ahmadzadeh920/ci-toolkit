# Reusing These Workflows in Another Repository

Use this checklist when adopting this reusable CI/CD library in another
repository.

- [ ] Confirm the repository can access `ci-toolkit`.
- [ ] Pin every `uses:` reference to a release tag (`@v1`), never `@main`.
- [ ] Choose a branching strategy — `trunk`, `github-flow`, or `git-flow` —
      before wiring any deploy/release job. See
      [`docs/branching-strategies.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/branching-strategies.md)
      for the full ref-to-environment mapping of each.
- [ ] Add a `resolve-context` job calling `reusable-branch-context.yml@v1`
      with your chosen `branching-strategy`, and `main-branch`/
      `develop-branch` overrides if your branch names differ from the
      `main`/`develop` defaults.
- [ ] Identify which reusable workflows you actually need — not every
      caller needs all 12.
- [ ] Configure all required `workflow_call` inputs (see
      [`docs/reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md)).
- [ ] Create only the secrets required by the workflows you're calling
      (see [`docs/secrets.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/secrets.md)).
- [ ] Create non-sensitive configuration as repository/environment
      variables (see [`docs/variables.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/variables.md)).
- [ ] Create `development`, `staging`, and/or `production` environments as
      needed (see [`docs/environments.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/environments.md)).
- [ ] Add environment-specific secrets for deployment.
- [ ] Pick exactly one deployment workflow — `reusable-deploy-docker-compose.yml`,
      `reusable-deploy-kubernetes.yml`, or `reusable-deploy-helm.yml`. There
      is no generic dispatcher; wire the one matching your infrastructure.
- [ ] Write your own manifest/chart/compose file using the shape in
      [`examples/`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/examples) — do not expect one to be provided by
      this repo.
- [ ] Wire every deploy/release job's `needs:` to include `resolve-context`
      **and** every required quality/security gate job (test, CodeQL,
      SonarQube, Trivy, etc.) — not just `resolve-context` alone.
- [ ] If a deploy/release job defines its own `if:` condition, explicitly
      add `needs.<job>.result == 'success'` checks for every job in its
      `needs:` list. Assigning a custom `if:` replaces GitHub Actions'
      implicit "only run if all `needs:` succeeded" behavior — it does not
      combine with it. This is a common source of gates silently not
      blocking deploys.
- [ ] If more than a couple of quality/security gates apply, consider a
      single aggregator job (e.g. `quality-gate`) that depends on all of
      them and checks their results with `if: always()`, so deploy jobs
      only ever need `needs: [resolve-context, quality-gate]` and don't
      need editing every time a gate is added or removed.
- [ ] Configure the correct self-hosted runner label for k3s deployments
      (`K8S_RUNNER`, default `k3s`).
- [ ] Configure GitHub Actions permissions required by each workflow (see
      [`docs/permissions.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/permissions.md)).
- [ ] Verify CodeQL has `security-events: write`.
- [ ] Verify Trivy SARIF upload has `security-events: write`.
- [ ] Verify GHCR publishing has `packages: write`.
- [ ] Verify SonarQube URL and token.
- [ ] Verify Docker registry credentials.
- [ ] Verify `DEPLOY_KEY` is actually required for your Kubernetes/Helm
      manifest location before adding it (see `docs/secrets.md` §2).
- [ ] Verify SSH credentials if Docker Compose deployment is used.
- [ ] Verify notification webhook only if notifications are enabled.
- [ ] Verify repository-sync token only if `reusable-sync.yml` is used.
- [ ] Never copy actual secret values into Git.
- [ ] Rotate credentials if their origin or exposure history is uncertain.
- [ ] Test each branching-strategy ref case (feature branch, `develop`,
      `release/*`, `main`, and a semver tag, as applicable to your chosen
      strategy) in a non-production environment first, confirming
      `resolve-context` resolves `environment`/`should-deploy` as expected
      for each.
- [ ] Promote the tested workflow version to production.

## Recommended future improvements

- [ ] Move `sonar-host-url` from secret to variable.
- [ ] Add explicit `permissions:` blocks to all three deployment workflows.
- [ ] Confirm whether `DEPLOY_KEY` is needed in `reusable-sonarqube.yml`,
      `reusable-deploy-kubernetes.yml`, and `reusable-deploy-helm.yml`, or
      whether the ambient `GITHUB_TOKEN` covers checkout in same-repo cases.
- [ ] Replace long-lived cloud registry credentials with OIDC where the
      registry is cloud-hosted (see [`docs/oidc.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/oidc.md)).
- [ ] Consider GitHub App authentication for `reusable-sync.yml` instead of
      a long-lived PAT.
- [ ] Remove any debug steps that expose token lengths/prefixes.
- [ ] Avoid `StrictHostKeyChecking=no` in the Compose deploy workflow; use
      managed SSH known-hosts where possible.
- [ ] Consider adding a fourth `branching-strategy` value if a repository's
      promotion model doesn't fit `trunk`/`github-flow`/`git-flow` cleanly,
      rather than layering ad hoc `if:` conditions on top of
      `resolve-context`'s outputs in the caller workflow.
