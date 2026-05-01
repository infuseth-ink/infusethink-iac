provider "aws" {
  region = var.aws_region
}

# Connects to the shared RDS instance to create per-env logical databases.
# Requires that `terraform apply` is run from a host whose IP is in
# `var.db_allowed_cidrs` (see terraform.tfvars).
provider "postgresql" {
  host            = module.db.db_address
  port            = module.db.db_port
  username        = module.db.db_master_username
  password        = module.db.db_master_password
  superuser       = false
  sslmode         = "require"
  connect_timeout = 15
}
