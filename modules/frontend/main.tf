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
# access_token (from SSM) connects the GitHub repo via UpdateApp on first apply.
# GitHub Actions then triggers builds via:
#   aws amplify start-job --app-id <id> --branch-name main --job-type RELEASE
#
# iam_service_role_arn is set by Amplify when GitHub is connected — ignored in
# lifecycle to prevent forced replacement on subsequent applies.
# ──────────────────────────────────────────────────────────────────────────────

resource "aws_amplify_app" "frontend" {
  name             = "infusethink-frontend-${var.environment}"
  platform         = "WEB_COMPUTE"
  compute_role_arn = aws_iam_role.amplify_compute.arn
  repository       = var.repository_url
  access_token     = var.access_token

  # pnpm build for Next.js SSR. baseDirectory must be .next for WEB_COMPUTE —
  # Amplify auto-detects Next.js and expects the .next output directory.
  # If an amplify.yml exists in the repo it overrides this; this spec is the
  # fallback used when no amplify.yml is committed.
  build_spec = <<-EOT
    version: 1
    frontend:
      phases:
        preBuild:
          commands:
            - corepack enable
            - pnpm install --frozen-lockfile
        build:
          commands:
            - pnpm run build
      artifacts:
        baseDirectory: .next
        files:
          - "**/*"
      cache:
        paths:
          - .next/cache/**/*
          - node_modules/**/*
  EOT

  # For Next.js SSR on WEB_COMPUTE, the Node.js runtime handles routing and
  # 404s — no custom_rule rewrite needed.

  # iam_service_role_arn is managed by Amplify when a GitHub repo is connected.
  # Attempting to remove it forces app replacement — ignore it here.
  # access_token is write-only (AWS never returns it); Terraform stores the
  # value in state so there is no perpetual diff unless the token is rotated.
  lifecycle {
    ignore_changes = [iam_service_role_arn, custom_rule, environment_variables]
  }

  tags = {
    Name        = "infusethink-frontend-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = var.branch_name

  # Auto-build disabled — GitHub Actions triggers releases via
  # `aws amplify start-job --job-type RELEASE` after pushing to the branch.
  enable_auto_build = false

  stage     = "BETA"
  framework = "Next.js - SSR"

  environment_variables = {
    AMPLIFY_MONOREPO_APP_ROOT = "apps/web"
  }

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

  # try() guards against an empty sub_domain set (e.g. during import before the
  # branch exists), which would otherwise crash with an invalid index error.
  subdomain_dns_parts = try(compact(split(" ", trimspace(tolist(aws_amplify_domain_association.frontend.sub_domain)[0].dns_record))), [])
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
  # Only created once the domain association has produced a DNS record.
  # length() == 0 during import/refresh before the branch exists.
  count = length(local.subdomain_dns_parts) >= 3 ? 1 : 0

  zone_id         = var.zone_id
  name            = local.subdomain_dns_parts[0]
  type            = "CNAME"
  ttl             = 300
  records         = [local.subdomain_dns_parts[2]]
  allow_overwrite = true
}

# ──────────────────────────────────────────────────────────────────────────────
# IAM — GHA deploy role Amplify permissions
# Scoped to the exact app + branch so that a compromised workflow cannot
# trigger builds on unrelated Amplify apps in the account.
# ──────────────────────────────────────────────────────────────────────────────

resource "aws_iam_role_policy" "gha_amplify" {
  name = "infusethink-gha-amplify-${var.environment}"
  role = var.gha_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AmplifyTriggerRelease"
      Effect = "Allow"
      Action = [
        "amplify:StartJob",
        "amplify:GetJob",
        "amplify:ListJobs",
        "amplify:StopJob",
      ]
      Resource = [
        "arn:aws:amplify:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:apps/${aws_amplify_app.frontend.id}/branches/${var.branch_name}",
        "arn:aws:amplify:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:apps/${aws_amplify_app.frontend.id}/branches/${var.branch_name}/jobs/*",
      ]
    }]
  })
}
