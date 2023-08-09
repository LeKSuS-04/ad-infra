locals {
  shared_metadata = {
    serial-port-enable = 1
    user-data          = file("./cloud-init.yaml")
  }
}

resource "yandex_compute_image" "ubuntu-2204-lts" {
  description   = "Ubuntu 22.04 LTS image"
  name          = "ubuntu-2204-lts"
  source_family = "ubuntu-2204-lts"
}

resource "yandex_compute_image" "nat-instance-ubuntu" {
  description   = "NAT image based on Ubuntu 18.04 LTS with predefined routing and ip forwarding rules"
  name          = "nat-instance-ubuntu-1804-lts"
  source_family = "nat-instance-ubuntu"
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
      image_id = yandex_compute_image.nat-instance-ubuntu.id
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
      image_id = yandex_compute_image.ubuntu-2204-lts.id
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
      image_id = yandex_compute_image.ubuntu-2204-lts.id
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
      image_id = yandex_compute_image.ubuntu-2204-lts.id
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

resource "yandex_compute_instance" "container-registry" {
  description = "DockerHub mirror that caches docker images"
  name        = "container-registry"
  hostname    = "container-registry"

  resources {
    cores  = var.container_registry_vm.cores
    memory = var.container_registry_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = yandex_compute_image.ubuntu-2204-lts.id
      type     = "network-ssd"
      size     = var.container_registry_vm.ssd_gb
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.admin_subnet.id
    nat       = true
  }

  metadata = local.shared_metadata
}