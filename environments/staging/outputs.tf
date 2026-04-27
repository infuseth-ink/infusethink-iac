output "instance_id" {
  description = "EC2 instance ID of the backend server"
  value       = module.backend.instance_id
}

output "public_ip" {
  description = "Public IP address of the backend server"
  value       = module.backend.public_ip
}
