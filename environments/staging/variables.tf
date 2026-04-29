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

variable "backend_subdomain" {
  description = "Subdomain for the backend EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for the backend"
  type        = string
  default     = "t3.micro"
}

variable "backend_port" {
  description = "Port the backend application listens on"
  type        = number
  default     = 8000
}

variable "key_name" {
  description = "EC2 key pair name for SSH access (GitHub Actions deploy). Leave empty to disable SSH."
  type        = string
  default     = ""
}
