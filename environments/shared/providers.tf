provider "aws" {
  region = var.aws_region
}

# Connects to the shared RDS instance to create per-env logical databases.
# Requires that `terraform apply` is run from a host that can reach the RDS
# endpoint on 5432 (the SG is open to 0.0.0.0/0, so any laptop works).
provider "postgresql" {
  host            = module.shared.db_address
  port            = module.shared.db_port
  username        = module.shared.db_master_username
  password        = module.shared.db_master_password
  superuser       = false
  sslmode         = "require"
  connect_timeout = 15
}
