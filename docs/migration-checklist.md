# Reusing These Workflows in Another Repository

Use this checklist when adopting this reusable CI/CD library in another
repository.

- [ ] Confirm the repository can access `ci-toolkit`.
- [ ] **Never reference a workflow from `ci-toolkit` using `@main` in any
production example, config, or workflow file.** Pin every `uses:`
reference to a release tag instead: `@v1` for a tracked, non-breaking-only
major version, or `@v1.2.3` for a fixed, immutable snapshot. `main` is
unpinned and can change, including breaking, at any time — this applies
to every `uses:` line you write, not just the first one you copy from a
README example.
- [ ] Identify which reusable workflows you actually need — not every
caller needs all 11.
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
- [ ] Test the workflow in a non-production environment first.
- [ ] Promote the tested workflow version to production.

## Why pinning to `@main` is forbidden, not just discouraged

`ci-toolkit` cannot guarantee anything about the state of `main` at the
moment your workflow happens to run — a commit that changes an input
name, removes a secret, or alters deployment behavior could land there
between your last successful run and your next one, with no version bump
to warn you.

Two things now make pinned tags a real guarantee rather than a
convention:

- **Contract-breaking changes are blocked in CI.** Every pull request
against `ci-toolkit` is checked by an automated contract-diff against
the last released tag — a removed or renamed input/secret/output fails
the PR unless it's explicitly labeled as a breaking change. That
guarantee only protects you if you're consuming a tagged release; it
says nothing about `main`, which has no such check gating direct
commits.
- **Release tags are immutable.** Full semver tags (`v1.0.0`, `v1.2.3`,
…) are protected against force-push and deletion once published — once
you've pinned to one, what you get from it cannot change under you. The
floating major alias (`v1`, `v2`, …) is the one exception: it's
deliberately designed to move forward to the latest compatible patch,
which is what makes `@v1` convenient to pin instead of a full version.

If you see `@main` anywhere in this repository's documentation or
examples, that is a documentation bug — open an issue rather than
copying it.

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
