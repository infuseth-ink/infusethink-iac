module "dns" {
  source      = "../../modules/dns"
  domain_name = var.domain_name
}

module "db" {
  source           = "../../modules/db"
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

resource "aws_secretsmanager_secret" "database_url_staging" {
  name                    = "infusethink/staging/database-url"
  description             = "DATABASE_URL for the staging app (least-privilege role, URL-encoded password)"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "database_url_staging" {
  secret_id = aws_secretsmanager_secret.database_url_staging.id
  secret_string = format(
    "postgres://%s:%s@%s:%d/%s?sslmode=require",
    postgresql_role.infusethink_staging.name,
    urlencode(random_password.infusethink_staging.result),
    module.db.db_address,
    module.db.db_port,
    postgresql_database.infusethink_staging.name,
  )
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
    module.db.db_address,
    module.db.db_port,
    postgresql_database.terraform_backend.name,
  )
}

# ──────────────────────────────────────────────────────────────────────────────
# GitHub Actions OIDC — allows the backend app repo to push images to ECR
# without long-lived AWS credentials.
# ──────────────────────────────────────────────────────────────────────────────

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = ["sts.amazonaws.com"]

  # Thumbprint for token.actions.githubusercontent.com (stable, rotated by GitHub)
  # Comes from: https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "gha_deploy" {
  name = "infusethink-gha-deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringLike = {
          "token.actions.githubusercontent.com:sub" = [
            "repo:infuseth-ink/infusethink-backend:ref:refs/heads/main",
            "repo:infuseth-ink/infusethink-backend:ref:refs/heads/dev",
            "repo:infuseth-ink/infusethink-backend:ref:refs/heads/staging",
          ]
        }
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
      }
    }]
  })

  tags = {
    Name = "infusethink-gha-deploy"
  }
}

resource "aws_iam_role_policy_attachment" "gha_deploy_ecr" {
  role       = aws_iam_role.gha_deploy.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_role_policy" "gha_deploy_database_url_staging" {
  name = "infusethink-gha-deploy-database-url-staging"
  role = aws_iam_role.gha_deploy.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "GetStagingDatabaseUrl"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"]
        Resource = aws_secretsmanager_secret.database_url_staging.arn
      },
    ]
  })
}

resource "aws_iam_role_policy" "gha_ssm_deploy" {
  name = "infusethink-gha-ssm-deploy"
  role = aws_iam_role.gha_deploy.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "SendCommandDocument"
        Effect   = "Allow"
        Action   = "ssm:SendCommand"
        Resource = "arn:aws:ssm:*:*:document/AWS-RunShellScript"
      },
      {
        Sid    = "SendCommandInstances"
        Effect = "Allow"
        Action = "ssm:SendCommand"
        Resource = [
          "arn:aws:ec2:*:*:instance/*",
        ]
        Condition = {
          StringLike = {
            "ec2:ResourceTag/Name" = "infusethink-backend-*"
          }
        }
      },
      {
        Sid      = "GetCommandInvocation"
        Effect   = "Allow"
        Action   = "ssm:GetCommandInvocation"
        Resource = "*"
      },
      {
        Sid      = "DescribeInstances"
        Effect   = "Allow"
        Action   = "ec2:DescribeInstances"
        Resource = "*"
      },
    ]
  })
}
