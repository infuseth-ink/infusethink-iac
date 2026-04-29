output "instance_id" {
  description = "EC2 instance ID of the backend server"
  value       = aws_instance.backend.id
}

output "public_ip" {
  description = "Public IP address of the backend server"
  value       = aws_instance.backend.public_ip
}

output "ecr_repository_url" {
  description = "ECR repository URL for the backend image"
  value       = aws_ecr_repository.backend.repository_url
}
