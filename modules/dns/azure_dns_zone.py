"""Azure DNS Zone module for domain management."""

import pulumi
from pulumi_azure_native import dns


class AzureDnsZone:
    """Azure DNS Zone factory for domain management."""

    @classmethod
    def sync(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        location: pulumi.Input[str],
        domain_name: str,
        tags: dict[str, str] | None = None,
    ) -> dns.Zone:
        """Create an Azure DNS Zone for a domain.

        Args:
            name: Pulumi resource name for the DNS zone
            resource_group_name: Resource group to create the zone in
            location: Azure region (note: DNS zones are always global)
            domain_name: The domain name (e.g., "infuseth.ink")
            tags: Optional tags for the resource

        Returns:
            The created DNS zone resource
        """

        dns_zone = dns.Zone(
            name,
            resource_group_name=resource_group_name,
            zone_name=domain_name,
            location="global",  # DNS zones are always global
            zone_type=dns.ZoneType.PUBLIC,
            tags={
                "Component": "DNS",
                "Domain": domain_name,
                **(tags or {}),
            },
        )

        # Export nameservers for domain registrar configuration
        pulumi.export(f"{name}_nameservers", dns_zone.name_servers)

        return dns_zone

    @classmethod
    def create_cname_record(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        zone_name: pulumi.Input[str],
        record_name: str,
        cname_target: pulumi.Input[str],
        ttl: int = 3600,
    ) -> dns.RecordSet:
        """Create a CNAME record in the DNS zone.

        Args:
            name: Pulumi resource name for the CNAME record
            resource_group_name: Resource group containing the DNS zone
            zone_name: Name of the DNS zone (e.g., "infuseth.ink")
            record_name: The subdomain (e.g., "api" creates "api.infuseth.ink")
            cname_target: Target domain/hostname for the CNAME
            ttl: Time to live in seconds (default: 3600 = 1 hour)

        Returns:
            The created CNAME record resource
        """

        return dns.RecordSet(
            name,
            resource_group_name=resource_group_name,
            zone_name=zone_name,
            relative_record_set_name=record_name,
            record_type="CNAME",
            ttl=ttl,
            cname_record=dns.CnameRecordArgs(
                cname=cname_target,
            ),
        )

    @classmethod
    def create_txt_record(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        zone_name: pulumi.Input[str],
        record_name: str,
        txt_value: pulumi.Input[str] | pulumi.Input[list[str]],
        ttl: int = 3600,
    ) -> dns.RecordSet:
        """Create a TXT record in the DNS zone (for domain verification).

        Args:
            name: Pulumi resource name for the TXT record
            resource_group_name: Resource group containing the DNS zone
            zone_name: Name of the DNS zone
            record_name: The subdomain or "@" for root domain
            txt_value: The TXT record value (string or list of strings for long records)
                Azure DNS requires strings to be max 255 chars, so long records
                (like DKIM) should be split into a list of strings
            ttl: Time to live in seconds (default: 3600 = 1 hour)

        Returns:
            The created TXT record resource
        """

        # Handle both single string and list of strings
        # When txt_value is a Pulumi Output, we need to use apply() to transform it
        def ensure_list(
            value: pulumi.Input[str] | pulumi.Input[list[str]],
        ) -> list[str]:
            if isinstance(value, str):
                return [value]
            elif isinstance(value, list):
                return value
            else:
                # For other Input types, return as-is (will be resolved by Pulumi)
                return [value]  # type: ignore

        value_list = pulumi.Output.from_input(txt_value).apply(ensure_list)

        return dns.RecordSet(
            name,
            resource_group_name=resource_group_name,
            zone_name=zone_name,
            relative_record_set_name=record_name,
            record_type="TXT",
            ttl=ttl,
            txt_records=[
                dns.TxtRecordArgs(
                    value=value_list,
                )
            ],
        )

    @classmethod
    def create_a_record(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        zone_name: pulumi.Input[str],
        record_name: str,
        ipv4_address: pulumi.Input[str],
        ttl: int = 3600,
    ) -> dns.RecordSet:
        """Create an A record in the DNS zone.

        Args:
            name: Pulumi resource name for the A record
            resource_group_name: Resource group containing the DNS zone
            zone_name: Name of the DNS zone
            record_name: The subdomain or "@" for root domain
            ipv4_address: IPv4 address to point to
            ttl: Time to live in seconds (default: 3600 = 1 hour)

        Returns:
            The created A record resource
        """

        return dns.RecordSet(
            name,
            resource_group_name=resource_group_name,
            zone_name=zone_name,
            relative_record_set_name=record_name,
            record_type="A",
            ttl=ttl,
            a_records=[
                dns.ARecordArgs(
                    ipv4_address=ipv4_address,
                )
            ],
        )

    @classmethod
    def create_mx_record(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        zone_name: pulumi.Input[str],
        record_name: str,
        mail_exchanges: list[tuple[str, int]],
        ttl: int = 3600,
    ) -> dns.RecordSet:
        """Create an MX record in the DNS zone (for email routing).

        Args:
            name: Pulumi resource name for the MX record
            resource_group_name: Resource group containing the DNS zone
            zone_name: Name of the DNS zone
            record_name: The subdomain or "@" for root domain
            mail_exchanges: List of (mail_server, priority) tuples
                Example: [("mx1.privateemail.com", 10), ("mx2.privateemail.com", 10)]
            ttl: Time to live in seconds (default: 3600 = 1 hour)

        Returns:
            The created MX record resource
        """

        return dns.RecordSet(
            name,
            resource_group_name=resource_group_name,
            zone_name=zone_name,
            relative_record_set_name=record_name,
            record_type="MX",
            ttl=ttl,
            mx_records=[
                dns.MxRecordArgs(
                    exchange=exchange,
                    preference=priority,
                )
                for exchange, priority in mail_exchanges
            ],
        )
