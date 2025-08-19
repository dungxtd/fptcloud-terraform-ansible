# Terraform FPT Cloud Infrastructure

Infrastructure-as-Code solution for provisioning and managing virtual machines on FPT Cloud with integrated Ansible automation for Windows and Linux systems.

## 🚀 Features

- **Multi-OS Support**: Deploy Windows and Linux VMs from FPT Cloud images
- **Flexible Instance Configuration**: Support for multiple VM configurations in a single deployment
- **Network Management**: Use existing VPCs, subnets, and security groups
- **Automated Configuration**: Seamless Ansible integration for post-deployment setup
- **Connection Automation**: Auto-generated SSH/RDP connection scripts
- **Floating IP Management**: Optional public IP assignment per instance
- **Template-based Configuration**: Dynamic inventory and connection script generation

## 📋 Prerequisites

### Required Software
- **Terraform** >= 1.0
- **Ansible** >= 2.9 (for automated configuration)
- **Python** >= 3.8 with `pywinrm` and `requests-ntlm` (for Windows management)

### Required Credentials
- **FPT Cloud Account** with API access
- **FPT Cloud API Token** with appropriate permissions
- **SSH Key Pair** (for Linux instances)

### FPT Cloud Resources
- Existing VPC and subnet
- Security group with appropriate rules
- Storage policy ID

## 🚀 Quick Start

### 1. Setup Configuration

```bash
# Navigate to terraform directory
cd terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your FPT Cloud credentials and requirements
vim terraform.tfvars
```

### 2. Configure Your Deployment

Edit `terraform.tfvars` with your specific values:

```hcl
# FPT Cloud Configuration
fpt_region      = "hanoi-vn"
fpt_token       = "your-fpt-cloud-api-token"
fpt_tenant_name = "YOUR-TENANT-NAME"

# Network Configuration (existing resources)
vpc_name            = "your-existing-vpc"
subnet_name         = "your-existing-subnet"
security_group_name = "your-security-group"

# Storage Configuration
default_storage_policy_id = "your-storage-policy-id"

# Instance Definitions
instances = {
  "windows-vm-1" = {
    name              = "windows-workstation-1"
    image_name        = "WINDOWS-11-24H2"
    flavor_name       = "4C4G"
    storage_size_gb   = 100
    os_type           = "windows"
    create_floating_ip = true
    password          = "YourSecurePassword123!"
  }
  "linux-vm-1" = {
    name              = "ubuntu-server-1"
    image_name        = "UBUNTU-20.04-04072024"
    flavor_name       = "2C2G"
    storage_size_gb   = 50
    os_type           = "linux"
    create_floating_ip = false
  }
}

# Ansible Configuration
windows_password      = "YourSecurePassword123!"
run_ansible          = true
ansible_playbook_path = "../ansible/setup.yml"
```

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment (review changes)
terraform plan

# Apply configuration
terraform apply
```

### 4. Access Your Instances

After deployment, connection files are automatically generated:

```bash
# SSH to Linux instances
./scripts/connect-linux-vm-1.sh

