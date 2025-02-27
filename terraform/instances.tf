locals {

  cloud_init_config_map = {
    users : [
      {
        name : var.admin_user.username
        groups : "sudo"
        shell : "/bin/bash"
        hashed_passwd : var.admin_user.password == null ? null : bcrypt(var.admin_user.password)
        lock_passwd : var.admin_user.password == null,
        sudo : ["ALL=(ALL) NOPASSWD:ALL"]
        ssh_authorized_keys : var.admin_user.ssh_keys
      }
    ]
    ssh_pwauth : var.admin_user.password != null
  }

  cloud_init_config = format(
    "#cloud-config\n%s",
    jsonencode(local.cloud_init_config_map)
  )

  cloud_init_config_with_ddos_protection = format(
    "#cloud-config\n%s",
    jsonencode(merge(
      local.cloud_init_config_map,
      {
        runcmd : [
          "netplan set ethernets.eth0.mtu=1450",
          "netplan apply"
        ]
      }
    ))
  )
}

resource "yandex_compute_image" "ubuntu-2204-lts" {
  description   = "Ubuntu 24.04 LTS image"
  name          = "ubuntu-2404-lts"
  source_family = "ubuntu-2404-lts"
}