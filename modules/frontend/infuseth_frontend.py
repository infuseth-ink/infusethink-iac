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
        custom_domain: str | None = None,
        shared_app_service_plan: web.AppServicePlan | None = None,
        tags: dict[str, str] | None = None,
    ) -> tuple[web.AppServicePlan, web.WebApp]:
        """Create an App Service Plan and Web App for Flutter hosting.

        Args:
            name: Pulumi resource name
            resource_group_name: Resource group
            location: Azure region
            environment: Environment name
            app_name: App Service name
            sku_tier: App Service Plan SKU
            custom_domain: Optional custom domain (e.g., "app.infuseth.ink")
            shared_app_service_plan: Optional existing App Service Plan to reuse
            tags: Optional tags

        Returns:
            Tuple of (App Service Plan, Web App)
        """

        # Use shared plan if provided, otherwise create new one
        if shared_app_service_plan:
            app_service_plan = shared_app_service_plan
        else:
            # Create App Service Plan
            app_service_plan = web.AppServicePlan(
                f"asp-{app_name}",
                resource_group_name=resource_group_name,
                location=location,
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
            https_only=True,  # Automatically redirect all HTTP requests to HTTPS
            site_config=web.SiteConfigArgs(
                # TODO: Migrate to NODE|24-lts once Azure App Service adds support
                linux_fx_version="NODE|22-lts",
                app_command_line="npx serve ./web -s -p $PORT",
                app_settings=[
                    web.NameValuePairArgs(
                        name="WEBSITE_NODE_DEFAULT_VERSION", value="22-lts"
                    ),
                    web.NameValuePairArgs(
                        name="SCM_DO_BUILD_DURING_DEPLOYMENT", value="false"
                    ),
                    web.NameValuePairArgs(name="WEBSITE_RUN_FROM_PACKAGE", value="1"),
                ],
                default_documents=["index.html"],
                http20_enabled=True,
                always_on=sku_tier != "F1",
            ),
            tags={
                "Environment": environment,
                "Component": "Frontend",
                "Application": "Infusethink",
                **(tags or {}),
            },
        )

        return app_service_plan, web_app
