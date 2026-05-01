variable "db_allowed_cidrs" {
  description = "CIDR blocks allowed to reach the shared Postgres on 5432. Tighten per-IP for least exposure; widen to a /24 if your ISP rotates the last octet."
  type        = list(string)
}

variable "db_allowed_security_group_ids" {
  description = "Security group IDs allowed to reach the shared Postgres on 5432. Must be in the same VPC as the DB SG (used as source_security_group_id in ingress rules)."
  type        = list(string)
  default     = []
}
