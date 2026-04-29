variable "domain_name" {
  description = "Root domain name"
  type        = string
}

variable "db_allowed_cidrs" {
  description = "CIDR blocks allowed to reach the shared Postgres on 5432. Tighten per-IP for least exposure; widen to a /24 if your ISP rotates the last octet."
  type        = list(string)
}
