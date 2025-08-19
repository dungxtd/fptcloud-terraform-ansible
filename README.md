# Windows Ansible Infrastructure

A comprehensive infrastructure-as-code solution for provisioning and configuring Windows virtual machines on FPT Cloud using Terraform and Ansible.

## 🚀 Overview

This project combines:
- **Terraform**: Infrastructure provisioning on FPT Cloud
- **Ansible**: Automated Windows configuration and security hardening
- **PowerShell Scripts**: WinRM setup and management

## 📁 Project Structure

```
windows-ansible/
├── terraform/          # Infrastructure provisioning
│   ├── main.tf         # Main Terraform configuration
│   ├── variables.tf    # Variable definitions
│   ├── outputs.tf      # Output definitions
│   ├── ansible.tf      # Ansible integration
│   └── templates/      # Template files
├── ansible/            # Configuration management
│   ├── setup.yml       # Main playbook
│   ├── inventory.ini   # Inventory configuration
│   ├── tasks/          # Task modules
│   ├── EnableWinRM.ps1 # WinRM setup script
│   └── DisableWinRM.ps1# WinRM cleanup script
└── README.md           # This file
```

## 🛠️ Prerequisites

### Required Software
- **Terraform** >= 1.0
- **Ansible** >= 2.9
- **Python** >= 3.8 (for Ansible Windows modules)
- **PowerShell** (for WinRM scripts)

### Required Credentials
- FPT Cloud account with API access
- FPT Cloud API token
- SSH key pair (for Linux instances)

### Python Dependencies
```bash
pip install pywinrm requests-ntlm
```

## 🚀 Quick Start

### 1. Infrastructure Provisioning

```bash
# Navigate to terraform directory
cd terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your FPT Cloud credentials
vim terraform.tfvars

# Initialize and deploy
terraform init
terraform plan
terraform apply
```

### 2. Windows Configuration

```bash
# Navigate to ansible directory
cd ansible

# Configure inventory with your Windows hosts
vim inventory.ini

# Enable WinRM on target Windows machines
# Run EnableWinRM.ps1 on each Windows host

# Run the playbook
bash setup-windows.sh
```

## ⚙️ Configuration

### Terraform Variables

Key variables in `terraform/terraform.tfvars`:

```hcl
# FPT Cloud Configuration
fpt_token       = "your-api-token"
fpt_tenant_name = "your-tenant"
fpt_region      = "HCM-01"

# Instance Configuration
os_type          = "windows"
instance_count   = 1
image_name       = "WINDOWS-SERVER-2019-04072024"
windows_password = "YourSecurePassword123!"

# Network Configuration
create_floating_ip = true
enable_rdp        = true
```

### Ansible Configuration

Key variables in `ansible/inventory.ini`:

```ini
[windows_client:vars]
ansible_connection=winrm
ansible_user=admin
ansible_password="YourPassword"
ansible_winrm_server_cert_validation=ignore

# Feature flags
disable_defender=True
install_security_tools=True
install_tehtris_edr=True
```

## 🔧 Features

### Infrastructure (Terraform)
- ✅ Multi-OS support (Windows/Linux)
- ✅ Image-based VM deployment
- ✅ Network management (VPC, subnets, security groups)
- ✅ Floating IP assignment
- ✅ Auto-generated connection scripts
- ✅ Ansible integration

### Configuration (Ansible)
- ✅ Windows security hardening
- ✅ Security tools installation
- ✅ EDR deployment (Tehtris)
- ✅ Windows Defender management
- ✅ PowerShell execution policy configuration
- ✅ WinRM setup automation

## 🔐 Security Features

### Network Security
- Configurable security groups
- RDP access control
- WinRM over HTTPS
- Private subnet support

### Windows Hardening
- Windows Defender configuration
- Security policy enforcement
- User account management
- Service hardening

## 📋 Usage Examples

### Deploy Single Windows Server
```bash
cd terraform
terraform apply -var="instance_count=1" -var="os_type=windows"
```

### Deploy Multiple Windows Workstations
```bash
cd terraform
terraform apply -var="instance_count=3" -var="image_name=WINDOWS-10-04072024"
```

### Configure Existing Windows Hosts
```bash
cd ansible
# Add hosts to inventory.ini
ansible-playbook setup.yml -i inventory.ini
```

## 🔍 Troubleshooting

### Common Issues

**WinRM Connection Failed**
```bash
# Check WinRM service status
winrm get winrm/config
# Verify firewall rules
netsh advfirewall firewall show rule name="Windows Remote Management (HTTPS-In)"
```

**Ansible Authentication Error**
```bash
# Test WinRM connectivity
ansible windows_client -i inventory.ini -m win_ping
```

**Terraform Provider Issues**
```bash
# Verify FPT Cloud credentials
terraform validate
# Check provider version
terraform version
```

### Debug Commands

```bash
# Terraform debugging
export TF_LOG=DEBUG
terraform apply

# Ansible verbose output
ansible-playbook setup.yml -vvv

# Test Windows connectivity
ansible windows_client -m win_ping -i inventory.ini
```

## 📚 Documentation

- [Terraform Configuration](terraform/README.md) - Detailed Terraform setup
- [Ansible Playbooks](ansible/README.md) - Windows configuration details
- [FPT Cloud Provider](https://registry.terraform.io/providers/fptcloud/fptcloud/latest/docs)

## 🧹 Cleanup

### Remove Infrastructure
```bash
cd terraform
terraform destroy
```

### Disable WinRM (Optional)
```powershell
# Run on Windows hosts
.\DisableWinRM.ps1
```

---

**⚠️ Security Notice**: This project handles sensitive credentials. Always:
- Use strong passwords
- Secure your `terraform.tfvars` file
- Rotate credentials regularly
- Follow principle of least privilege
