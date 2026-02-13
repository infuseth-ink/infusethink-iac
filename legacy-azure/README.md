# Legacy Azure App Service Implementation

> [!WARNING]
> This code is **untested after the mono-repo refactor**.
>
> - Uses legacy `.sync()` pattern (pre-ComponentResource refactor)
> - Azure App Service (PaaS) approach - not suitable for VM/container learning
> - Kept for reference only
> - **Do not use for new deployments**

## Why Archived

App Service (PaaS) abstracts away too much infrastructure detail. For learning scalable architecture
patterns (VMs, containers, Kubernetes), a lower-level approach is more valuable.

This setup was built for:
- **Learning PaaS patterns**: Azure App Service abstractions
- **Easy deployment**: Minimal infrastructure management
- **Quick prototyping**: Rapid iteration without DevOps complexity

The new implementation focuses on:
- **VM management**: EC2, Azure VMs
- **Container orchestration**: Docker, future K8s preparation
- **Infrastructure fundamentals**: Networking, security groups, load balancing
- **Cost optimization**: Granular control vs PaaS pricing

## Original Structure

```
modules/
  backend/      - FastAPI App Service
  frontend/     - Flutter web hosting
  database/     - PostgreSQL Flexible Server
  dns/          - Azure DNS Zone
  shared/       - Resource groups

config/         - Environment configs (dev, prod)
shared-infra/   - Shared PostgreSQL server stack
__main__.py     - Main orchestration
```

## To Use This Code

1. Ensure you have the old Pulumi stack state
2. Be aware this uses the old `.sync()` factory pattern
3. May have breaking changes from refactor
4. Consider migrating to the new VM-based implementation instead
