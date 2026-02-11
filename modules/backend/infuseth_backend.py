"""Azure App Service module for backend API hosting."""

from typing import Literal

import pulumi
from pulumi_azure_native import web

# Define valid App Service Plan SKUs
AppServiceSku = Literal["F1", "B1", "B2", "B3", "S1", "S2", "S3", "P1", "P2", "P3"]


class InfusethBackend:
    """Azure App Service factory for FastAPI backend hosting."""

    @classmethod
    def sync(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        location: pulumi.Input[str],
        environment: str,
        app_name: str,
        sku_tier: AppServiceSku = "F1",
        database_connection_string: pulumi.Input[str] | None = None,
        shared_app_service_plan: web.AppServicePlan | None = None,
        custom_domain: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> tuple[web.AppServicePlan, web.WebApp]:
        """Create an App Service Plan and Web App for FastAPI backend hosting.

        Args:
            name: Pulumi resource name
            resource_group_name: Azure resource group name
            location: Azure region location
            environment: Environment name (dev, prod)
            app_name: App Service name
            sku_tier: App Service Plan SKU tier
            database_connection_string: Optional database connection string
            shared_app_service_plan: Optional existing App Service Plan to reuse
            custom_domain: Optional custom domain for hostname binding (requires B1+)
            tags: Optional resource tags
        """

        # Create or reuse App Service Plan
        app_service_plan = (
            shared_app_service_plan
            if shared_app_service_plan
            else web.AppServicePlan(
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
                    "Component": "Backend-Plan",
                    "Application": "Infusethink",
                    **(tags or {}),
                },
            )
        )

        # Create Web App for FastAPI backend
        web_app = web.WebApp(
            f"{app_name}",
            resource_group_name=resource_group_name,
            location=location,
            name=f"{app_name}",
            server_farm_id=app_service_plan.id,
            https_only=True,  # Redirect HTTP to HTTPS
            site_config=web.SiteConfigArgs(
                # Python 3.13 runtime for FastAPI
                linux_fx_version="PYTHON|3.13",
                # Gunicorn startup command for FastAPI
                app_command_line="gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT src.main:app",
                app_settings=[
                    web.NameValuePairArgs(
                        name="SCM_DO_BUILD_DURING_DEPLOYMENT", value="true"
                    ),
                    # Run Alembic migrations after build completes (official recommended approach)
                    web.NameValuePairArgs(
                        name="POST_BUILD_COMMAND", value="alembic upgrade head"
                    ),
                    # Add database connection string if provided
                    *(
                        [
                            web.NameValuePairArgs(
                                name="DATABASE_URL", value=database_connection_string
                            )
                        ]
                        if database_connection_string
                        else []
                    ),
                ],
                http20_enabled=True,
                always_on=sku_tier != "F1",
            ),
            tags={
                "Environment": environment,
                "Component": "Backend",
                "Application": "Infusethink",
                **(tags or {}),
            },
        )

        return app_service_plan, web_app
