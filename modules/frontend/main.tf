# ──────────────────────────────────────────────────────────────────────────────
# IAM — Amplify SSR compute role
# Amplify WEB_COMPUTE needs a role it can assume to write CloudWatch Logs.
# ──────────────────────────────────────────────────────────────────────────────

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "aws_iam_role" "amplify_compute" {
  name = "infusethink-amplify-compute-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "amplify.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Name        = "infusethink-amplify-compute-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "amplify_compute_logs" {
  name = "infusethink-amplify-compute-${var.environment}-logs"
  role = aws_iam_role.amplify_compute.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "CloudWatchLogs"
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogGroups",
        "logs:PutLogEvents",
      ]
      Resource = [
        "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/amplify/${aws_amplify_app.frontend.id}",
        "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/amplify/${aws_amplify_app.frontend.id}:*",
      ]
    }]
  })
}

# ──────────────────────────────────────────────────────────────────────────────
# Amplify app
# No repository or access_token — GitHub Actions owns the full build+deploy
# lifecycle using the manual deploy API (create-deployment + start-deployment).
# ──────────────────────────────────────────────────────────────────────────────

resource "aws_amplify_app" "frontend" {
  name             = "infusethink-frontend-${var.environment}"
  platform         = "WEB_COMPUTE"
  compute_role_arn = aws_iam_role.amplify_compute.arn

  # For Next.js SSR on WEB_COMPUTE, the Node.js runtime handles routing and
  # 404s — no custom_rule rewrite needed.

  tags = {
    Name        = "infusethink-frontend-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = var.branch_name

  # GitHub Actions triggers deploys via the manual deploy API — no Amplify
  # auto-build hooks needed.
  enable_auto_build = false

  stage     = "BETA"
  framework = "Next.js - SSR"

  tags = {
    Name        = "infusethink-frontend-${var.environment}-${var.branch_name}"
    Environment = var.environment
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# Custom domain
# wait_for_verification = false means Terraform does not block on cert
# verification. Amplify receives the cert verification CNAME (created below)
# and completes verification automatically in the background — no second apply.
# ──────────────────────────────────────────────────────────────────────────────

resource "aws_amplify_domain_association" "frontend" {
  app_id      = aws_amplify_app.frontend.id
  domain_name = var.domain_name

  wait_for_verification = false

  certificate_settings {
    type = "AMPLIFY_MANAGED"
  }

  sub_domain {
    prefix      = var.frontend_subdomain
    branch_name = aws_amplify_branch.main.branch_name
  }
}

# The domain_association outputs two DNS records we must create in Route53:
#   certificate_verification_dns_record — format: "<name> CNAME <value>"
#   sub_domain[0].dns_record            — format: "<name> CNAME <value>"
#                                         (name may have a leading space)

locals {
  cert_dns_parts = compact(split(" ", trimspace(aws_amplify_domain_association.frontend.certificate_verification_dns_record)))
  # cert_dns_parts[0] = record name (e.g. "_abc.demo.infuseth.ink")
  # cert_dns_parts[1] = "CNAME"
  # cert_dns_parts[2] = record value

  subdomain_dns_parts = compact(split(" ", trimspace(tolist(aws_amplify_domain_association.frontend.sub_domain)[0].dns_record)))
  # subdomain_dns_parts[0] = subdomain fqdn  (e.g. "demo.infuseth.ink")
  # subdomain_dns_parts[1] = "CNAME"
  # subdomain_dns_parts[2] = CloudFront hostname
}

resource "aws_route53_record" "frontend_cert_verification" {
  zone_id         = var.zone_id
  name            = local.cert_dns_parts[0]
  type            = "CNAME"
  ttl             = 300
  records         = [local.cert_dns_parts[2]]
  allow_overwrite = true
}

resource "aws_route53_record" "frontend_subdomain" {
  zone_id         = var.zone_id
  name            = local.subdomain_dns_parts[0]
  type            = "CNAME"
  ttl             = 300
  records         = [local.subdomain_dns_parts[2]]
  allow_overwrite = true
}
