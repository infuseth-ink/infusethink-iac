module "shared" {
  source      = "../../modules/shared"
  domain_name = var.domain_name
}

# Logical databases inside the shared Postgres instance — one per environment.
# Naming: <app>_<env> so the instance can host other apps/microservices later.
resource "postgresql_database" "infusethink_staging" {
  name = "infusethink_staging"
}
