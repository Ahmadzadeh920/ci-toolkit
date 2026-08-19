# Reusing These Workflows in Another Repository

Use this checklist when adopting this reusable CI/CD library in another
repository.

- [ ] Confirm the repository can access `ci-toolkit`.
- [ ] Pin every `uses:` reference to a release tag (`@v1`), never `@main`.
- [ ] Identify which reusable workflows you actually need — not every
      caller needs all 11.
- [ ] Configure all required `workflow_call` inputs (see
      [`docs/reusable-workflows.md`](reusable-workflows.md)).
- [ ] Create only the secrets required by the workflows you're calling
      (see [`docs/secrets.md`](secrets.md)).
- [ ] Create non-sensitive configuration as repository/environment
      variables (see [`docs/variables.md`](variables.md)).
- [ ] Create `development`, `staging`, and/or `production` environments as
      needed (see [`docs/environments.md`](environments.md)).
- [ ] Add environment-specific secrets for deployment.
- [ ] Pick exactly one deployment workflow — `reusable-deploy-docker-compose.yml`,
      `reusable-deploy-kubernetes.yml`, or `reusable-deploy-helm.yml`. There
      is no generic dispatcher; wire the one matching your infrastructure.
- [ ] Configure the correct self-hosted runner label for k3s deployments
      (`K8S_RUNNER`, default `k3s`).
- [ ] Configure GitHub Actions permissions required by each workflow (see
      [`docs/permissions.md`](permissions.md)).
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

## Recommended future improvements

- [ ] Move `sonar-host-url` from secret to variable.
- [ ] Add explicit `permissions:` blocks to all three deployment workflows.
- [ ] Confirm whether `DEPLOY_KEY` is needed in `reusable-sonarqube.yml`,
      `reusable-deploy-kubernetes.yml`, and `reusable-deploy-helm.yml`, or
      whether the ambient `GITHUB_TOKEN` covers checkout in same-repo cases.
- [ ] Consider GitHub App authentication for `reusable-sync.yml` instead of
      a long-lived PAT.
- [ ] Remove any debug steps that expose token lengths/prefixes.
- [ ] Avoid `StrictHostKeyChecking=no` in the Compose deploy workflow; use
      managed SSH known-hosts where possible.
