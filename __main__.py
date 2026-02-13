import pulumi

from infusethink.backend.ec2 import AwsEc2Backend
from infusethink.dns.route53 import AwsRoute53Zone

backend = AwsEc2Backend(
    "infusethink-backend", ssh_key_name="infusethink-backend", instance_type="t3.micro"
)
dns_zone = AwsRoute53Zone("infusethink-dns", domain_name="infuseth.ink")

pulumi.export("backend_instance_id", backend.instance_id)
pulumi.export("backend_public_ip", backend.public_ip)
pulumi.export("dns_zone_id", dns_zone.zone_id)
pulumi.export("dns_name_servers", dns_zone.name_servers)
