# Generate Ansible inventory file
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/templates/inventory.tpl", {
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
  filename = "${path.module}/../ansible/inventory/hosts"

  depends_on = [
    fptcloud_instance.vm,
    fptcloud_floating_ip_association.vm
  ]
}

# Wait for instances to be ready
resource "null_resource" "wait_for_instances" {
  for_each = var.instances

  # Wait for the instance to be accessible
  provisioner "local-exec" {
    command = each.value.os_type == "windows" ? (
      each.value.create_floating_ip ?
      "timeout 300 bash -c 'until nc -z ${fptcloud_floating_ip.vm[each.key].ip_address} 5985; do sleep 5; done'" :
      "timeout 300 bash -c 'until nc -z ${fptcloud_instance.vm[each.key].private_ip} 5985; do sleep 5; done'"
    ) : (
      each.value.create_floating_ip ?
      "timeout 300 bash -c 'until nc -z ${fptcloud_floating_ip.vm[each.key].ip_address} 22; do sleep 5; done'" :
      "timeout 300 bash -c 'until nc -z ${fptcloud_instance.vm[each.key].private_ip} 22; do sleep 5; done'"
    )
  }

  depends_on = [
    fptcloud_instance.vm,
    fptcloud_floating_ip_association.vm,
    local_file.ansible_inventory
  ]
}

# Run Ansible playbook
resource "null_resource" "run_ansible" {
  count = var.run_ansible ? 1 : 0

  provisioner "local-exec" {
    command = "cd ${path.module}/.. && ansible-playbook -i ansible/inventory/hosts ${var.ansible_playbook_path}"
    
    environment = {
      ANSIBLE_HOST_KEY_CHECKING = "False"
      ANSIBLE_TIMEOUT = "30"
    }
  }

  depends_on = [
    null_resource.wait_for_instances,
    local_file.ansible_inventory
  ]

  # Re-run if inventory changes
  triggers = {
    inventory_content = local_file.ansible_inventory.content
    playbook_path     = var.ansible_playbook_path
  }
}

# Generate connection scripts for Linux instances
resource "local_file" "connection_scripts" {
  for_each = {
    for k, v in var.instances : k => v
    if v.os_type == "linux"
  }

  content = templatefile("${path.module}/templates/connect.sh.tpl", {
    instance_name = fptcloud_instance.vm[each.key].name
    ip_address    = each.value.create_floating_ip ? fptcloud_floating_ip.vm[each.key].ip_address : (fptcloud_instance.vm[each.key].private_ip != null ? fptcloud_instance.vm[each.key].private_ip : "pending")
    ssh_key_file  = var.ansible_ssh_private_key_file
    username      = var.ansible_user != "" ? var.ansible_user : "ubuntu"
  })

  filename        = "${path.module}/../scripts/connect-${fptcloud_instance.vm[each.key].name}.sh"
  file_permission = "0755"

  depends_on = [
    fptcloud_instance.vm,
    fptcloud_floating_ip_association.vm
  ]
}

# Generate RDP connection files for Windows instances
resource "local_file" "rdp_scripts" {
  for_each = {
    for k, v in var.instances : k => v
    if v.os_type == "windows"
  }

  content = templatefile("${path.module}/templates/connect.rdp.tpl", {
    instance_name = fptcloud_instance.vm[each.key].name
    ip_address    = each.value.create_floating_ip ? fptcloud_floating_ip.vm[each.key].ip_address : (fptcloud_instance.vm[each.key].private_ip != null ? fptcloud_instance.vm[each.key].private_ip : "pending")
  })

  filename = "${path.module}/../scripts/connect-${fptcloud_instance.vm[each.key].name}.rdp"

  depends_on = [
    fptcloud_instance.vm,
    fptcloud_floating_ip_association.vm
  ]
}
