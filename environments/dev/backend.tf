# Remote state in the shared Postgres instance — one schema per env.
# Connection string is supplied via the PG_CONN_STR env var (set by the
# `mise run tf` task from Secrets Manager: infusethink/terraform-state-conn-str).
# See README for bootstrap/recovery instructions.
terraform {
  backend "pg" {
    schema_name = "dev"
  }
}
