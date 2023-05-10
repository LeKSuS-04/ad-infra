locals {
  ubuntu_image_id = "fd82sqrj4uk9j7vlki3q"
}

resource "yandex_compute_instance" "vpn_server" {
  name        = "vpn-server"
  description = "manages game VPN network"

  resources {
    cores  = var.vpn_vm.cores
    memory = var.vpn_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = local.ubuntu_image_id
      size = var.vpn_vm.ssd_gb
      type = "network-ssd"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.vulnbox_subnet.id
  }

  metadata = {
    serial-port-enable = 1
    user-data          = "#!/usr/bin/env bash\n\necho 'root:toor' | chpasswd"
  }
}
