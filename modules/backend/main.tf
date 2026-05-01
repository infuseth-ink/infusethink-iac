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
  name = "infusethink-backend-${var.environment}"

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
    Name = "infusethink-backend-${var.environment}"
  }
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.backend.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ecr_pull" {
  role       = aws_iam_role.backend.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy" "secrets" {
  name = "infusethink-backend-${var.environment}-secrets"
  role = aws_iam_role.backend.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"]
      Resource = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:infusethink/${var.environment}/*"
    }]
  })
}

resource "aws_ecr_repository" "backend" {
  name                 = "infusethink-backend-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "infusethink-backend-${var.environment}"
  }
}

resource "aws_iam_instance_profile" "backend" {
  name = "infusethink-backend-${var.environment}"
  role = aws_iam_role.backend.name
}

resource "aws_security_group" "backend" {
  name_prefix = "infusethink-backend-${var.environment}-sg-"
  description = "Security group for Infusethink backend (${var.environment}) - allows HTTP(S)"

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
    Name = "infusethink-backend-${var.environment}"
  }
}

resource "aws_instance" "backend" {
  ami           = data.aws_ami.al2023.id
  instance_type = var.instance_type

  iam_instance_profile   = aws_iam_instance_profile.backend.name
  vpc_security_group_ids = [aws_security_group.backend.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    domain       = "${var.backend_subdomain}.${var.domain_name}"
    backend_port = var.backend_port
  })

  # Replace instance when user_data changes (new deploy = new instance)
  user_data_replace_on_change = true

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name = "infusethink-backend-${var.environment}"
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
