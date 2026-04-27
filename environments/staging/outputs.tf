output "instance_id" {
  description = "EC2 instance ID of the backend server"
  value       = module.backend.instance_id
}

output "public_ip" {
  description = "Public IP address of the backend server"
  value       = module.backend.public_ip
}

output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = module.shared.zone_id
}

output "name_servers" {
  description = "Route53 name servers for the hosted zone"
  value       = module.shared.name_servers
}
