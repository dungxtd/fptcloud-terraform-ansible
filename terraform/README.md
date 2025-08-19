# Terraform FPT Cloud VM Provisioning with Ansible

This Terraform project provisions virtual machines on FPT Cloud and automatically configures them using Ansible playbooks. It supports both Linux and Windows instances created from images, with flexible network configurations.

## Features

- **Multi-OS Support**: Deploy Linux or Windows VMs
- **Image-based Deployment**: Create VMs from FPT Cloud images
- **Network Management**: Create or use existing VPCs, subnets, and security groups
- **Automated Configuration**: Ansible integration for post-deployment setup
- **Connection Scripts**: Auto-generated SSH/RDP connection scripts
- **Floating IP Support**: Optional public IP assignment
- **Security Groups**: Configurable firewall rules

## Important Note: Snapshot Support

**The FPT Cloud Terraform provider does not currently support:**
- Creating VMs from snapshots (`snapshot_id` parameter)
- Creating snapshots via Terraform (`fptcloud_snapshot` resource)

**For snapshot management, you need to use:**
- FPT Cloud Console (web interface)
- FPT Cloud CLI (if available)
- FPT Cloud API directly

## Prerequisites

1. **FPT Cloud Account**: Valid FPT Cloud credentials and tenant access
2. **Terraform**: Version >= 1.0
3. **Ansible**: For post-deployment configuration
4. **SSH Key Pair**: For Linux instances (if creating new key)

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to terraform directory
cd terraform

# Copy example configuration
cp examples/linux-from-image.tfvars terraform.tfvars
# OR for Windows:
cp examples/windows-from-image.tfvars terraform.tfvars

# Edit configuration
vim terraform.tfvars
```

### 2. Configure Variables

Edit `terraform.tfvars` with your specific values:

```hcl
# Required FPT Cloud settings
fpt_token       = "your-fpt-cloud-token"
fpt_tenant_name = "your-tenant-name"
fpt_region      = "HCM-01"

# Storage policy (get from FPT Cloud console)
storage_policy_id = "your-storage-policy-id"

# For Linux instances
ssh_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... your-key"

# For Windows instances
windows_password = "YourSecurePassword123!"
```

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

### 4. Connect to Instances

After deployment, connection scripts are generated:

```bash
# For Linux instances
./scripts/connect-vm-1.sh

# For Windows instances (RDP files)
open scripts/connect-vm-1.rdp
```

## Configuration Examples

### Linux Web Servers from Image

```hcl
os_type               = "linux"
instance_count        = 2
image_name           = "UBUNTU-20.04-04072024"
create_floating_ip   = true

linux_packages = [
  "nginx",
  "docker.io",
  "git"
]
```

### Windows Workstation from Image

```hcl
os_type          = "windows"
instance_count   = 1
image_name       = "WINDOWS-SERVER-2019-04072024"
windows_password = "SecurePassword123!"
enable_rdp       = true
```

### Using Existing Infrastructure

```hcl
create_vpc                    = false
existing_vpc_name            = "my-existing-vpc"
create_subnet                = false
existing_subnet_name         = "my-existing-subnet"
create_security_group        = false
existing_security_group_name = "my-existing-sg"
```

## Snapshot Management Alternatives

Since Terraform doesn't support snapshots, here are alternative approaches:

### 1. Manual Snapshot Creation

**Via FPT Cloud Console:**
1. Log into FPT Cloud Console
2. Navigate to Compute > Instances
3. Select your instance
4. Click "Create Snapshot"
5. Provide name and description

**Via FPT Cloud CLI (if available):**
```bash
# Create snapshot
fptcloud compute snapshot create --instance-id <instance-id> --name "my-snapshot"

# List snapshots
fptcloud compute snapshot list

