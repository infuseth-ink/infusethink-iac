"""Infuseth.ink Infrastructure as Code with Pulumi and Azure - Frontend and Backend."""

import pulumi

from config import load_config
from modules.backend.infuseth_backend import InfusethBackend
from modules.database.infuseth_database import InfusethDatabase
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

# Create frontend (App Service)
frontend_app_service_plan, frontend_web_app = InfusethFrontend.sync(
    "frontend",
    resource_group_name=resource_group.name,
    location=location,
    environment=env_config,
    app_name=frontend_config["app_name"],
    sku_tier=frontend_config["sku_tier"],
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
    tags=shared_config["tags"],
)

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
