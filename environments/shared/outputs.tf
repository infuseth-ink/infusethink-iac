output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = module.dns.zone_id
}

output "name_servers" {
  description = "Route53 name servers for the hosted zone"
  value       = module.dns.name_servers
}

output "db_address" {
  description = "Shared Postgres hostname"
  value       = module.db.db_address
}

output "db_port" {
  description = "Shared Postgres port"
  value       = module.db.db_port
}

output "db_master_username" {
  description = "Shared Postgres master username"
  value       = module.db.db_master_username
}

output "db_master_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the master credentials. Fetch with `aws secretsmanager get-secret-value --secret-id <arn>`."
  value       = module.db.db_master_secret_arn
}

output "gha_deploy_role_arn" {
  description = "ARN of the GitHub Actions IAM role — use as `role-to-assume` in aws-actions/configure-aws-credentials"
  value       = aws_iam_role.gha_deploy.arn
}

output "staging_database_url_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the staging DATABASE_URL. Fetch with `aws secretsmanager get-secret-value --secret-id <arn>`."
  value       = aws_secretsmanager_secret.database_url_staging.arn
}
