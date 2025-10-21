"""Shared Infrastructure for Infuseth.ink - PostgreSQL Server."""

from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import pulumi
from pulumi_azure_native import resources

from modules.database.infuseth_database import InfusethDatabaseServer

# Get Azure location from Pulumi config
azure_config = pulumi.Config("azure-native")
location = azure_config.require("location")

# Get database credentials from Pulumi config (stored as secrets)
# To set: pulumi config set --secret db_admin_password <your-secure-password>
db_config = pulumi.Config()
db_admin_username = db_config.require("db_admin_username")
db_admin_password = db_config.require_secret("db_admin_password")

# Create shared resource group for database
shared_rg = resources.ResourceGroup(
    "rg-infusethink-shared",
    resource_group_name="rg-infusethink-shared",
    location=location,
    tags={
        "Environment": "Shared",
        "Application": "Infusethink",
        "ManagedBy": "Pulumi",
        "Purpose": "Shared PostgreSQL server for all environments",
    },
)

# Create shared PostgreSQL Flexible Server
postgres_server = InfusethDatabaseServer.sync(
    "shared-db-server",
    resource_group_name=shared_rg.name,
    location=location,
    server_name="infusethink",
    admin_username=db_admin_username,
    admin_password=db_admin_password,
    sku_name="Standard_B1ms",  # Cheapest tier
    storage_size_gb=32,
    postgresql_version="17",  # Latest stable version
    tags={
        "Environment": "Shared",
        "Component": "Database-Server",
        "Application": "Infusethink",
    },
)

# Export values for other stacks to reference
pulumi.export("resource_group_name", shared_rg.name)
pulumi.export("postgres_server_name", postgres_server.name)
pulumi.export("postgres_server_fqdn", postgres_server.fully_qualified_domain_name)
pulumi.export("postgres_admin_username", db_admin_username)
