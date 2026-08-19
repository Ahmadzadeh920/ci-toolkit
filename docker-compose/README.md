# docker-compose/

Minimal example file consumed by
[`reusable-deploy-docker-compose.yml`](../.github/workflows/reusable-deploy-docker-compose.yml).

This is **not a real application** — it's a placeholder showing the shape
the workflow expects. Replace `app`, the image, and the port mapping with
your own service(s) before using it.

## Usage

Reference this file (or your own copy of it) via the `compose-file` input:

```yaml
jobs:
  deploy:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-docker-compose.yml@v1
    with:
      compose-file: docker-compose/docker-compose.yml
      image: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
      remote-directory: /opt/my-app
    secrets:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

The workflow SSHes into `ssh-host` and runs Docker Compose using this file
against the image/tag you pass in. If your Compose file defines multiple
services, use the optional `compose-service` input to target just one.

See [`docs/reusable-workflows.md`](../docs/reusable-workflows.md) for the
full input/secret contract.
