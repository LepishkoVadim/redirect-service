output "elastic_ip" {
  description = "Public Elastic IP of the instance."
  value       = aws_eip.this.public_ip
}

output "app_url" {
  description = "Base URL of the service (via nginx :80)."
  value       = "http://${aws_eip.this.public_ip}/"
}

output "health_url" {
  value = "http://${aws_eip.this.public_ip}/health/"
}

output "docs_url" {
  value = "http://${aws_eip.this.public_ip}/api/docs/"
}

output "ssh_command" {
  description = "SSH into the instance (uses the private key matching the configured pubkey)."
  value       = "ssh ubuntu@${aws_eip.this.public_ip}"
}

output "superuser_password" {
  description = "Bootstrapped Django admin password (from var.superuser_password)."
  value       = var.superuser_password
  sensitive   = true
}
