"""Production environment configuration."""

from typing import Any

# Environment-specific configuration
ENVIRONMENT = "prod"

# Frontend configuration (Azure App Service)
FRONTEND_CONFIG = {
    "app_name": "infusethink-app",
    "sku_tier": "F1",  # App Service SKU (F1 is free tier)
    "custom_domain": "www.infuseth.ink",
}

# Backend configuration (Azure App Service)
BACKEND_CONFIG = {
    "app_name": "infusethink-api",
    "sku_tier": "F1",  # App Service SKU (F1 is free tier)
    "custom_domain": "api.infuseth.ink",
}

# Database configuration (PostgreSQL Flexible Server)
DATABASE_CONFIG = {
    "database_name": "infusethink_prod",  # Database name with environment suffix
    "admin_username": "infusethink_admin",  # Must match shared server's admin username
}

# DNS configuration (only in production)
DNS_CONFIG = {
    "domain_name": "infuseth.ink",
    "email": {
        "mx_records": [
            ("mx1.privateemail.com.", 10),
            ("mx2.privateemail.com.", 10),
        ],
        "spf": "v=spf1 include:spf.privateemail.com ~all",
        # DKIM record split into chunks (Azure DNS has 255 char limit per string)
        "dkim": [
            "v=DKIM1;k=rsa;p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqHfS1n3GDYIg+/WlerdvooNBs/1XeFtm1nh3cCxFFktUbXoYNkDMTLHITpT8ngk6CZ7s+qHegqPzh6O7i0jKTCMfPrK7FbZBTPXMctzY6FSWe0xGYK+LakLtvXktnZd90SAtKyBnUe62hqB9EXNpvRF2vHQlavCIuLEj2Ci8MeO",
            "HLx9jNvZH6CaTEtb/AxxMQPrwwFOZ5at4ta83RxQNKQtlAPBIfrDt1i/E+yC6yskVK1CC2UEYZINQrFuz3CFPX1Et0ES60gL/H4tLtZ8N3bnfthS3qWPCt79a+lsSCmrIwggjZjA2+oVPMmiOATZCeCZVze33T++xDnJNj3pN+wIDAQAB",
        ],
        "dmarc": "v=DMARC1; p=none; rua=mailto:dmarc@infuseth.ink",
    },
}

# Shared configuration
SHARED_CONFIG = {
    "tags": {
        "Purpose": "Production",
        "CostCenter": "Operations",
        "Owner": "Platform Team",
    },
}


def get_config() -> dict[str, Any]:
    """Get complete configuration for prod environment."""
    return {
        "environment": ENVIRONMENT,
        "frontend": FRONTEND_CONFIG,
        "backend": BACKEND_CONFIG,
        "database": DATABASE_CONFIG,
        "dns": DNS_CONFIG,
        "shared": SHARED_CONFIG,
    }
