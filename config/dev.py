"""Development environment configuration."""

from typing import Any

# Environment-specific configuration
ENVIRONMENT = "dev"

# Frontend configuration (Azure App Service)
FRONTEND_CONFIG = {
    "app_name": "infusethink-trials",
    "sku_tier": "F1",  # App Service SKU (F1 is free tier)
    "custom_domain": None,
}

# Backend configuration (Azure App Service)
BACKEND_CONFIG = {
    "app_name": "infusethink-labs",
    "sku_tier": "F1",  # App Service SKU (F1 is free tier)
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
        "backend": BACKEND_CONFIG,
        "shared": SHARED_CONFIG,
    }
