output "instance_id" {
  description = "EC2 instance ID of the backend server"
  value       = aws_instance.backend.id
}

output "public_ip" {
  description = "Public IP address of the backend server"
  value       = aws_instance.backend.public_ip
}

output "zone_id" {
  description = "Route 53 hosted zone ID"
  value       = aws_route53_zone.main.zone_id
}

output "name_servers" {
  description = "Route 53 name servers for the hosted zone"
  value       = aws_route53_zone.main.name_servers
}
