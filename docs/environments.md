# GitHub Actions Environments

GitHub Actions Environments provide a way to separate deployment configuration and protect environment-specific secrets.

`ci-toolkit` supports using GitHub Environments for repositories that have multiple deployment stages such as:

```text
development
     ↓
staging
     ↓
production
```

The toolkit does not require every repository to use all three environments.

A repository should create only the environments it actually needs.

---

## Why use environments?

Deployment configuration often differs between environments.

For example:

| Environment | Purpose | Typical deployment |
|---|---|---|
| `development` | Developer testing | Development infrastructure |
| `staging` | Pre-production validation | Staging infrastructure |
| `production` | Live application | Production infrastructure |

GitHub Environments allow repositories to keep environment-specific configuration separate.

---

# Recommended environment structure

For a repository with multiple deployment stages:

```text
GitHub repository
│
├── development
│   ├── variables
│   └── secrets
│
├── staging
│   ├── variables
│   └── secrets
│
└── production
    ├── variables
    └── secrets
```

The exact environment names are a repository-level decision, but using consistent names makes CI/CD easier to understand.

---

# Environment-specific secrets

Deployment credentials should normally be stored as environment secrets when they differ between environments.

For example:

```text
development
    SSH_HOST
    SSH_USER
    SSH_PRIVATE_KEY

staging
    SSH_HOST
    SSH_USER
    SSH_PRIVATE_KEY

production
    SSH_HOST
    SSH_USER
    SSH_PRIVATE_KEY
```

The values can be different for every environment.

Never commit these values to Git.

---

# Environment-specific variables

Non-sensitive configuration can be stored as environment variables.

Examples include:

```text
DEPLOYMENT_NAMESPACE
REMOTE_DIRECTORY
COMPOSE_SERVICE
IMAGE_REPOSITORY
```

Sensitive values must remain secrets.

Do not use repository variables for passwords, private keys, tokens, or other credentials.

---

# Using an environment from a caller workflow

A consuming repository can associate a deployment job with an environment:

```yaml
jobs:
  deploy:
    environment:
      name: production

    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-kubernetes.yml@v1

    with:
      runner: k3s
      application: my-app
      namespace: production
      manifest: k8s/
      image-repository: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
```

The environment belongs to the **consuming repository**, not to `ci-toolkit`.

---

# Production protection

Production deployments should be protected when the project requires approval.

GitHub Environments can be configured with protection rules such as:

- required reviewers
- deployment restrictions
- environment-specific secrets
- environment-specific variables

A typical production flow is:

```text
Build
  |
  v
Test
  |
  v
Security Scan
  |
  v
Staging
  |
  v
Production approval
  |
  v
Production deployment
```

This helps prevent an automatically triggered workflow from immediately deploying an unreviewed change to production.

---

# Deployment strategy and environments

Environments are independent of the deployment mechanism.

A repository can use environments with any of the three supported deployment strategies:

### Docker Compose

```text
development → Docker Compose
staging     → Docker Compose
production  → Docker Compose
```

### Kubernetes / k3s

```text
development → Kubernetes
staging     → Kubernetes
production  → Kubernetes
```

### Helm

```text
development → Helm
staging     → Helm
production  → Helm
```

The repository should still select its primary deployment strategy rather than configuring all three for the same deployment pipeline.

---

# Environment naming

Recommended names are:

```text
development
staging
production
```

If the repository has different requirements, names such as:

```text
dev
test
stage
prod
```

can be used, but consistency across repositories is preferable.

---

# Important security rules

1. Never commit environment secrets.
2. Do not place production credentials in development environments.
3. Use separate credentials for different environments where possible.
4. Protect production deployments with appropriate approval rules.
5. Use least-privilege credentials.
6. Do not hard-code environment-specific infrastructure addresses in reusable workflows.
7. Keep environment configuration in the consuming repository.
8. Do not put environment-specific secrets inside `ci-toolkit`.

---

# Relationship with ci-toolkit

`ci-toolkit` provides the reusable workflow implementation.

The consuming repository provides:

```text
Workflow inputs
        +
Secrets
        +
Variables
        +
Environment
        +
Application deployment configuration
```

For example:

```text
auth-gateway-platform
│
├── GitHub Environment: production
│
├── Secrets
│   ├── SSH_HOST
│   ├── SSH_USER
│   └── SSH_PRIVATE_KEY
│
├── Variables
│   └── deployment configuration
│
└── .github/workflows/ci.yml
        |
        | calls
        v
ci-toolkit
```

This separation keeps the reusable toolkit generic and prevents application or infrastructure-specific information from being embedded in the toolkit.

---

# Related documentation

- [`reusable-workflows.md`](./reusable-workflows.md)
- [`permissions.md`](./permissions.md)
- [`secrets.md`](./secrets.md)
- [`variables.md`](./variables.md)
- [`migration-checklist.md`](./migration-checklist.md)