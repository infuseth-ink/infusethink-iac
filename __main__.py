"""Infuseth.ink Infrastructure as Code with Pulumi and Azure - Frontend and Backend."""

import pulumi

from config import load_config
from modules.backend.infuseth_backend import InfusethBackend
from modules.database.infuseth_database import InfusethDatabase

# Import DNS module (only used in prod, but imported to avoid linter warnings)
from modules.dns.azure_dns_zone import AzureDnsZone
from modules.frontend.infuseth_frontend import InfusethFrontend
from modules.shared.infusethink_resource_group import InfusethinkResourceGroup

# Load environment-specific configuration
config = load_config()
env_config = config["environment"]
frontend_config = config["frontend"]
backend_config = config["backend"]
database_config = config["database"]
shared_config = config["shared"]

# Get Azure location from Pulumi config
azure_config = pulumi.Config("azure-native")
location = azure_config.require("location")

# Reference shared infrastructure stack for PostgreSQL server details
# To create the shared stack first, cd into shared-infra and run:
# pulumi stack init shared
# pulumi config set --secret db_admin_password <password>
# pulumi up
org_name = pulumi.get_organization()
project_name = "infusethink-shared"  # Must match shared-infra/Pulumi.yaml project name
stack_name = "shared"
shared_stack = pulumi.StackReference(f"{org_name}/{project_name}/{stack_name}")

# Get shared PostgreSQL server details and credentials from shared stack
postgres_server_name = shared_stack.require_output("postgres_server_name")
postgres_server_fqdn = shared_stack.require_output("postgres_server_fqdn")
shared_resource_group_name = shared_stack.require_output("resource_group_name")
postgres_admin_password = shared_stack.require_output("postgres_admin_password")

# Create environment-specific resource group for frontend/backend
resource_group = InfusethinkResourceGroup.sync(
    "infusethink", location=location, environment=env_config, tags=shared_config["tags"]
)

# Create shared App Service Plan for production (to save costs)
# In prod, both frontend and backend share a single B1 plan (~$13/month total vs ~$26 for two)
# In dev, each service gets its own F1 free plan
shared_app_service_plan = None
if env_config == "prod":
    from pulumi_azure_native import web

    shared_app_service_plan = web.AppServicePlan(
        "asp-shared-prod",
        resource_group_name=resource_group.name,
        location=location,
        name="asp-infusethink-prod",
        kind="linux",
        reserved=True,
        sku={
            "name": "B1",
            "tier": "Basic",
        },
        tags={
            "Environment": env_config,
            "Component": "Shared-Plan",
            "Application": "Infusethink",
            **shared_config["tags"],
        },
    )

# Create frontend (App Service)
frontend_app_service_plan, frontend_web_app = InfusethFrontend.sync(
    "frontend",
    resource_group_name=resource_group.name,
    location=location,
    environment=env_config,
    app_name=frontend_config["app_name"],
    sku_tier=frontend_config["sku_tier"],
    shared_app_service_plan=shared_app_service_plan,
    custom_domain=frontend_config.get("custom_domain"),
    tags=shared_config["tags"],
)

# Create PostgreSQL database on shared server (in shared resource group)
postgres_database, connection_string = InfusethDatabase.sync(
    "database",
    resource_group_name=shared_resource_group_name,
    server_name=postgres_server_name,
    server_fqdn=postgres_server_fqdn,
    database_name=database_config["database_name"],
    admin_username=database_config["admin_username"],
    admin_password=postgres_admin_password,  # Use password from shared stack
    tags=shared_config["tags"],
)

# Create backend (App Service for FastAPI)
backend_app_service_plan, backend_web_app = InfusethBackend.sync(
    "backend",
    resource_group_name=resource_group.name,
    location=location,
    environment=env_config,
    app_name=backend_config["app_name"],
    sku_tier=backend_config["sku_tier"],
    database_connection_string=connection_string,
    shared_app_service_plan=shared_app_service_plan,
    custom_domain=backend_config.get("custom_domain"),
    tags=shared_config["tags"],
)

# ============================================
# DNS Zone (Production only)
# ============================================

