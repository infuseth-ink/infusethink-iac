# Infuseth.ink Infrastructure as Code

Infrastructure as Code for Infuseth.ink using Pulumi and Azure. This project manages a multi-environment setup with frontend (Static Web Apps) and backend (App Service) deployments.

## 🏗️ Architecture Overview

This infrastructure supports a modular, multi-environment setup with separate frontend and backend services:

### Environment Plan

#### Development
- **Frontend**: `infusethink-trials.azurewebsites.net`
- **Backend**: `infusethink-labs.azurewebsites.net`
- **Purpose**: Development testing - you can break it, minimal coordination needed

#### Staging
- **Frontend**: `infusethink-demo.azurewebsites.net`
- **Backend**: `infusethink-backstage.azurewebsites.net`
- **Purpose**: QA and demo purposes - gatekeeps production

#### Production
- **Frontend**: `app.infuseth.ink` (custom domain) / `infusethink-app.azurewebsites.net`
- **Backend**: `api.infuseth.ink` (custom domain) / `infusethink-api.azurewebsites.net`
- **Purpose**: Production environment

### Environment Notes

- **dev**: Experimental environment where any developer can push with minimal coordination. Perfect for testing:
  - Remote environment issues you're not confident testing locally
  - Cookie SameSite policies and cross-origin behavior
  - CDN and caching behavior
  - Sharing a possibly unstable version with team members or stakeholders
  - Offloading backend to free up laptop resources
- **staging**: QA and demonstration environment. Changes require review and gatekeeps production from bugs
  - Final QA testing before production
  - Client demonstrations and previews
- **prod**: Production environment with custom domains and full monitoring

### Azure Services Used

- **Frontend**: Azure Static Web Apps (free tier available)

## 🚀 Deployment

### Prerequisites

- Azure CLI installed and authenticated (`az login`)
- Pulumi CLI installed
- Python 3.13+ with uv package manager

### Setup

1. Install dependencies:

   ```bash
   uv sync --dev
   ```

2. Configure Pulumi stack for your environment:

   ```bash
   pulumi stack init dev  # or staging/prod
   pulumi config set azure-native:location southeastasia
   ```

3. Deploy:
   ```bash
   pulumi up
   ```

## 🛠️ Development

This project uses modern Python development tools:

- **Ruff**: Fast linting and formatting
- **Pyright**: Static type checking
- **Commitizen**: Conventional commit messages
- **pre-commit**: Automated code quality checks

### Commit Message Format

Use conventional commits:

```bash
feat: add new Azure Static Web App module
fix: resolve DNS configuration issue
docs: update deployment guide
```

Or use the interactive tool:

```bash
cz commit
```

## 📁 Project Structure

```
├── __main__.py              # Main Pulumi program
├── modules/                 # Reusable Pulumi modules
│   ├── frontend/           # Static Web App module
│   ├── backend/            # App Service module
│   └── shared/             # Shared resources (storage, DNS)
├── config/                 # Environment-specific configurations
└── scripts/                # Deployment and utility scripts
```
