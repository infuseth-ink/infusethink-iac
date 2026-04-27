output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = module.shared.zone_id
}

output "name_servers" {
  description = "Route53 name servers for the hosted zone"
  value       = module.shared.name_servers
}
