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
        tags: dict[str, str] | None = None,
    ) -> tuple[web.AppServicePlan, web.WebApp]:
        """Create an App Service Plan and Web App for FastAPI backend hosting."""

        # Create App Service Plan for backend
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
                "Component": "Backend-Plan",
                "Application": "Infusethink",
                **(tags or {}),
            },
        )

        # Create Web App for FastAPI backend
        web_app = web.WebApp(
            f"{app_name}",
            resource_group_name=resource_group_name,
            location=location,
            name=f"{app_name}",
            server_farm_id=app_service_plan.id,
            site_config=web.SiteConfigArgs(
                # Python 3.13 runtime for FastAPI
                linux_fx_version="PYTHON|3.13",
                # FastAPI with uvicorn startup command
                app_command_line="uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4",
                app_settings=[
                    web.NameValuePairArgs(
                        name="SCM_DO_BUILD_DURING_DEPLOYMENT", value="true"
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
