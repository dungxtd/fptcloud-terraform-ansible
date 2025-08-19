# Windows Ansible Configuration

Comprehensive Ansible playbooks for automated Windows system configuration, security hardening, and software deployment.

## 🚀 Overview

This Ansible project provides automated configuration management for Windows systems with focus on:
- **Security Hardening**: Windows Defender management, security policies
- **Software Installation**: Security tools and EDR solutions
- **System Configuration**: PowerShell policies, user management
- **WinRM Management**: Automated setup and cleanup scripts

## 📁 Project Structure

```
ansible/
├── setup.yml              # Main playbook
├── inventory.ini           # Static inventory configuration
├── setup-windows.sh        # Execution script
├── EnableWinRM.ps1         # WinRM setup script
├── DisableWinRM.ps1        # WinRM cleanup script
├── tasks/                  # Task modules
│   ├── security-tools.yml  # Security software installation
│   ├── install-tehtris.yml # Tehtris EDR deployment
│   ├── disable-defender.yml# Windows Defender management
│   ├── policies.yml        # Security policy configuration
│   ├── prepare.yml         # System preparation
│   ├── misc.yml           # Miscellaneous configurations
│   ├── cleanup.yml        # Post-configuration cleanup
│   └── util/              # Utility tasks
├── res/                   # Resources and files
└── inventory/             # Generated inventory (from Terraform)
    └── hosts              # Dynamic inventory file
```

## 🛠️ Prerequisites

### Required Software
- **Ansible** >= 2.9
- **Python** >= 3.8
- **pywinrm** and **requests-ntlm** Python packages

### Windows Target Requirements
- **Windows 10/11** or **Windows Server 2016+**
- **PowerShell** 5.1 or later
- **WinRM** enabled and configured
- **Administrator access** on target systems

### Installation
```bash
# Install Python dependencies
pip install pywinrm requests-ntlm

# Verify Ansible Windows support
ansible-doc -t connection winrm
```

## 🚀 Quick Start

### 1. WinRM Setup (On Windows Targets)

Run the WinRM setup script on each Windows machine:

```powershell
# Download and run EnableWinRM.ps1 on target Windows machines
# This script will:
# - Enable WinRM service
# - Configure WinRM for HTTP/HTTPS
# - Set up firewall rules
# - Create temporary password if needed (default: 1234)

.\EnableWinRM.ps1
```

### 2. Configure Inventory

Edit `inventory.ini` with your Windows hosts:

```ini
[windows_client:vars]
ansible_connection=winrm
ansible_user=admin
ansible_password="YourPassword"
ansible_winrm_server_cert_validation=ignore

# Configuration flags
hardcore_mode=False
set_powerplan=False
change_hostname=False
set_spy_block_hosts=False
disable_defender=True
install_security_tools=True
install_tehtris_edr=True
cleanup=False

[windows_client]
192.168.1.100
192.168.1.101
windows-server-1.domain.com
```

### 3. Run Playbook

Execute the main playbook:

```bash
# Using the provided script
bash ./setup-windows.sh

# Or directly with ansible-playbook
ansible-playbook -i inventory.ini setup.yml

# With verbose output for debugging
ansible-playbook -i inventory.ini setup.yml -vvv
```

### 4. Cleanup (Optional)

After configuration, optionally disable WinRM:

```powershell
# Run on Windows targets to disable WinRM
.\DisableWinRM.ps1
```
## 🔧 Configuration Options

### Inventory Variables

Configure behavior through inventory variables:

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `hardcore_mode` | Enable aggressive security settings | `False` | `True`/`False` |
| `set_powerplan` | Configure power management | `False` | `True`/`False` |
| `change_hostname` | Modify system hostname | `False` | `True`/`False` |
| `set_spy_block_hosts` | Block telemetry hosts | `False` | `True`/`False` |
| `disable_defender` | Disable Windows Defender | `True` | `True`/`False` |
| `install_security_tools` | Install security software | `True` | `True`/`False` |
| `install_tehtris_edr` | Deploy Tehtris EDR | `True` | `True`/`False` |
| `cleanup` | Run cleanup tasks | `False` | `True`/`False` |

### Connection Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ansible_connection` | Connection type | `winrm` |
| `ansible_user` | Windows username | `admin` |
| `ansible_password` | Windows password | `"SecurePassword123!"` |
| `ansible_winrm_server_cert_validation` | Certificate validation | `ignore` |
| `ansible_winrm_transport` | WinRM transport | `basic` |
| `ansible_winrm_scheme` | WinRM scheme | `http` |
| `ansible_port` | WinRM port | `5985` (HTTP) / `5986` (HTTPS) |

## 📋 Available Tasks

### Core Tasks

**Security Tools Installation** (`tasks/security-tools.yml`)
- Installs essential security software
- Configures security applications
- Sets up monitoring tools

**Tehtris EDR Deployment** (`tasks/install-tehtris.yml`)
- Deploys Tehtris Endpoint Detection and Response
- Configures EDR policies
- Establishes monitoring connections

**Windows Defender Management** (`tasks/disable-defender.yml`)
- Configures Windows Defender settings
- Manages real-time protection
- Controls security notifications

**Security Policies** (`tasks/policies.yml`)
- Applies Windows security policies
- Configures user account controls
- Sets password policies

**System Preparation** (`tasks/prepare.yml`)
- Prepares system for configuration
- Installs prerequisites
- Configures PowerShell execution policy

**Miscellaneous Configuration** (`tasks/misc.yml`)
- Various system tweaks
- Performance optimizations
- User experience improvements

