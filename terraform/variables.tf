# FPT Cloud Provider Configuration
variable "fpt_region" {
  description = "FPT Cloud region"
  type        = string
  default     = "hanoi-vn"
}

variable "fpt_token" {
  description = "FPT Cloud API token"
  type        = string
  sensitive   = true
}

variable "fpt_tenant_name" {
  description = "FPT Cloud tenant name"
  type        = string
}

variable "fpt_timeout" {
  description = "FPT Cloud API timeout in seconds"
  type        = number
  default     = 30
}

# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "terraform-ansible-vm"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Network Configuration (using existing resources)
variable "vpc_name" {
  description = "Name of the existing VPC to use"
  type        = string
  default     = "workstation-vpc"
}

variable "subnet_name" {
  description = "Name of the existing subnet to use"
  type        = string
  default     = "workstation-subnet"
}

variable "security_group_name" {
  description = "Name of the existing security group to use"
  type        = string
  default     = "workstation-sg"
}

# Note: Security group rules are managed through FPT Cloud console
# The provider only supports reading existing security groups, not creating rules

# Instance Configuration
variable "instances" {
  description = "Map of instances to create with their configurations"
  type = map(object({
    name              = string
    image_name        = string
    flavor_name       = string
    storage_size_gb   = number
    storage_policy_id = string
    os_type           = string
    create_floating_ip = bool
    ssh_key           = optional(string)
    password          = optional(string)
    tags              = optional(map(string), {})
  }))
  default = {}
}

# Default values for instances
variable "default_storage_policy_id" {
  description = "Default storage policy ID for instances"
  type        = string
}

# SSH Key Configuration (for Linux instances)
variable "create_ssh_key" {
  description = "Whether to create a new SSH key"
  type        = bool
  default     = true
}

variable "ssh_key_name" {
  description = "Name of the SSH key to create"
  type        = string
  default     = "terraform-key"
}

variable "ssh_public_key" {
  description = "SSH public key content"
  type        = string
  default     = ""
}

variable "existing_ssh_key_name" {
  description = "Name of existing SSH key to use (when create_ssh_key is false)"
  type        = string
  default     = ""
}

# Windows Configuration
variable "windows_password" {
  description = "Password for Windows instances"
  type        = string
  sensitive   = true
  default     = ""
}

# Floating IP Configuration
variable "create_floating_ip" {
  description = "Whether to create and associate floating IPs"
  type        = bool
  default     = false
}

# Ansible Configuration
variable "ansible_user" {
  description = "Username for Ansible connection"
  type        = string
  default     = ""
}

variable "ansible_ssh_private_key_file" {
  description = "Path to SSH private key file for Ansible"
  type        = string
  default     = ""
}

variable "run_ansible" {
  description = "Whether to run Ansible playbook after VM creation"
  type        = bool
  default     = true
}

variable "ansible_playbook_path" {
  description = "Path to Ansible playbook"
  type        = string
  default     = "../ansible/setup.yml"
}

# Linux-specific Configuration
variable "linux_packages" {
  description = "List of packages to install on Linux instances"
  type        = list(string)
  default     = ["curl", "wget", "git", "htop", "vim", "unzip"]
}

variable "linux_services" {
  description = "List of services to enable on Linux instances"
  type        = list(string)
  default     = ["ssh"]
}
