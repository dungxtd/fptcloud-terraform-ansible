# Terraform configuration for FPT Cloud VM provisioning with Ansible
terraform {
  required_version = ">= 1.0"
  required_providers {
    fptcloud = {
      source  = "fpt-corp/fptcloud"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# Configure the FPT Cloud Provider
provider "fptcloud" {
  region      = var.fpt_region
  token       = var.fpt_token
  tenant_name = var.fpt_tenant_name
  timeout     = var.fpt_timeout
}

# Data sources for existing resources
data "fptcloud_vpc" "selected" {
  name = var.vpc_name
}

data "fptcloud_subnet" "selected" {
  vpc_id = data.fptcloud_vpc.selected.id
}

data "fptcloud_security_group" "selected" {
  vpc_id = data.fptcloud_vpc.selected.id
  name   = var.security_group_name
}

# SSH Keys for Linux instances (create one per unique key)
resource "fptcloud_ssh_key" "keys" {
  for_each = {
    for k, v in var.instances : k => v
    if v.os_type == "linux" && v.ssh_key != null
  }

  name       = "${each.key}-ssh-key"
  public_key = each.value.ssh_key
}

# Create VM instances
resource "fptcloud_instance" "vm" {
  for_each = var.instances

  name              = each.value.name
  vpc_id            = data.fptcloud_vpc.selected.id
  subnet_id         = [for subnet in data.fptcloud_subnet.selected.subnets : subnet.id if subnet.name == var.subnet_name][0]
  image_name        = each.value.image_name
  flavor_name       = each.value.flavor_name
  storage_size_gb   = each.value.storage_size_gb
  storage_policy_id = each.value.storage_policy_id
  status            = "POWERED_ON"

  # Authentication - use SSH key for Linux, password for Windows
  ssh_key  = each.value.os_type == "linux" && each.value.ssh_key != null ? fptcloud_ssh_key.keys[each.key].name : null
  password = each.value.os_type == "windows" ? each.value.password : null

  # Security groups
  security_group_ids = [data.fptcloud_security_group.selected.id]
}

# Create floating IPs for instances that need them
resource "fptcloud_floating_ip" "vm" {
  for_each = {
    for k, v in var.instances : k => v
    if v.create_floating_ip
  }

  vpc_id = data.fptcloud_vpc.selected.id
}

# Associate floating IPs with instances
resource "fptcloud_floating_ip_association" "vm" {
  for_each = {
    for k, v in var.instances : k => v
    if v.create_floating_ip
  }

  vpc_id         = data.fptcloud_vpc.selected.id
  floating_ip_id = fptcloud_floating_ip.vm[each.key].id
  instance_id    = fptcloud_instance.vm[each.key].id
}
