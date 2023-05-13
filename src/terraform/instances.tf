locals {
  ubuntu_image_id = "fd82sqrj4uk9j7vlki3q"

  shared_metadata = {
    serial-port-enable = 0
    user-data          = file("./cloud-init.yaml")
  }
}

resource "yandex_compute_instance" "bastion" {
  description = "SSH bastion that provides access to vulnbox instances. Also acts as a NAT gateway"
  name        = "bastion"
  hostname    = "bastion"

  resources {
    cores  = var.bastion_vm.cores
    memory = var.bastion_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = local.ubuntu_image_id
      type     = "network-ssd"
      size     = var.bastion_vm.ssd_gb
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.admin_subnet.id
    nat       = true
  }

  metadata = local.shared_metadata
}

resource "yandex_compute_instance" "vulnbox" {
  description = "Vulnbox for team ${count.index + 1}"
  count       = var.vulnbox_count
  name        = format("vulnbox%03d", count.index + 1)
  hostname    = format("vulnbox%03d", count.index + 1)

  resources {
    cores  = var.vulnbox_vm.cores
    memory = var.vulnbox_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = local.ubuntu_image_id
      type     = "network-ssd"
      size     = var.vulnbox_vm.ssd_gb
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.vulnbox_subnet.id
    nat       = false
  }

  metadata = local.shared_metadata
}

resource "yandex_compute_instance" "jury" {
  description = "Jury server that contains checksystem"
  name        = "jury"
  hostname    = "jury"

  resources {
    cores  = var.jury_vm.cores
    memory = var.jury_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = local.ubuntu_image_id
      type     = "network-ssd"
      size     = var.jury_vm.ssd_gb
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.admin_subnet.id
    nat       = true
  }

  metadata = local.shared_metadata
}

resource "yandex_compute_instance" "vpn" {
  description = "Host for game VPN network"
  name        = "vpn"
  hostname    = "vpn"

  resources {
    cores  = var.vpn_vm.cores
    memory = var.vpn_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = local.ubuntu_image_id
      type     = "network-ssd"
      size     = var.vpn_vm.ssd_gb
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.admin_subnet.id
    nat       = true
  }

  metadata = local.shared_metadata
}
