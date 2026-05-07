data "aws_route53_zone" "shared" {
  name         = var.domain_name
  private_zone = false
}

data "aws_ssm_parameter" "github_amplify_pat" {
  name            = "/infusethink/github/amplify-pat"
  with_decryption = true
}

module "backend" {
  source            = "../../modules/backend"
  zone_id           = data.aws_route53_zone.shared.zone_id
  environment       = "staging"
  domain_name       = var.domain_name
  backend_subdomain = var.backend_subdomain
  instance_type     = var.instance_type
  backend_port      = var.backend_port
}

module "frontend" {
  source             = "../../modules/frontend"
  environment        = "staging"
  domain_name        = var.domain_name
  frontend_subdomain = var.frontend_subdomain
  zone_id            = data.aws_route53_zone.shared.zone_id
  branch_name        = var.branch_name
  repository_url     = var.repository_url
  access_token       = data.aws_ssm_parameter.github_amplify_pat.value
  gha_role_name      = "infusethink-gha-deploy-frontend"
}
