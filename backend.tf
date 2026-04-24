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
