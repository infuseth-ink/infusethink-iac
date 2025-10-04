"""Development environment configuration."""

from typing import Any

# Environment-specific configuration
ENVIRONMENT = "dev"

# Frontend configuration (Azure Static Web App)
FRONTEND_CONFIG = {
    "app_name": "infusethink-trials",
    "sku_tier": "Free",  # Static Web App SKU (Free or Standard)
    "custom_domain": None,
}


# Shared configuration
SHARED_CONFIG = {
    "tags": {
        "Purpose": "Development testing and experimentation",
        "CostCenter": "Engineering",
        "Owner": "Development Team",
    },
}


def get_config() -> dict[str, Any]:
    """Get complete configuration for dev environment."""
    return {
        "environment": ENVIRONMENT,
        "frontend": FRONTEND_CONFIG,
        "shared": SHARED_CONFIG,
    }
