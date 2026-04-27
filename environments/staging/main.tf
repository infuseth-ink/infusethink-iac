data "aws_route53_zone" "shared" {
  name         = var.domain_name
  private_zone = false
}

module "backend" {
  source            = "../../modules/backend"
  zone_id           = data.aws_route53_zone.shared.zone_id
  domain_name       = var.domain_name
  backend_subdomain = var.backend_subdomain
  instance_type     = var.instance_type
  backend_port      = var.backend_port
}
