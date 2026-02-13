import pulumi
import pulumi_aws as aws


class AwsEc2Backend(pulumi.ComponentResource):
    """AWS EC2 backend factory for Infusethink."""

    instance: aws.ec2.Instance
    """EC2 instance resource."""

    instance_id: pulumi.Output[str]
    """ID of the EC2 instance."""

    public_ip: pulumi.Output[str]
    """Public IP address of the EC2 instance."""

    def __init__(
        self,
        name: str,
        instance_type: str,
        opts: pulumi.ResourceOptions | None = None,
    ):
        """
        Constructor for backend server in any environment.

        Args:
            name: Pulumi resource name
            instance_type: EC2 instance type (e.g., "t3.micro")
            opts: Optional Pulumi resource options
        """
        super().__init__(
            "infusethink:backend:AwsEc2Backend",
            name,
            {
                "instance_type": instance_type,
            },
            opts,
        )

        child_opts = pulumi.ResourceOptions(parent=self)

        amazon_linux = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                aws.ec2.GetAmiFilterArgs(
                    name="name",
                    values=["al2023-ami-*-x86_64"],
                )
            ],
        )

        self.instance = aws.ec2.Instance(
            f"{name}-instance",
            instance_type=instance_type,
            ami=amazon_linux.id,
            tags={
                "Name": f"{name}-backend",
            },
            opts=child_opts,
        )

        self.instance_id = self.instance.id
        self.public_ip = self.instance.public_ip

        self.register_outputs(
            {
                "instance_id": self.instance_id,
                "public_ip": self.public_ip,
            }
        )
