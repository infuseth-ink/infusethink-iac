module "shared" {
  source           = "../../modules/shared"
  domain_name      = var.domain_name
  db_allowed_cidrs = var.db_allowed_cidrs
}

# Logical databases inside the shared Postgres instance — one per environment.
# Naming: <app>_<env> so the instance can host other apps/microservices later.
resource "postgresql_database" "infusethink_staging" {
  name  = "infusethink_staging"
  owner = postgresql_role.infusethink_staging.name
}

# Dedicated least-privilege login role for the staging DB.
# Owns the DB so it can create schemas/tables but cannot touch other databases
# on the shared instance, and cannot perform superuser actions.
resource "random_password" "infusethink_staging" {
  length  = 32
  special = false
}

resource "postgresql_role" "infusethink_staging" {
  name     = "infusethink_staging"
  login    = true
  password = random_password.infusethink_staging.result
}

# ──────────────────────────────────────────────────────────────────────────────
# Terraform remote state backend (pg backend) — one DB, one schema per env.
# The connection string is published to Secrets Manager so the `mise run tf`
# task can fetch it (chicken/egg: we can't read it from `terraform output`
# because doing so would already need backend access).
# ──────────────────────────────────────────────────────────────────────────────

resource "postgresql_database" "terraform_backend" {
  name  = "terraform_backend"
  owner = postgresql_role.terraform_backend.name
}

resource "random_password" "terraform_backend" {
  length  = 32
  special = false
}

resource "postgresql_role" "terraform_backend" {
  name     = "terraform_backend"
  login    = true
  password = random_password.terraform_backend.result
}

resource "aws_secretsmanager_secret" "tfstate_conn_str" {
  name                    = "infusethink/terraform-state-conn-str"
  description             = "Postgres connection string used by the terraform pg backend"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "tfstate_conn_str" {
  secret_id = aws_secretsmanager_secret.tfstate_conn_str.id
  secret_string = format(
    "postgres://%s:%s@%s:%d/%s?sslmode=require",
    postgresql_role.terraform_backend.name,
    urlencode(random_password.terraform_backend.result),
    module.shared.db_address,
    module.shared.db_port,
    postgresql_database.terraform_backend.name,
  )
}
