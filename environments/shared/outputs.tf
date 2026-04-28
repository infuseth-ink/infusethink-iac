output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = module.shared.zone_id
}

output "name_servers" {
  description = "Route53 name servers for the hosted zone"
  value       = module.shared.name_servers
}

output "db_address" {
  description = "Shared Postgres hostname"
  value       = module.shared.db_address
}

output "db_port" {
  description = "Shared Postgres port"
  value       = module.shared.db_port
}

output "db_master_username" {
  description = "Shared Postgres master username"
  value       = module.shared.db_master_username
}

output "db_master_password" {
  description = "Shared Postgres master password (managed by RDS in Secrets Manager)"
  value       = module.shared.db_master_password
  sensitive   = true
}

output "db_master_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the master credentials"
  value       = module.shared.db_master_secret_arn
}
