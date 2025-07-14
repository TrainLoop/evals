---
sidebar_position: 3
---

# Cloud Deployment

Deploy TrainLoop Evals to a cloud environment for team access.

## Tutorial

1. Build all components:
   ```bash
   npm run build
   ```
2. Configure cloud storage (S3, GCS, or Azure):
   ```bash
   trainloop config set storage s3://my-bucket
   ```
3. Push the Studio UI to your hosting service.
4. Share the URL with your team.

## How-tos

- [S3 integration](../docs/reference/integration/s3.md)
- [GCS integration](../docs/reference/integration/gcs.md)
- [Azure integration](../docs/reference/integration/azure.md)

## Pitfalls

- Ensure credentials are available during deployment.
- Flush events before uploading logs.
- Label each environment (dev, staging, prod).
- Keep configuration files in version control to avoid cascade issues.
