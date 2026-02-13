import pulumi

from infusethink.backend.ec2 import AwsEc2Backend
from infusethink.dns.records import (
    create_a_record,
    create_dkim_record,
    create_dmarc_record,
    create_mx_records,
    create_spf_record,
)
from infusethink.dns.route53 import AwsRoute53Zone

DOMAIN_NAME = "infuseth.ink"

backend = AwsEc2Backend(
    "infusethink-backend", ssh_key_name="infusethink-backend", instance_type="t3.micro"
)
dns_zone = AwsRoute53Zone("infusethink-dns", domain_name="infuseth.ink")

# Preserve MX records in Namecheap's Private Email rather than Route53
mx_record = create_mx_records(
    zone_id=dns_zone.zone_id,
    domain_name=DOMAIN_NAME,
    mx_servers=[
        "10 mx1.privateemail.com",
        "20 mx2.privateemail.com",
    ],
    name="email-mx",
)
spf_record = create_spf_record(
    zone_id=dns_zone.zone_id,
    domain_name=DOMAIN_NAME,
    spf_value="v=spf1 include:spf.privateemail.com ~all",
    name="email-spf",
)
dkim_record = create_dkim_record(
    zone_id=dns_zone.zone_id,
    selector="default",
    domain_name=DOMAIN_NAME,
    dkim_value="v=DKIM1;k=rsa;p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqHfS1n3GDYIg+/WlerdvooNBs/1XeFtm1nh3cCxFFktUbXoYNkDMTLHITpT8ngk6CZ7s+qHegqPzh6O7i0jKTCMfPrK7FbZBTPXMctzY6FSWe0xGYK+LakLtvXktnZd90SAtKyBnUe62hqB9EXNpvRF2vHQlavCIuLEj2Ci8MeOHLx9jNvZH6CaTEtb/AxxMQPrwwFOZ5at4ta83RxQNKQtlAPBIfrDt1i/E+yC6yskVK1CC2UEYZINQrFuz3CFPX1Et0ES60gL/H4tLtZ8N3bnfthS3qWPCt79a+lsSCmrIwggjZjA2+oVPMmiOATZCeCZVze33T++xDnJNj3pN+wIDAQAB",
    name="email-dkim",
)
dmarc_record = create_dmarc_record(
    zone_id=dns_zone.zone_id,
    domain_name=DOMAIN_NAME,
    policy="none",
    name="email-dmarc",
)

# subdoamin for backend EC2 instance
a_record = create_a_record(
    zone_id=dns_zone.zone_id,
    record_name="backstage.infuseth.ink",
    ip_address=backend.public_ip,
    name="backend-a-record",
)

pulumi.export("backend_instance_id", backend.instance_id)
pulumi.export("backend_public_ip", backend.public_ip)
pulumi.export("dns_zone_id", dns_zone.zone_id)
pulumi.export("dns_name_servers", dns_zone.name_servers)
