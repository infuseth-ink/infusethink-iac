output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = aws_route53_zone.main.zone_id
}

output "name_servers" {
  description = "Route53 name servers for the hosted zone"
  value       = aws_route53_zone.main.name_servers
}

output "db_address" {
  description = "Shared Postgres hostname"
  value       = aws_db_instance.shared.address
}

output "db_port" {
  description = "Shared Postgres port"
  value       = aws_db_instance.shared.port
}

output "db_master_username" {
  description = "Shared Postgres master username"
  value       = aws_db_instance.shared.username
}

output "db_master_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the master credentials"
  value       = aws_db_instance.shared.master_user_secret[0].secret_arn
}

# Internal: consumed by the postgresql provider in environments/shared to
# create logical DBs/roles. Not surfaced as a top-level env output.
output "db_master_password" {
  description = "Shared Postgres master password (managed by RDS in Secrets Manager)"
  value       = jsondecode(data.aws_secretsmanager_secret_version.db_master.secret_string)["password"]
  sensitive   = true
}
