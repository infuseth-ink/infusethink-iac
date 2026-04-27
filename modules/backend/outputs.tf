output "instance_id" {
  description = "EC2 instance ID of the backend server"
  value       = aws_instance.backend.id
}

output "public_ip" {
  description = "Public IP address of the backend server"
  value       = aws_instance.backend.public_ip
}
