output "amplify_app_id" {
  description = "Amplify app ID — pass to `aws amplify create-deployment --app-id` in GitHub Actions"
  value       = aws_amplify_app.frontend.id
}

output "amplify_app_arn" {
  description = "Amplify app ARN"
  value       = aws_amplify_app.frontend.arn
}

output "amplify_default_domain" {
  description = "Amplify-managed default domain (e.g. <id>.amplifyapp.com)"
  value       = aws_amplify_app.frontend.default_domain
}
