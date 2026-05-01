output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = aws_route53_zone.main.zone_id
}

output "name_servers" {
  description = "Route53 name servers for the hosted zone"
  value       = aws_route53_zone.main.name_servers
}
