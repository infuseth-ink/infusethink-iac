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

# ---------------------------------------------------------------------------
# State was migrated from root flat addresses → module addresses using:
#   terraform state mv aws_route53_zone.main          module.shared.aws_route53_zone.main
#   terraform state mv aws_route53_record.mx          module.shared.aws_route53_record.mx
#   terraform state mv aws_route53_record.spf         module.shared.aws_route53_record.spf
#   terraform state mv aws_route53_record.dkim        module.shared.aws_route53_record.dkim
#   terraform state mv aws_route53_record.dmarc       module.shared.aws_route53_record.dmarc
#   terraform state mv aws_iam_role.backend           module.backend.aws_iam_role.backend
#   terraform state mv aws_iam_role_policy_attachment.ssm module.backend.aws_iam_role_policy_attachment.ssm
#   terraform state mv aws_iam_instance_profile.backend   module.backend.aws_iam_instance_profile.backend
#   terraform state mv aws_security_group.backend     module.backend.aws_security_group.backend
#   terraform state mv aws_instance.backend           module.backend.aws_instance.backend
#   terraform state mv aws_route53_record.backend_a   module.backend.aws_route53_record.backend_a
# ---------------------------------------------------------------------------
