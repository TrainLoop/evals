# Infrastructure Overview

The `infra/` folder contains the Pulumi program used to deploy the Studio UI on
AWS Fargate with an S3 bucket and EFS volume. Key files:

- `index.ts` &ndash; main Pulumi stack creating the load balancer, ECS service and
  auto-scaling rules.
- `Pulumi.yaml` and `Pulumi.trainloop.yaml` &ndash; stack configuration.

To preview or update the infrastructure:

```bash
cd infra
npm install
pulumi preview  # see planned changes
pulumi up       # apply changes
```

The stack expects configuration values such as `resource-prefix`,
`hostedZoneDomain`, `subdomain` and `appImage`. Secrets are managed through
Pulumi's standard configuration system.