**Cleanup Tasks** (`tasks/cleanup.yml`)
- Removes temporary files
- Cleans up installation artifacts
- Finalizes configuration

### Utility Tasks

Located in `tasks/util/`:
- `apply-policies.yml` - Policy application utilities
- `exec-interactive.yml` - Interactive execution helpers
- `run-interactive.yml` - Interactive command runners
- `run.yml` - General command execution
- `sudo.yml` - Privilege escalation utilities
## 🔐 Security Features

### Windows Defender Management
- Configurable real-time protection
- Exclusion management
- Threat detection settings
- Notification control

### Security Policy Enforcement
- User Account Control (UAC) configuration
- Password complexity requirements
- Account lockout policies
- Audit policy settings

### EDR Integration
- Tehtris EDR deployment and configuration
- Endpoint monitoring setup
- Threat detection and response
- Centralized security management

### Network Security
- Windows Firewall configuration
- Network access control
- Service hardening
- Port management

## 🔍 Troubleshooting

### Common Issues

**WinRM Connection Failed**
```bash
# Test WinRM connectivity
ansible windows_client -i inventory.ini -m win_ping

# Check WinRM service on Windows target
winrm get winrm/config

# Verify firewall rules
netsh advfirewall firewall show rule name="Windows Remote Management*"
```

**Authentication Errors**
```bash
# Test with verbose output
ansible-playbook -i inventory.ini setup.yml -vvv

# Check credentials in inventory
cat inventory.ini

# Test manual WinRM connection
python -c "import winrm; s=winrm.Session('http://target-ip:5985/wsman', auth=('user', 'pass')); print(s.run_cmd('whoami'))"
```

**PowerShell Execution Policy Issues**
```powershell
# On Windows target, check execution policy
Get-ExecutionPolicy -List

# Set execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

**Task Failures**
```bash
# Run specific tasks only
ansible-playbook -i inventory.ini setup.yml --tags "security-tools"

# Skip problematic tasks
ansible-playbook -i inventory.ini setup.yml --skip-tags "tehtris"

# Check task syntax
ansible-playbook -i inventory.ini setup.yml --syntax-check
```

### Debug Commands

```bash
# Test connectivity to all hosts
ansible all -i inventory.ini -m win_ping

# Check Windows facts
ansible windows_client -i inventory.ini -m setup

# Run single command
ansible windows_client -i inventory.ini -m win_shell -a "Get-Service WinRM"

# Dry run playbook
ansible-playbook -i inventory.ini setup.yml --check

# List all tasks
ansible-playbook -i inventory.ini setup.yml --list-tasks
```

## 📋 Usage Examples

### Basic Windows Configuration
```bash
# Configure all Windows clients with default settings
ansible-playbook -i inventory.ini setup.yml
```

### Security-Only Deployment
```bash
# Install only security tools
ansible-playbook -i inventory.ini setup.yml --tags "security-tools"
```

### Custom Configuration
```bash
# Override variables at runtime
ansible-playbook -i inventory.ini setup.yml -e "disable_defender=False install_tehtris_edr=False"
```

### Specific Host Targeting
```bash
# Target specific hosts
ansible-playbook -i inventory.ini setup.yml --limit "192.168.1.100"

# Target host group
ansible-playbook -i inventory.ini setup.yml --limit "windows_client"
```

## 🧹 Maintenance

### Regular Tasks
```bash
# Update security tools
ansible-playbook -i inventory.ini setup.yml --tags "security-tools"

# Apply new policies
ansible-playbook -i inventory.ini setup.yml --tags "policies"

# System cleanup
ansible-playbook -i inventory.ini setup.yml --tags "cleanup"
```

### WinRM Management
```powershell
# Enable WinRM (run on Windows targets)
.\EnableWinRM.ps1

# Disable WinRM (run on Windows targets)
.\DisableWinRM.ps1

# Check WinRM status
Get-Service WinRM
winrm get winrm/config
```

## 🔒 Security Best Practices

### Credential Management
- **Use strong passwords** for Windows accounts
- **Store credentials securely** (Ansible Vault, environment variables)
- **Rotate passwords regularly**
- **Limit WinRM access** to specific IP ranges

### Network Security
- **Use HTTPS for WinRM** in production environments
- **Configure firewall rules** to restrict WinRM access
- **Use VPN or bastion hosts** for remote management
- **Monitor WinRM connections** and authentication attempts

### System Hardening
- **Enable Windows Defender** unless using alternative EDR
- **Apply security policies** consistently across all systems
- **Keep systems updated** with latest security patches
- **Monitor security events** and audit logs

### Ansible Security
```bash
# Use Ansible Vault for sensitive data
ansible-vault create secrets.yml
ansible-vault edit secrets.yml

# Run with vault password
ansible-playbook -i inventory.ini setup.yml --ask-vault-pass

# Use environment variables for credentials
export ANSIBLE_PASSWORD="your-password"
ansible-playbook -i inventory.ini setup.yml
```

## 📚 Additional Resources

- [Ansible Windows Documentation](https://docs.ansible.com/ansible/latest/user_guide/windows.html)
- [WinRM Configuration Guide](https://docs.ansible.com/ansible/latest/user_guide/windows_setup.html)
- [Windows Security Hardening](https://docs.microsoft.com/en-us/windows/security/)
- [PowerShell Execution Policies](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)

---

**⚠️ Security Notice**: This playbook modifies system security settings. Always:
- **Test in non-production environments** first
- **Review all tasks** before execution
- **Backup systems** before making changes
- **Monitor systems** after configuration changes