# Create VM from snapshot (manual process)
fptcloud compute instance create --snapshot-id <snapshot-id> --name "new-vm"
```

### 2. Automated Backup Strategy

Create a scheduled script for regular snapshots:

```bash
#!/bin/bash
# backup-vms.sh
INSTANCE_IDS=$(terraform output -json instance_ids | jq -r '.[]')

for instance_id in $INSTANCE_IDS; do
    snapshot_name="auto-backup-$(date +%Y%m%d-%H%M%S)"
    fptcloud compute snapshot create \
        --instance-id "$instance_id" \
        --name "$snapshot_name" \
        --description "Automated backup"
done
```

### 3. Infrastructure as Code for Snapshots

While you can't create snapshots with Terraform, you can:

1. **Document snapshot IDs** in your Terraform variables for reference
2. **Use external scripts** triggered by Terraform's `local-exec` provisioner
3. **Implement custom providers** if you have access to FPT Cloud API

## Directory Structure

```
terraform/
├── main.tf                 # Main Terraform configuration
├── variables.tf            # Variable definitions
├── outputs.tf             # Output definitions
├── ansible.tf             # Ansible integration
├── templates/             # Template files
│   ├── inventory.tpl      # Ansible inventory template
│   ├── connect.sh.tpl     # SSH connection script template
│   └── connect.rdp.tpl    # RDP connection file template
└── examples/              # Example configurations
    ├── linux-from-image.tfvars
    └── windows-from-image.tfvars
```

## Variables Reference

### Required Variables

| Variable | Description | Type |
|----------|-------------|------|
| `fpt_token` | FPT Cloud API token | string |
| `fpt_tenant_name` | FPT Cloud tenant name | string |
| `storage_policy_id` | Storage policy ID | string |

### Key Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `os_type` | OS type (linux/windows) | "linux" |
| `instance_count` | Number of instances | 1 |
| `image_name` | Image name to use | "UBUNTU-20.04-04072024" |
| `create_floating_ip` | Create public IPs | false |
| `run_ansible` | Run Ansible after deployment | true |

## Ansible Integration

The project automatically:

1. **Generates Inventory**: Creates Ansible inventory from deployed instances
2. **Waits for Connectivity**: Ensures instances are accessible
3. **Runs Playbooks**: Executes specified Ansible playbooks
4. **Creates Scripts**: Generates connection scripts

### Custom Playbooks

Place custom playbooks in the `../ansible/playbooks/` directory and reference them:

```hcl
ansible_playbook_path = "../ansible/playbooks/custom-setup.yml"
```

## Outputs

After deployment, Terraform provides:

- **Instance Information**: IDs, names, IP addresses
- **Connection Details**: SSH commands, RDP files
- **Network Information**: VPC, subnet, security group IDs
- **Ansible Inventory**: Generated inventory content

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify FPT Cloud token and tenant name
   - Check token permissions

2. **Network Connectivity**
   - Ensure security group rules allow required ports
   - Check VPC/subnet configuration

3. **Ansible Failures**
   - Verify SSH key permissions (600)
   - Check instance accessibility
   - Review Ansible inventory format

### Debug Commands

```bash
# Check Terraform state
terraform show

# Validate configuration
terraform validate

# Check Ansible connectivity
ansible all -i ../ansible/inventory/hosts -m ping

# Test SSH connection
ssh -i ~/.ssh/your-key ubuntu@instance-ip
```

## Security Considerations

1. **Restrict Access**: Limit security group rules to specific IP ranges
2. **Strong Passwords**: Use complex passwords for Windows instances
3. **Key Management**: Secure SSH private keys (permissions 600)
4. **Network Segmentation**: Use private subnets where possible
5. **Regular Updates**: Keep instances updated via Ansible

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

This will remove all created instances, networks, and associated resources.

## Support

For issues related to:
- **FPT Cloud Provider**: Check FPT Cloud documentation
- **Terraform**: Refer to Terraform documentation
- **Ansible**: See Ansible documentation

## License

This project is provided as-is for educational and development purposes.
