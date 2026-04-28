module "shared" {
  source      = "../../modules/shared"
  domain_name = var.domain_name
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
