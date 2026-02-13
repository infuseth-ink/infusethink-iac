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
        ssh_key_name: str | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        """
        Constructor for backend server in any environment.

        Args:
            name: Pulumi resource name
            instance_type: EC2 instance type (e.g., "t3.micro")
            ssh_key_name: Optional SSH key name for the instance
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
        security_group = self.__create_security_group(child_opts)

        self.instance = aws.ec2.Instance(
            f"{name}-instance",
            instance_type=instance_type,
            ami=amazon_linux.id,
            key_name=ssh_key_name,
            vpc_security_group_ids=[security_group.id],
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

    def __create_security_group(
        self, child_opts: pulumi.ResourceOptions
    ) -> aws.ec2.SecurityGroup:
        """
        Create a security group for the EC2 instance.

        Args:
            child_opts: Pulumi resource options for the security group
        """

        return aws.ec2.SecurityGroup(
            f"{self._name}-sg",
            description="Security group for Infusethink backend - allows HTTP(S) and SSH",
            ingress=[
                # SSH (port 22)
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=22,
                    to_port=22,
                    cidr_blocks=["0.0.0.0/0"],
                    description="SSH access",
                ),
                # HTTP (port 80)
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=80,
                    to_port=80,
                    cidr_blocks=["0.0.0.0/0"],
                    description="HTTP access",
                ),
                # HTTPS (port 443)
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=443,
                    to_port=443,
                    cidr_blocks=["0.0.0.0/0"],
                    description="HTTPS access",
                ),
            ],
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    protocol="-1",
                    from_port=0,
                    to_port=0,
                    cidr_blocks=["0.0.0.0/0"],
                    description="Allow all outbound traffic",
                ),
            ],
            opts=child_opts,
        )
