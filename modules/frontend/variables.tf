variable "environment" {
  description = "Environment name (e.g. staging, dev, prod) — used to namespace resource names"
  type        = string
}

variable "domain_name" {
  description = "Root domain name"
  type        = string
}

variable "frontend_subdomain" {
  description = "Subdomain for the frontend Amplify app"
  type        = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID (from shared module)"
  type        = string
}

variable "branch_name" {
  description = "Git branch name that Amplify tracks for this environment"
  type        = string
  default     = "main"
}

variable "repository_url" {
  description = "GitHub repository URL for Amplify to build from (e.g. https://github.com/org/repo)"
  type        = string
}
