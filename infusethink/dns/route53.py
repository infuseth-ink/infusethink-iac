from collections.abc import Sequence

import pulumi
import pulumi_aws as aws


class AwsRoute53Zone(pulumi.ComponentResource):
    zone: aws.route53.Zone
    """Route 53 hosted zone resource."""

    zone_id: pulumi.Output[str]
    """ID of the hosted zone."""

    name_servers: pulumi.Output[Sequence[str]]
    """List of name servers for the hosted zone."""

    def __init__(
        self,
        name: str,
        domain_name: str,
        opts: pulumi.ResourceOptions | None = None,
    ):
        """
        Create a Route 53 Hosted Zone.

        Args:
            name: Pulumi resource name
            domain_name: Domain name for the hosted zone (e.g., "infuseth.ink")
            opts: Optional Pulumi resource options
        """
        super().__init__(
            "infusethink:aws:Route53Zone",
            name,
            {"domain_name": domain_name},
            opts,
        )

        child_opts = pulumi.ResourceOptions(parent=self)

        self.zone = aws.route53.Zone(
            f"{name}-zone",
            name=domain_name,
            comment=f"Managed by Pulumi - {domain_name}",
            opts=child_opts,
        )

        self.zone_id = self.zone.zone_id
        self.name_servers = self.zone.name_servers

        self.register_outputs(
            {
                "zone_id": self.zone_id,
                "name_servers": self.name_servers,
            }
        )
