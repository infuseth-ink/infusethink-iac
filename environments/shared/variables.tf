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
