import textwrap

import pulumi
import pulumi_aws as aws


def create_mx_records(
    zone_id: pulumi.Output[str],
    domain_name: pulumi.Input[str],
    mx_servers: list[str],
    name: str = "email-mx",
) -> aws.route53.Record:
    """
    Create MX records in Route 53.

    One use case: Preserve MX records in Namecheap's Private Email rather than Route53.

    Args:
        zone_id: The ID of the Route 53 hosted zone
        domain_name: The domain name for which to create MX records
        mx_servers: List of MX server strings (e.g., ["10 mx1.privateemail.com", "20 mx2.privateemail.com"])
        name: Pulumi resource name
    Returns:
        The created Route 53 Record object
    """
    return aws.route53.Record(
        name,
        zone_id=zone_id,
        name=domain_name,
        type="MX",
        ttl=300,
        records=mx_servers,
    )


def create_a_record(
    zone_id: pulumi.Output[str],
    record_name: pulumi.Input[str],
    ip_address: pulumi.Output[str],
    name: str = "a-record",
) -> aws.route53.Record:
    """
    Create an A record in Route 53.

    Args:
        zone_id: The ID of the Route 53 hosted zone
        record_name: The name of the A record to create
        ip_address: The IP address to point the A record to
        name: Pulumi resource name
    Returns:
        The created Route 53 Record object
    """
    return aws.route53.Record(
        name,
        zone_id=zone_id,
        name=record_name,
        type="A",
        ttl=300,
        records=[ip_address],
    )


def create_spf_record(
    zone_id: pulumi.Output[str],
    domain_name: pulumi.Input[str],
    spf_value: str,
    name: str = "spf-txt",
) -> aws.route53.Record:
    """
    Create an SPF record in Route 53.

    Args:
        zone_id: The ID of the Route 53 hosted zone
        domain_name: The domain name for which to create the SPF record
        spf_value: The value of the SPF record (e.g., "v=spf1 include:_spf.google.com ~all")
        name: Pulumi resource name
    Returns:
        The created Route 53 Record object
    """
    return aws.route53.Record(
        name,
        zone_id=zone_id,
        name=domain_name,
        type="TXT",
        records=[spf_value],  # ✅ Remove quotes - just pass value
        ttl=300,
    )


def create_dkim_record(
    zone_id: pulumi.Output[str],
    selector: str,
    domain_name: pulumi.Input[str],
    dkim_value: str,
    name: str = "dkim-txt",
) -> aws.route53.Record:
    """
    Create a DKIM record in Route 53.

    Args:
        zone_id: The ID of the Route 53 hosted zone
        selector: The DKIM selector (e.g., "default")
        domain_name: The domain name for which to create the DKIM record
        dkim_value: The value of the DKIM record (e.g., "v=DKIM1; k=rsa; p=...")
        name: Pulumi resource name
    Returns:
        The created Route 53 Record object
    """
    return aws.route53.Record(
        name,
        zone_id=zone_id,
        name=f"{selector}._domainkey.{domain_name}",
        type="TXT",
        records=textwrap.wrap(dkim_value, width=255, break_long_words=True),
        ttl=300,
    )


def create_dmarc_record(
    zone_id: pulumi.Output[str],
    domain_name: pulumi.Input[str],
    policy: str = "none",
    rua_email: str | None = None,
    name: str = "dmarc-txt",
) -> aws.route53.Record:
    """
    Create DMARC TXT record for email policy.

    Args:
        zone_id: Route53 hosted zone ID
        domain_name: Base domain name (e.g., "infuseth.ink")
        policy: DMARC policy - "none", "quarantine", or "reject"
        rua_email: Optional rua email address
        name: Resource name prefix

    Returns:
        Route53 TXT record resource
    """
    dmarc_value = f"v=DMARC1; p={policy};"
    if rua_email:
        dmarc_value += f" rua=mailto:{rua_email};"

    return aws.route53.Record(
        name,
        zone_id=zone_id,
        name=f"_dmarc.{domain_name}",
        type="TXT",
        records=[dmarc_value],  # ✅ Remove quotes
        ttl=300,
    )
