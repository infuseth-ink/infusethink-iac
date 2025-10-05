"""Resource Group module for shared Azure resources."""

import pulumi
from pulumi_azure_native import resources


class InfusethinkResourceGroup:
    """Azure Resource Group factory."""

    @classmethod
    def sync(
        cls,
        name: str,
        location: pulumi.Input[str],
        environment: str,
        tags: dict[str, str] | None = None,
    ) -> resources.ResourceGroup:
        """Create a Resource Group with simplified arguments."""
        return resources.ResourceGroup(
            f"rg-{name}-{environment}",
            resource_group_name=f"rg-infusethink-{environment}",
            location=location,
            tags={
                "Environment": environment,
                "Application": "Infusethink",
                "ManagedBy": "Pulumi",
                **(tags or {}),
            },
        )
