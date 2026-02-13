import pulumi

from infusethink.backend.ec2 import AwsEc2Backend

backend = AwsEc2Backend(
    "infusethink-backend", ssh_key_name="infusethink-backend", instance_type="t3.micro"
)

pulumi.export("backend_instance_id", backend.instance_id)
pulumi.export("backend_public_ip", backend.public_ip)