# RDP to Windows instances
open scripts/connect-windows-vm-1.rdp
```

## 📖 Configuration Examples

### Multiple Windows Workstations

```hcl
instances = {
  "win-dev-1" = {
    name              = "windows-dev-1"
    image_name        = "WINDOWS-11-24H2"
    flavor_name       = "4C8G"
    storage_size_gb   = 150
    os_type           = "windows"
    create_floating_ip = true
    password          = "DevPassword123!"
    tags = {
      Purpose = "development"
      Team    = "dev-team"
    }
  }
  "win-test-1" = {
    name              = "windows-test-1"
    image_name        = "WINDOWS-SERVER-2019-04072024"
    flavor_name       = "2C4G"
    storage_size_gb   = 100
    os_type           = "windows"
    create_floating_ip = false
    password          = "TestPassword123!"
    tags = {
      Purpose = "testing"
      Team    = "qa-team"
    }
  }
}
```

### Mixed Linux and Windows Environment

```hcl
instances = {
  "web-server" = {
    name              = "ubuntu-web-server"
    image_name        = "UBUNTU-20.04-04072024"
    flavor_name       = "2C4G"
    storage_size_gb   = 80
    os_type           = "linux"
    create_floating_ip = true
  }
  "win-client" = {
    name              = "windows-client"
    image_name        = "WINDOWS-11-24H2"
    flavor_name       = "4C4G"
    storage_size_gb   = 120
    os_type           = "windows"
    create_floating_ip = true
    password          = "ClientPassword123!"
  }
}
```

### High-Performance Windows Workstation

```hcl
instances = {
  "win-workstation" = {
    name              = "high-perf-workstation"
    image_name        = "WINDOWS-11-24H2"
    flavor_name       = "8C16G"
    storage_size_gb   = 500
    storage_policy_id = "high-performance-ssd-policy-id"
    os_type           = "windows"
    create_floating_ip = true
    password          = "WorkstationPassword123!"
    tags = {
      Purpose     = "development"
      Performance = "high"
      Owner       = "senior-dev"
    }
  }
}
```

## 🏗️ Project Structure

```
terraform/
├── main.tf                    # Main Terraform configuration
├── variables.tf               # Variable definitions
├── outputs.tf                 # Output definitions
├── ansible.tf                 # Ansible integration
├── terraform.tf               # Provider requirements
├── terraform.tfvars          # Your configuration (not in git)
├── terraform.tfvars.example   # Example configuration
├── templates/                 # Template files
│   ├── inventory.tpl          # Ansible inventory template
│   ├── connect.sh.tpl         # SSH connection script template
│   └── connect.rdp.tpl        # RDP connection file template
└── scripts/                   # Generated connection scripts
    ├── connect-vm-1.sh        # SSH scripts (generated)
    └── connect-vm-1.rdp       # RDP files (generated)
```

## 🔧 Key Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `fpt_token` | FPT Cloud API token | `"eyJ0eXAiOiJKV1Q..."` |
| `fpt_tenant_name` | FPT Cloud tenant name | `"YOUR-COMPANY-NAME"` |
| `fpt_region` | FPT Cloud region | `"hanoi-vn"` |
| `vpc_name` | Existing VPC name | `"my-vpc"` |
| `subnet_name` | Existing subnet name | `"my-subnet"` |
| `security_group_name` | Existing security group | `"default"` |

### Instance Configuration

Each instance in the `instances` map supports:

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `name` | Instance name | Yes | - |
| `image_name` | FPT Cloud image name | Yes | - |
| `flavor_name` | Instance size | Yes | - |
| `storage_size_gb` | Disk size in GB | Yes | - |
| `os_type` | OS type (`windows`/`linux`) | Yes | - |
| `create_floating_ip` | Create public IP | No | `false` |
| `password` | Windows password | Windows only | - |
| `storage_policy_id` | Custom storage policy | No | Uses default |
| `tags` | Resource tags | No | `{}` |

## 🤖 Ansible Integration

This Terraform configuration automatically integrates with Ansible for post-deployment configuration:

### Automatic Features

1. **Dynamic Inventory Generation**: Creates `../ansible/inventory/hosts` with all deployed instances
2. **Connection Script Generation**: Creates SSH/RDP connection scripts in `scripts/` directory
3. **Connectivity Verification**: Waits for instances to be accessible before running Ansible
4. **Playbook Execution**: Automatically runs specified Ansible playbooks

### Configuration

```hcl
# Ansible settings in terraform.tfvars
ansible_user                 = "Admin"  # Default user (overridden per OS)
ansible_ssh_private_key_file = "~/.ssh/your-key"
windows_password             = "YourSecurePassword123!"
run_ansible                  = true
ansible_playbook_path        = "../ansible/setup.yml"
```

### Generated Inventory Format

The generated inventory includes:
- Windows instances in `[windows_client]` group
- Linux instances in `[linux_servers]` group
- Appropriate connection variables for each OS type
- Public/private IP handling based on floating IP configuration

## 📤 Outputs

After successful deployment, Terraform provides comprehensive information:

### Instance Information
- Instance IDs, names, and status
- Private and public IP addresses
- Instance specifications (flavor, storage, etc.)

### Connection Details
- Auto-generated SSH connection scripts for Linux instances
- RDP connection files for Windows instances
- Connection commands and credentials

### Network Information
- VPC, subnet, and security group details
- Floating IP assignments
- Network configuration summary

### Ansible Integration
- Generated inventory file location
- Ansible playbook execution status
- Connection verification results

### Access Outputs

```bash
# View all outputs
terraform output

