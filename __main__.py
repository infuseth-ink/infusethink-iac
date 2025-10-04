"""Infuseth.ink Infrastructure as Code with Pulumi and Azure - Frontend Only."""

import pulumi

from config import load_config
from modules.frontend.infuseth_frontend import InfusethFrontend
from modules.shared.infusethink_resource_group import InfusethinkResourceGroup

# Load environment-specific configuration
config = load_config()
env_config = config["environment"]
frontend_config = config["frontend"]
shared_config = config["shared"]

# Get Azure location from Pulumi config
azure_config = pulumi.Config("azure-native")
location = azure_config.require("location")

# Create shared resource group
resource_group = InfusethinkResourceGroup.sync(
    "infusethink", location=location, environment=env_config, tags=shared_config["tags"]
)

# Create frontend (Static Web App)
frontend = InfusethFrontend.sync(
    "frontend",
    resource_group_name=resource_group.name,
    location=location,
    environment=env_config,
    app_name=frontend_config["app_name"],
    sku_tier=frontend_config["sku_tier"],
    tags=shared_config["tags"],
)

# Export important values
pulumi.export("environment", env_config)
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("frontend_url", frontend.default_hostname)
