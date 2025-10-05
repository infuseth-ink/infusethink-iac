"""Azure App Service module for frontend hosting."""

from typing import Literal

import pulumi
from pulumi_azure_native import web

# Define valid App Service Plan SKUs
AppServiceSku = Literal["F1", "B1", "B2", "B3", "S1", "S2", "S3", "P1", "P2", "P3"]


class InfusethFrontend:
    """Azure App Service factory for Flutter web hosting."""

    @classmethod
    def sync(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        location: pulumi.Input[str],
        environment: str,
        app_name: str,
        sku_tier: AppServiceSku = "F1",
        tags: dict[str, str] | None = None,
    ) -> tuple[web.AppServicePlan, web.WebApp]:
        """Create an App Service Plan and Web App for Flutter hosting."""

        # Create App Service Plan
        app_service_plan = web.AppServicePlan(
            f"asp-{app_name}",
            resource_group_name=resource_group_name,
            location=location,
            # TODO: for prod we plan to share the ASP across FE and BE, so name using the resource group
            name=f"asp-{app_name}",
            kind="linux",
            reserved=True,
            sku={
                "name": sku_tier,
                "tier": "Free"
                if sku_tier == "F1"
                else "Basic"
                if sku_tier.startswith("B")
                else "Standard"
                if sku_tier.startswith("S")
                else "Premium",
            },
            tags={
                "Environment": environment,
                "Component": "Frontend-Plan",
                "Application": "Infusethink",
                **(tags or {}),
            },
        )

        # Create Web App
        web_app = web.WebApp(
            app_name,
            resource_group_name=resource_group_name,
            location=location,
            name=app_name,
            server_farm_id=app_service_plan.id,
            site_config={
                # TODO: Migrate to NODE|24-lts once Azure App Service adds support
                "linuxFxVersion": "NODE:22-lts",
                "appCommandLine": "npx serve build/web -s -p 8080",
                "appSettings": [
                    {"name": "WEBSITE_NODE_DEFAULT_VERSION", "value": "22-lts"},
                    {"name": "SCM_DO_BUILD_DURING_DEPLOYMENT", "value": "false"},
                    {"name": "WEBSITE_RUN_FROM_PACKAGE", "value": "1"},
                ],
                "defaultDocuments": ["index.html"],
                "http20Enabled": True,
                "alwaysOn": sku_tier != "F1",
            },
            tags={
                "Environment": environment,
                "Component": "Frontend",
                "Application": "Infusethink",
                **(tags or {}),
            },
        )

        return app_service_plan, web_app