# View specific output
terraform output instance_ips

# View sensitive outputs (like inventory)
terraform output -json ansible_inventory
```

## 🔍 Troubleshooting

### Common Issues

**Authentication Errors**
```bash
# Verify FPT Cloud credentials
terraform validate
export TF_LOG=DEBUG
terraform plan
```

**Instance Creation Failures**
```bash
# Check available images
# (Use FPT Cloud console or API)

# Verify flavor availability
# (Check FPT Cloud console for available sizes)

# Check storage policy
# (Ensure storage_policy_id exists in your tenant)
```

**Network Connectivity Issues**
```bash
# Verify existing network resources
terraform plan  # Check if VPC/subnet/security group exist

# Test connectivity after deployment
ping <instance-ip>
telnet <instance-ip> 22    # For Linux SSH
telnet <instance-ip> 3389  # For Windows RDP
```

**Ansible Integration Problems**
```bash
# Check generated inventory
cat ../ansible/inventory/hosts

# Test Ansible connectivity
cd ../ansible
ansible all -i inventory/hosts -m ping

# Debug Windows connectivity
ansible windows_client -i inventory/hosts -m win_ping -vvv
```

### Debug Commands

```bash
# Terraform debugging
export TF_LOG=DEBUG
terraform apply

# Check current state
terraform show
terraform state list

# Validate configuration
terraform validate
terraform fmt -check

# Force refresh state
terraform refresh

# Check outputs
terraform output
```

## 🔐 Security Best Practices

### Credential Management
- **Never commit** `terraform.tfvars` to version control
- Use **strong passwords** for Windows instances (12+ characters, mixed case, numbers, symbols)
- **Rotate credentials** regularly
- Store sensitive values in environment variables or secure vaults

### Network Security
- **Restrict security group rules** to specific IP ranges, not 0.0.0.0/0
- Use **private subnets** for instances that don't need direct internet access
- **Limit RDP/SSH access** to trusted IP ranges only
- Consider **VPN or bastion hosts** for production environments

### Instance Security
- **Keep instances updated** via Ansible automation
- **Disable unnecessary services** and ports
- **Use SSH keys** instead of passwords for Linux instances
- **Enable logging and monitoring** for security events

### File Permissions
```bash
# Secure SSH private keys
chmod 600 ~/.ssh/your-private-key

# Secure terraform.tfvars
chmod 600 terraform.tfvars
```

## 🧹 Cleanup

### Destroy All Resources
```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy all managed resources
terraform destroy
```

### Selective Cleanup
```bash
# Remove specific instances
terraform destroy -target=fptcloud_instance.vm["instance-key"]

# Remove floating IPs only
terraform destroy -target=fptcloud_floating_ip.vm
```

## 📚 Additional Resources

- [FPT Cloud Documentation](https://fptcloud.com/docs)
- [Terraform FPT Cloud Provider](https://registry.terraform.io/providers/fpt-corp/fptcloud/latest/docs)
- [Ansible Windows Documentation](https://docs.ansible.com/ansible/latest/user_guide/windows.html)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

## 🆘 Support

For technical support:
1. **Check this documentation** and troubleshooting section
2. **Review Terraform and Ansible logs** for specific error messages
3. **Verify FPT Cloud console** for resource status and limits
4. **Test connectivity** using provided debug commands

---

**⚠️ Important**: This configuration manages real cloud resources that incur costs. Always review `terraform plan` output before applying changes and clean up unused resources promptly.
