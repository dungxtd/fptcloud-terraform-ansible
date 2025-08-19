# Instance Information
output "instance_ids" {
  description = "IDs of the created instances"
  value       = { for k, v in fptcloud_instance.vm : k => v.id }
}

output "instance_names" {
  description = "Names of the created instances"
  value       = { for k, v in fptcloud_instance.vm : k => v.name }
}

output "instance_private_ips" {
  description = "Private IP addresses of the instances"
  value       = { for k, v in fptcloud_instance.vm : k => v.private_ip }
}

output "instance_public_ips" {
  description = "Public IP addresses of the instances (if floating IPs are created)"
  value       = { for k, v in fptcloud_floating_ip.vm : k => v.ip_address }
}

output "floating_ip_ids" {
  description = "IDs of the created floating IPs"
  value       = { for k, v in fptcloud_floating_ip.vm : k => v.id }
}

# Network Information
output "vpc_id" {
  description = "ID of the VPC"
  value       = data.fptcloud_vpc.selected.id
}

output "subnet_id" {
  description = "ID of the subnet"
  value       = [for subnet in data.fptcloud_subnet.selected.subnets : subnet.id if subnet.name == var.subnet_name][0]
}

output "security_group_id" {
  description = "ID of the security group"
  value       = data.fptcloud_security_group.selected.id
}

# SSH Key Information
output "ssh_key_names" {
  description = "Names of the SSH keys"
  value       = { for k, v in fptcloud_ssh_key.keys : k => v.name }
}

# Ansible Inventory
output "ansible_inventory" {
  description = "Ansible inventory content"
  sensitive   = true
  value = templatefile("${path.module}/templates/inventory.tpl", {
    instances = [
      for k, instance in fptcloud_instance.vm : {
        key        = k
        name       = instance.name
        private_ip = instance.private_ip
        public_ip  = contains(keys(fptcloud_floating_ip.vm), k) ? fptcloud_floating_ip.vm[k].ip_address : instance.private_ip
        os_type    = var.instances[k].os_type
        has_floating_ip = contains(keys(fptcloud_floating_ip.vm), k)
      }
    ]
    ansible_user                   = var.ansible_user
    ansible_ssh_private_key_file   = var.ansible_ssh_private_key_file
    windows_password               = var.windows_password
  })
}

# Connection Information
output "connection_info" {
  description = "Connection information for the instances"
  value = {
    for k, instance in fptcloud_instance.vm : k => {
      name       = instance.name
      private_ip = instance.private_ip
      public_ip  = contains(keys(fptcloud_floating_ip.vm), k) ? fptcloud_floating_ip.vm[k].ip_address : null
      os_type    = var.instances[k].os_type
      ssh_command = var.instances[k].os_type == "linux" ? (
        contains(keys(fptcloud_floating_ip.vm), k) ?
        "ssh -i ${var.ansible_ssh_private_key_file} ${var.ansible_user != "" ? var.ansible_user : "ubuntu"}@${fptcloud_floating_ip.vm[k].ip_address}" :
        "ssh -i ${var.ansible_ssh_private_key_file} ${var.ansible_user != "" ? var.ansible_user : "ubuntu"}@${instance.private_ip != null ? instance.private_ip : "pending"}"
      ) : null
      rdp_command = var.instances[k].os_type == "windows" ? (
        contains(keys(fptcloud_floating_ip.vm), k) ?
        "mstsc /v:${fptcloud_floating_ip.vm[k].ip_address}" :
        "mstsc /v:${instance.private_ip != null ? instance.private_ip : "pending"}"
      ) : null
    }
  }
}
