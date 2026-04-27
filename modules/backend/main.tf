data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_iam_role" "backend" {
  name = "infusethink-backend"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "ec2.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "infusethink-backend"
  }
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.backend.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "backend" {
  name = "infusethink-backend"
  role = aws_iam_role.backend.name
}

resource "aws_security_group" "backend" {
  name_prefix = "infusethink-backend-sg-"
  description = "Security group for Infusethink backend - allows HTTP(S)"

  lifecycle {
    create_before_destroy = true
  }

  # HTTP — required for Caddy ACME HTTP-01 challenge
  ingress {
    description      = "HTTP"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  # HTTPS — primary traffic
  ingress {
    description      = "HTTPS"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  # Egress — required for Caddy to reach Let's Encrypt and pull Docker images
  egress {
    description      = "Allow all outbound"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "infusethink-backend"
  }
}

resource "aws_instance" "backend" {
  ami           = data.aws_ami.al2023.id
  instance_type = var.instance_type

  iam_instance_profile   = aws_iam_instance_profile.backend.name
  vpc_security_group_ids = [aws_security_group.backend.id]

  # No key_name — access via SSM Session Manager only
  user_data = templatefile("${path.module}/user_data.sh", {
    domain       = "${var.backend_subdomain}.${var.domain_name}"
    backend_port = var.backend_port
  })

  # Replace instance when user_data changes (new deploy = new instance)
  user_data_replace_on_change = true

  tags = {
    Name = "infusethink-backend"
  }
}

# A record — points subdomain at this EC2 instance
resource "aws_route53_record" "backend_a" {
  zone_id = var.zone_id
  name    = "${var.backend_subdomain}.${var.domain_name}"
  type    = "A"
  ttl     = 300

  records = [aws_instance.backend.public_ip]
}
