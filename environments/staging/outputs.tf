output "instance_id" {
  description = "EC2 instance ID of the backend server"
  value       = module.backend.instance_id
}

output "public_ip" {
  description = "Public IP address of the backend server"
  value       = module.backend.public_ip
}

output "amplify_app_id" {
  description = "Amplify app ID — set as AMPLIFY_APP_ID GitHub Actions variable in the frontend repo"
  value       = module.frontend.amplify_app_id
}

output "amplify_default_domain" {
  description = "Amplify-managed default domain (usable before custom domain is verified)"
  value       = module.frontend.amplify_default_domain
}
