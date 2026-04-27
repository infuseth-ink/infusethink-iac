module "shared" {
  source      = "../../modules/shared"
  domain_name = var.domain_name
}

module "backend" {
  source            = "../../modules/backend"
  zone_id           = module.shared.zone_id
  domain_name       = var.domain_name
  backend_subdomain = var.backend_subdomain
  instance_type     = var.instance_type
  backend_port      = var.backend_port
}
