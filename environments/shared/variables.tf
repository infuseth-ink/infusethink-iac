variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-southeast-1"
}

variable "domain_name" {
  description = "Root domain name"
  type        = string
  default     = "infuseth.ink"
}

variable "db_allowed_cidrs" {
  description = "CIDR blocks allowed to reach the shared Postgres on 5432"
  type        = list(string)
}

variable "github_amplify_pat" {
  description = "GitHub classic PAT (repo + admin:repo_hook) used by Amplify to connect the repository. Stored in SSM; never committed."
  type        = string
  sensitive   = true
}
