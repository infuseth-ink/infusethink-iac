"""Azure Static Web App module for frontend hosting."""

import pulumi
from pulumi_azure_native import web


class InfusethFrontend:
    """Azure Static Web App factory."""

    @classmethod
    def sync(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        location: pulumi.Input[str],
        environment: str,
        app_name: str,
        sku_tier: str = "Free",
        tags: dict[str, str] | None = None,
    ) -> web.StaticSite:
        """Create a Static Web App with simplified arguments."""
        return web.StaticSite(
            app_name,
            resource_group_name=resource_group_name,
            location=location,
            name=app_name,
            sku={
                "name": sku_tier,
                "tier": sku_tier,
            },
            build_properties={
                "app_location": "/",
                "api_location": "",  # No API for Flutter web app
                "output_location": "build/web",  # Flutter web build output
            },
            tags={
                "Environment": environment,
                "Component": "Frontend",
                "Application": "Infusethink",
                **(tags or {}),
            },
        )
