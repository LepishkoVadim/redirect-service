variable "region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "eu-central-1"
}

variable "aws_profile" {
  description = "Named AWS CLI profile used for credentials."
  type        = string
  default     = "redirect-service"
}

variable "project" {
  description = "Project name, used for resource names and tags."
  type        = string
  default     = "redirect-service"
}

variable "domain" {
  description = "Public domain served by the app (A-record must point at the EIP). In ALLOWED_HOSTS."
  type        = string
  default     = "redirect-service.pp.ua"
}

variable "instance_type" {
  description = "EC2 instance type. t3.small (2 GB) fits the 4-container build; t3.micro for free tier."
  type        = string
  default     = "t3.small"
}

variable "repo_url" {
  description = "Public HTTPS git URL cloned on the instance at boot."
  type        = string
  default     = "https://github.com/LepishkoVadim/redirect-service.git"
}

variable "repo_branch" {
  description = "Git branch to deploy."
  type        = string
  default     = "main"
}

variable "ssh_public_key_path" {
  description = "Path to the SSH public key registered as the EC2 key pair."
  type        = string
  default     = "~/.ssh/lepishko.pub"
}

variable "ssh_ingress_cidr" {
  description = "CIDR allowed to reach SSH (22). Restrict to your IP for real use."
  type        = string
  default     = "0.0.0.0/0"
}

variable "superuser_username" {
  description = "Django admin username bootstrapped on first boot."
  type        = string
  default     = "admin"
}

variable "superuser_password" {
  description = "Django admin password bootstrapped on first boot (set in terraform.tfvars)."
  type        = string
  default     = "admin12345"
  sensitive   = true
}

variable "superuser_email" {
  description = "Django admin email bootstrapped on first boot."
  type        = string
  default     = "admin@example.com"
}

variable "root_volume_gb" {
  description = "Root EBS volume size (GB)."
  type        = number
  default     = 20
}