# Only create DNS zone in production (not dev/staging)
if env_config == "prod" and "dns" in config:
    dns_config = config["dns"]

    # Create Azure DNS Zone for domain management
    dns_zone = AzureDnsZone.sync(
        name="infuseth-dns-zone",
        resource_group_name=resource_group.name,
        location=location,
        domain_name=dns_config["domain_name"],
        tags={
            "Environment": env_config,
            **shared_config["tags"],
        },
    )

    # MX Records - Routes incoming email to Namecheap's mail servers
    email_mx_records = AzureDnsZone.create_mx_record(
        name="email-mx-records",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="@",
        mail_exchanges=dns_config["email"]["mx_records"],
        ttl=3600,
    )

    # SPF Record - Prevents email spoofing
    email_spf_record = AzureDnsZone.create_txt_record(
        name="email-spf-record",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="@",
        txt_value=dns_config["email"]["spf"],
        ttl=3600,
    )

    # DKIM Record - Cryptographic signing (split into chunks for Azure DNS 255 char limit)
    email_dkim_record = AzureDnsZone.create_txt_record(
        name="email-dkim-record",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="default._domainkey",
        txt_value=dns_config["email"]["dkim"],
        ttl=3600,
    )

    # DMARC Record - Email policy and reporting
    email_dmarc_record = AzureDnsZone.create_txt_record(
        name="email-dmarc-record",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="_dmarc",
        txt_value=dns_config["email"]["dmarc"],
        ttl=3600,
    )

    # CNAME Record - Frontend custom domain (app.infuseth.ink → Azure App Service)
    frontend_cname_record = AzureDnsZone.create_cname_record(
        name="frontend-cname",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="app",
        cname_target=frontend_web_app.default_host_name,
        ttl=3600,
    )

    # CNAME Record - Backend custom domain (api.infuseth.ink → Azure App Service)
    backend_cname_record = AzureDnsZone.create_cname_record(
        name="backend-cname",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="api",
        cname_target=backend_web_app.default_host_name,
        ttl=3600,
    )

    # TXT Record - Domain verification for frontend (asuid.app.infuseth.ink)
    # Cast Output to handle potential None value
    frontend_verification_id = pulumi.Output.all(
        frontend_web_app.custom_domain_verification_id
    ).apply(lambda ids: ids[0] if ids[0] else "")
    frontend_verification_record = AzureDnsZone.create_txt_record(
        name="frontend-verification",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="asuid.app",
        txt_value=frontend_verification_id,
        ttl=3600,
    )

    # TXT Record - Domain verification for backend (asuid.api.infuseth.ink)
    backend_verification_id = pulumi.Output.all(
        backend_web_app.custom_domain_verification_id
    ).apply(lambda ids: ids[0] if ids[0] else "")
    backend_verification_record = AzureDnsZone.create_txt_record(
        name="backend-verification",
        resource_group_name=resource_group.name,
        zone_name=dns_zone.name,
        record_name="asuid.api",
        txt_value=backend_verification_id,
        ttl=3600,
    )

    # Import web module for hostname bindings
    from pulumi_azure_native import web

    # At this point, shared_app_service_plan is guaranteed to be non-None (we're in prod)
    assert shared_app_service_plan is not None, (
        "shared_app_service_plan must exist in prod"
    )

    # Custom domain binding for frontend with managed SSL certificate
    if frontend_config.get("custom_domain"):
        # Create free managed certificate (Azure will create temp binding internally for validation)
        frontend_certificate = web.Certificate(
            "frontend-managed-cert",
            resource_group_name=resource_group.name,
            name=f"{frontend_config['custom_domain']}-cert",
            location=location,
            canonical_name=frontend_config["custom_domain"],
            server_farm_id=shared_app_service_plan.id,
            opts=pulumi.ResourceOptions(
                depends_on=[frontend_verification_record, frontend_cname_record]
            ),
        )

        # Bind hostname with SSL enabled using the managed certificate
        frontend_hostname_binding = web.WebAppHostNameBinding(
            "frontend-custom-domain",
            resource_group_name=resource_group.name,
            name=frontend_web_app.name,
            host_name=frontend_config["custom_domain"],
            site_name=frontend_web_app.name,
            ssl_state=web.SslState.SNI_ENABLED,
            thumbprint=frontend_certificate.thumbprint,
            opts=pulumi.ResourceOptions(depends_on=[frontend_certificate]),
        )

    # Custom domain binding for backend with managed SSL certificate
    if backend_config.get("custom_domain"):
        # Create free managed certificate (Azure will create temp binding internally for validation)
        backend_certificate = web.Certificate(
            "backend-managed-cert",
            resource_group_name=resource_group.name,
            name=f"{backend_config['custom_domain']}-cert",
            location=location,
            canonical_name=backend_config["custom_domain"],
            server_farm_id=shared_app_service_plan.id,
            opts=pulumi.ResourceOptions(
                depends_on=[backend_verification_record, backend_cname_record]
            ),
        )

        # Bind hostname with SSL enabled using the managed certificate
        backend_hostname_binding = web.WebAppHostNameBinding(
            "backend-custom-domain",
            resource_group_name=resource_group.name,
            name=backend_web_app.name,
            host_name=backend_config["custom_domain"],
            site_name=backend_web_app.name,
            ssl_state=web.SslState.SNI_ENABLED,
            thumbprint=backend_certificate.thumbprint,
            opts=pulumi.ResourceOptions(depends_on=[backend_certificate]),
        )

    # Export DNS zone name for prod
    pulumi.export("dns_zone_name", dns_zone.name)

# Export important values
pulumi.export("environment", env_config)
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("frontend_app_service_plan_name", frontend_app_service_plan.name)
pulumi.export("frontend_url", frontend_web_app.default_host_name)
pulumi.export("backend_app_service_plan_name", backend_app_service_plan.name)
pulumi.export("backend_url", backend_web_app.default_host_name)
pulumi.export("database_server_name", postgres_server_name)
pulumi.export("database_host", postgres_server_fqdn)
pulumi.export("database_name", postgres_database.name)
pulumi.export("database_connection_string", connection_string)  # Exported as secret
